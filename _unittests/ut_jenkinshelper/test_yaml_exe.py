"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import re
import warnings


try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from src.pyquickhelper.loghelper import fLOG, run_cmd
from src.pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from src.pyquickhelper.jenkinshelper.yaml_helper import load_yaml, enumerate_convert_yaml_into_instructions, evaluate_condition, convert_sequence_into_batch_file

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestYamlExe(unittest.TestCase):

    def test_bug_exe(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        command = "dir" if sys.platform.startswith("win32") else "ls"
        yml = """
        language: python
        python:
            - {{Python35}}
        before:
            - %s
        after_script:
            - %s {{PLATFORM}}
        script:
            - %s
        """ % (command, command, command)
        context = dict(Python34="fake", Python35=os.path.dirname(sys.executable),
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython35=None, project_name="pyquickhelper",
                       root_path="ROOT", PLATFORM="win")
        obj = load_yaml(yml, context=context)
        try:
            res = list(enumerate_convert_yaml_into_instructions(
                obj, variables=context))
            assert False
        except ValueError as e:
            assert "'before'" in str(e)

    def test_exe(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_exe")
        this = os.path.abspath(os.path.dirname(__file__))
        command = "dir" if sys.platform.startswith("win32") else "ls"
        yml = """
        language: python
        python:
            - {{Python35}}
        before_script:
            - %s
        after_script:
            - %s {{PLATFORM}}
        script:
            - %s
        """ % (command, command, command)
        context = dict(Python34="fake", Python35=os.path.dirname(sys.executable),
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython35=None, project_name="pyquickhelper",
                       root_path="ROOT", PLATFORM="win")
        obj = load_yaml(yml, context=context)
        res = list(enumerate_convert_yaml_into_instructions(
            obj, variables=context))
        for r, var in res:
            conv = convert_sequence_into_batch_file(r, variables=var)
            assert ("%s " % command) in conv
            fLOG("####", conv)
            ext = "bat" if command == "dir" else "sh"
            name = os.path.join(temp, "yml.%s" % ext)
            with open(name, "w") as f:
                f.write(conv)
            if is_travis_or_appveyor() == "travis":
                warnings.warn("Test disabled on travis")
            else:
                out, err = run_cmd(name, wait=True)
                fLOG("###")
                fLOG(out)
                if "BEFORE_SCRIPT" not in out:
                    raise Exception(
                        "{0}\nERR\n{2}\n#########\n{1}".format(out, conv, err))
                if "AFTER_SCRIPT" not in out:
                    raise Exception(
                        "{0}\nERR\n{2}\n#########\n{1}".format(out, conv, err))
                if "SCRIPT" not in out:
                    raise Exception(
                        "{0}\nERR\n{2}\n#########\n{1}".format(out, conv, err))


if __name__ == "__main__":
    unittest.main()