"""
@file
@brief Modified version of `runipy.notebook_runner <https://github.com/paulgb/runipy/blob/master/runipy/notebook_runner.py>`_.
"""

from queue import Empty
import os
import re
from time import sleep

from IPython.nbformat.current import NotebookNode
from IPython.kernel import KernelManager

from ..loghelper.flog import noLOG


class NotebookError(Exception):

    """
    custom exception
    """
    pass


class NotebookRunner(object):

    """
    The kernel communicates with mime-types while the notebook
    uses short labels for different cell types. We'll use this to
    map from kernel types to notebook format types.

    This classes executes a notebook end to end.
    """

    MIME_MAP = {
        'image/jpeg': 'jpeg',
        'image/png': 'png',
        'text/plain': 'text',
        'text/html': 'html',
        'text/latex': 'latex',
        'application/javascript': 'html',
        'image/svg+xml': 'svg',
    }

    def __init__(self, nb, profile_dir=None, working_dir=None,
                 fLOG=noLOG):
        """
        constuctor

        @param      nb              notebook as JSON
        @param      profile_dir     profile directory
        @param      working_dir     working directory
        @param      fLOG            logging function
        """
        self.km = KernelManager()
        self.fLOG = fLOG
        args = []

        if profile_dir:
            args.append('--profile-dir=%s' % os.path.abspath(profile_dir))

        cwd = os.getcwd()

        if working_dir:
            os.chdir(working_dir)

        self.km.start_kernel(extra_arguments=args)

        os.chdir(cwd)

        self.kc = self.km.client()
        self.kc.start_channels()
        # self.kc.wait_for_ready()
        self.nb = nb

    def shutdown_kernel(self):
        """
        shut down kernel
        """
        self.fLOG('-- shutdown kernel')
        self.kc.stop_channels()
        self.km.shutdown_kernel(now=True)

    def clean_code(self, code):
        """
        clean the code before running it, the function comment out
        instruction such as ``show()``

        @param      code        code (string)
        @return                 cleaned code
        """
        has_bokeh = "bokeh." in code or "from bokeh" in code or "import bokeh" in code
        if code is None:
            return code
        else:
            lines = [_.strip("\n\r").rstrip(" \t") for _ in code.split("\n")]
            res = []
            show_is_last = False
            for line in lines:
                if line.replace(" ", "") == "show()":
                    line = line.replace("show", "#show")
                    show_is_last = True
                elif has_bokeh and line.replace(" ", "") == "output_notebook()":
                    line = line.replace("output_notebook", "#output_notebook")
                else:
                    show_is_last = False
                res.append(line)
                if show_is_last:
                    res.append('"nothing to show"')
            return "\n".join(res)

    def run_cell(self, index_cell, cell, clean_function=None):
        '''
        Run a notebook cell and update the output of that cell in-place.

        @param      index_cell          index of the cell
        @param      cell                cell to execute
        @param      clean_function      cleaning function to apply to the code before running it
        @return                         output of the cell
        '''
        if isinstance(cell, str):
            iscell = False
            codei = cell
        else:
            iscell = True
            codei = cell.input

        self.fLOG('-- running cell:\n%s\n' % codei)

        code = self.clean_code(codei)
        if clean_function is not None:
            code = clean_function(code)
        if len(code) == 0:
            return ""
        self.kc.execute(code)

        reply = self.kc.get_shell_msg()
        try:
            status = reply['content']['status']
        except KeyError:
            status = 'error'

        if status == 'error':
            ansi_escape = re.compile(r'\x1b[^m]*m')
            try:
                tr = [ansi_escape.sub('', _)
                      for _ in reply['content']['traceback']]
            except KeyError:
                tr = ["No traceback, avaible keys in reply['content']"] + \
                    [_ for _ in reply['content']]
            traceback_text = '\n'.join(tr)
            self.fLOG("ERR:\n", traceback_text)
        else:
            traceback_text = ''
            self.fLOG('-- cell returned')

        outs = list()
        nbissue = 0
        while True:
            try:
                msg = self.kc.get_iopub_msg(timeout=1)
                if msg['msg_type'] == 'status':
                    if msg['content']['execution_state'] == 'idle':
                        break
            except Empty as e:
                # execution state should return to idle before the queue becomes empty,
                # if it doesn't, something bad has happened
                status = "error"
                nbissue += 1
                if nbissue > 10:
                    # the notebook is empty
                    return ""
                else:
                    continue

            content = msg['content']
            msg_type = msg['msg_type']

            # IPython 3.0.0-dev writes pyerr/pyout in the notebook format but uses
            # error/execute_result in the message spec. This does the translation
            # needed for tests to pass with IPython 3.0.0-dev
            notebook3_format_conversions = {
                'error': 'pyerr',
                'execute_result': 'pyout'
            }
            msg_type = notebook3_format_conversions.get(msg_type, msg_type)

            out = NotebookNode(output_type=msg_type)

            if 'execution_count' in content:
                if iscell:
                    cell['prompt_number'] = content['execution_count']
                out.prompt_number = content['execution_count']

            if msg_type in ('status', 'pyin', 'execute_input'):
                continue

            elif msg_type == 'stream':
                out.stream = content['name']
                # in msgspec 5, this is name, text
                # in msgspec 4, this is name, data
                if 'text' in content:
                    out.text = content['text']
                else:
                    out.text = content['data']

            elif msg_type in ('display_data', 'pyout'):
                for mime, data in content['data'].items():
                    try:
                        attr = self.MIME_MAP[mime]
                    except KeyError:
                        raise NotImplementedError(
                            'unhandled mime type: %s' % mime)
                    setattr(out, attr, data)

            elif msg_type == 'pyerr':
                out.ename = content['ename']
                out.evalue = content['evalue']
                out.traceback = content['traceback']

            elif msg_type == 'clear_output':
                outs = list()
                continue

            else:
                raise NotImplementedError(
                    'unhandled iopub message: %s' % msg_type)
            outs.append(out)

        if iscell:
            cell['outputs'] = outs

        raw = []
        for _ in outs:
            try:
                t = _.text
                raw.append(t)
            except AttributeError:
                continue

        sraw = "\n".join(raw)
        self.fLOG(sraw)

        def reply2string(reply):
            sreply = []
            for k, v in sorted(reply.items()):
                if isinstance(v, dict):
                    temp = []
                    for _, __ in sorted(v.items()):
                        temp.append("    [{0}]={1}".format(_, str(__)))
                    v = "\n".join(temp)
                    sreply.append("reply['{0}']=dict\n{1}".format(k, v))
                else:
                    sreply.append("reply['{0}']={1}".format(k, str(v)))
            sreply = "\n".join(sreply)
            return sreply

        if status == 'error':
            sreply = reply2string(reply)
            if len(code) < 5:
                scode = [code]
            else:
                scode = ""
            raise NotebookError("CELL {4} length={5} -- {6}:\n{0}\nTRACE:\n{1}\nRAW:\n{2}REPLY:\n{3}".format(
                code, traceback_text, sraw, sreply, index_cell, len(code), scode))
        return outs

    def iter_code_cells(self):
        '''
        Iterate over the notebook cells containing code.
        '''
        for ws in self.nb.worksheets:
            for cell in ws.cells:
                if cell.cell_type == 'code':
                    yield cell

    def run_notebook(self,
                     skip_exceptions=False,
                     progress_callback=None,
                     additional_path=None,
                     valid=None,
                     clean_function=None):
        '''
        Run all the cells of a notebook in order and update
        the outputs in-place.

        If ``skip_exceptions`` is set, then if exceptions occur in a cell, the
        subsequent cells are run (by default, the notebook execution stops).

        @param      skip_exceptions     skip exception
        @param      progress_callback   call back function
        @param      additional_path     additional paths (as a list or None if none)
        @param      valid               if not None, valid is a function which returns wether or not the cell should be executed or not
        @param      clean_function      function which cleans a cell's code before executing it (None for None)
        '''
        if additional_path is not None:
            if not isinstance(additional_path, list):
                raise TypeError(
                    "additional_path should be a list not: " + str(additional_path))
            code = ["import sys"]
            for p in additional_path:
                code.append("sys.path.append(r'{0}')".format(p))
            cell = "\n".join(code)
            self.run_cell(-1, cell)

        for i, cell in enumerate(self.iter_code_cells()):
            if valid is not None and not valid(cell.input):
                continue
            try:
                self.run_cell(i, cell, clean_function=clean_function)
            except Empty as er:
                raise Exception(
                    "issue when executing:\n{0}".format(cell.input)) from er
            except NotebookError as e:
                if not skip_exceptions:
                    raise
                else:
                    raise Exception(
                        "issue when executing:\n{0}".format(cell.input)) from e
            if progress_callback:
                progress_callback(i)

    def count_code_cells(self):
        '''
        @return the number of code cells in the notebook
        '''
        return sum(1 for _ in self.iter_code_cells())
