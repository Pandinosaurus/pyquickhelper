"""
@file
@brief Main functions to produce the documentation for a module

"""
import os,sys, shutil, datetime, re
from pandas import DataFrame

from ..loghelper.flog           import run_cmd, fLOG
from ..loghelper.pyrepo_helper  import SourceRepository
from ..pandashelper.tblformat   import df_to_rst
from .utils_sphinx_doc          import prepare_file_for_sphinx_help_generation
from .utils_sphinx_doc_helpers  import HelpGenException

template_examples = """

List of programs
++++++++++++++++
      
.. toctree::
   :maxdepth: 2

.. autosummary:: __init__.py
   :toctree: %s/
   :template: modules.rst
   
Another list
++++++++++++

"""

def get_executables_path() :
    """
    returns the paths to Python, Python Scripts
    
    @return     a list of paths
    """
    res  = [ os.path.split(sys.executable)[0] ]
    res += [ os.path.join(res[-1], "Scripts") ]
    if sys.platform == "win32" :
        ver = "c:\\Python%d%d" % (sys.version_info.major, sys.version_info.minor)
        res += [ver ]
        res += [ os.path.join(res[-1], "Scripts") ]
    return res
    
def generate_changes_repo(  chan, 
                            source, 
                            exception_if_empty = True,
                            filter_commit = lambda c : c.strip() != "documentation") :
    """
    Generates a rst tables containing the changes stored by a svn or git repository,
    the outcome is stored in a file.
    The log comment must start with ``*`` to be taken into account.
    
    @param          chan                filename to write (or None if you don't need to)
    @param          source              source folder to get changes for
    @param          exception_if_empty  raises an exception if empty
    @param          filter_commit       function which accepts a commit to show on the documentation (based on the comment)
    @return                             string (rst tables with the changes)
    """
    # builds the changes files
    try :
        src = SourceRepository(commandline=True)
        logs = src.log(path = source)
    except Exception as e :
        if exception_if_empty :
            fLOG("error, unable to retrieve log from " + source)
            raise HelpGenException("unable to retrieve log from " + source) from e
        else :
            logs = [ ("none", 0, datetime.datetime.now(), "-") ]
            fLOG("error,",e)

    if len(logs) == 0 :
        fLOG("error, unable to retrieve log from " + source)
        if exception_if_empty:
            raise HelpGenException("retrieved logs are empty from " + source)
    else :
        fLOG("info, retrieved ", len(logs), " commits")
        
    rows = [ ]
    rows.append("""\n.. _l-changes:\n\n\nChanges\n=======\n\nList of recent changes:\n""")

    values = []
    for row in logs :
        code, nbch, date, comment = row[:4]
        last = row[-1]
        if last.startswith("http") :
            nbch = "`%s <%s>`_"% (str(nbch), last)
            
        ds = "%04d-%02d-%02d" % (date.year, date.month, date.day)
        if filter_commit(comment):
            if isinstance(nbch,int) :
                values.append ( ["%04d" % nbch, "%s" % ds, comment.strip("*") ] )
            else :
                values.append ( ["%s" % nbch, "%s" % ds, comment.strip("*") ] )
            
    if len(values) == 0 and exception_if_empty:
        raise HelpGenException("Logs were not empty but there was no comment starting with '*' from " + source + "\n" + "\n".join( [ str(_) for _ in logs ] ))

    if len(values) > 0 :
        tbl = DataFrame ( columns=["change number", "date", "comment"], data=values)
        rows.append("\n\n" + df_to_rst(tbl, align=["1x","1x","3x"]) + "\n\n")

    final = "\n".join(rows)
    if chan != None :
        with open(chan, "w") as f :
            f.write(final)
    return final

def generate_help_sphinx (  project_var_name, 
                            clean = True, 
                            root = ".",
                            filter_commit = lambda c : c.strip() != "documentation",
                            extra_ext = []) :
    """
    runs the help generation
        - copies every file in another folder
        - replaces comments in doxygen format into rst format
        - replaces local import by global import (tweaking sys.path too)
        - calls sphinx to generate the documentation.
        
    @param      project_var_name    project name
    @param      clean               if True, cleans the previous documentation first
    @param      root                see below
    @param      filter_commit       function which accepts a commit to show on the documentation (based on the comment)
    @param      extra_ext           list of file extensions
    
    The result is stored in path: ``root/_doc/sphinxdoc/source``.
    
    @example(run help generation)
    @code
    # from the main folder which contains folder src
    generate_help_sphinx("pyquickhelper")
    @endcode
    @endexample
    
    By default, the function only consider files end by ``.py`` and ``.rst`` but you could
    add others files sharing the same extensions by adding this one
    in the ``extra_ext`` list.
    
    @example(other page of examples___run help generation)
    This example is exactly the same as the previous one but will be generated on another page of examples.
    @code
    # from the main folder which contains folder src
    generate_help_sphinx("pyquickhelper")
    @endcode
    @endexample
    """
    sys.path.append (os.path.abspath(os.path.join("_doc", "sphinxdoc","source")))
    root = os.path.abspath(root)
    
    src = SourceRepository(commandline=True)
    version = src.version(os.path.abspath(root))
    if version != None :
        with open("version.txt", "w") as f : f.write(str(version) + "\n")
    
    # modifies the version number in conf.py
    shutil.copy("README.rst", "_doc/sphinxdoc/source")
    shutil.copy("LICENSE.txt", "_doc/sphinxdoc/source")

    #changes
    chan = os.path.join (root, "_doc", "sphinxdoc", "source", "filechanges.rst")
    generate_changes_repo(chan, root, filter_commit = filter_commit)
    
    # copy the files 
    optional_dirs = [ ]
    
    mapped_function = [ (".*[.]%s$" % ext.strip(".") , None) for ext in extra_ext ]
            
    prepare_file_for_sphinx_help_generation ( 
                {},
                root, 
                "_doc/sphinxdoc/source/", 
                subfolders      = [ 
                                    ("src/" + project_var_name, project_var_name), 
                                     ],
                silent          = True,
                rootrep         = ("_doc.sphinxdoc.source.%s." % (project_var_name,), ""),
                optional_dirs   = optional_dirs,
                mapped_function = mapped_function )
                
    fLOG("**** end of prepare_file_for_sphinx_help_generation")
    
    # notebooks
    notebook_dir = os.path.abspath(os.path.join("_doc", "notebooks"))
    notebook_doc = os.path.abspath(os.path.join("_doc/sphinxdoc/source", "notebooks"))
    if os.path.exists(notebook_dir):
        notebooks = [ os.path.join(notebook_dir,_) for _ in os.listdir(notebook_dir) if ".ipynb" in _ ]
        if len(notebooks) >0:
            fLOG("**** notebooks")
            build = os.path.abspath("build/notebooks")
            if not os.path.exists(build): os.makedirs(build)
            if not os.path.exists(notebook_doc): os.mkdir(notebook_doc)
            nbs = process_notebooks(notebooks, 
                                    build=build, 
                                    outfold=notebook_doc)
            add_notebook_page(nbs, os.path.join(notebook_doc,"..","all_notebooks.rst"))
                
    #  run the documentation generation
    if sys.platform == "win32" :
        temp = os.environ ["PATH"]
        pyts = get_executables_path()
        script = ";".join(pyts)
        fLOG ("adding " + script)
        temp = script + ";" + temp
        os.environ["PATH"] = temp
        fLOG("changing PATH", temp)
        pa = os.getcwd ()

    thispath = os.path.normpath(root)
    docpath  = os.path.normpath(os.path.join(thispath, "_doc","sphinxdoc"))

    fLOG("checking encoding utf8...")
    for root, dirs, files in os.walk(docpath):
        for name in files:
            thn = os.path.join(root, name)
            if name.endswith(".rst") :
                try :
                    with open(thn, "r", encoding="utf8") as f : f.read()
                except Exception as e :
                    raise HelpGenException ("issue with file ", thn) from e
                
    fLOG("running sphinx... from", docpath)
    if not os.path.exists (docpath) :
        raise FileNotFoundError(docpath)
        
    if sys.platform == "win32" :
        make = os.path.join(docpath, "make.bat")
        if not os.path.exists(make) : raise FileNotFoundError(make)
            
    os.chdir (docpath)
    if clean :
        cmd = "make.bat clean".split ()
        run_cmd (cmd, wait = True)
        
    cmd = "make.bat html".split ()
    
    # This instruction should work but it does not. Sphinx seems to be stuck.
    #run_cmd (cmd, wait = True, secure="make_help.log", stop_waiting_if = lambda v : "build succeeded" in v)
    # The following one works but opens a extra windows.
    os.system("make html")
    
    # end
    os.chdir (pa)
    
def process_notebooks(  notebooks, 
                        outfold, 
                        build,
                        pandoc_path = "%USERPROFILE%\\AppData\\Local\\Pandoc",
                        formats = ["html", "python", "rst", "pdf"],
                        latex_path = r"C:\Program Files\MiKTeX 2.9\miktex\bin\x64"):
    """
    converts notebooks into html, rst, latex using 
    `nbconvert <http://ipython.org/ipython-doc/rel-1.0.0/interactive/nbconvert.html>`_.
    
    @param      notebooks   list of notebooks 
    @param      outfold     folder which will contains the outputs
    @param      build       tempoary folder which contains all produced files
    @param      pandoc_path path to pandoc
    @param      formats     list of formats to convert into (pdf format means latex then compilation)
    @param      latex_path  path to the latex compiler
    @return                 created files
    
    This function relies on `pandoc <http://johnmacfarlane.net/pandoc/index.html>`_.
    It also needs modules `pywin32 <http://sourceforge.net/projects/pywin32/>`_,
    `pygments <http://pygments.org/>`_.
    
    The latex compilation uses `MiKTeX <http://miktex.org/>`_.
    
    @warning Some latex templates (for nbconvert) uses ``[commandchars=\\\\\\{\\}]{\\|}`` which allows commands ``\\\\`` and it does not compile. 
                The one used here is ``report``.
                
    The function can use a different python Version if environement variable ``PANDOCPY`` is set up the Python path.
    `WinPython <http://winpython.sourceforge.net/>`_ works better when a notebook contains an image.
    """
    if isinstance(notebooks,str):
        notebooks = [ notebooks ]

    if "PANDOCPY" in os.environ:
        exe = os.environ["PANDOCPY"]
        exe = exe.rstrip("\\/")
        if exe.endswith("\\Scripts"):
            exe = exe[:len(exe)-len("Scripts")-1]
        if not os.path.exists(exe):
            raise FileNotFoundError(exe)
        fLOG("** using PANDOCPY", exe)
    else :
        exe = os.path.split(sys.executable)[0]
        exe2 = exe.replace("Python34","Python33")
        if os.path.exists(exe2):
            exe = exe2  # safer for the moment
        # very specific, should be removed
        exe2 = exe.replace("Python33_x64", "Python33")
        if os.path.exists(exe2):
            exe = exe2  # safer for the moment
    
    if sys.platform.startswith("win"):
        user = os.environ["USERPROFILE"]
        path = pandoc_path.replace("%USERPROFILE%", user)
        p = os.environ["PATH"]
        if path not in p :
            p += ";%WINPYDIR%\DLLs;" + path 
            os.environ["WINPYDIR"]=exe
            os.environ["PATH"] = p
            
        files = [ ]
        
        ipy = os.path.join(exe, "Scripts", "ipython3.exe")
        cmd = '{0} nbconvert --to {1} "{2}" --template {5} --output="{3}\\{4}"'
        for notebook in notebooks:
            nbout = os.path.split(notebook)[-1]
            nbout = os.path.splitext(nbout)[0]
            for format in formats :
                
                compilation = format == "pdf"
                if format == "pdf": format = "latex"
                
                templ = "full" if format != "latex" else "article"
                fLOG("convert into ", format, " NB: ", notebook)
                c = cmd.format(ipy, format, notebook, build, nbout, templ)
                fLOG(c)
                out,err = run_cmd(c,wait=True, do_not_log = False, log_error=False)
                
                if "raise ImportError" in err:
                    raise ImportError(err)
                if len(err)>0 and "error" in err.lower():
                    raise HelpGenException(err)
                    
                if format == "latex": format = "tex"
                if format == "python": format = "py"
                files.append ( os.path.join( build, nbout + "." + format) )
                
                if compilation:
                    # compilation latex
                    if os.path.exists(latex_path):
                        lat = os.path.join(latex_path, "pdflatex.exe")
                        c = '"{0}" "{1}" -output-directory="{2}"'.format(lat, files[-1], os.path.split(files[-1])[0])
                        out,err = run_cmd(c,wait=True, do_not_log = False, log_error=False)
                        if len(err) > 0 :
                            raise HelpGenException(err)
                        f = os.path.join( build, nbout + ".pdf")
                        if not os.path.exists(f):
                            raise HelpGenException(err)
                        files.append(f)
                    else:
                        fLOG("unable to find latex in", latex_path)
                        
                elif format == "html":
                    # we add a link to the notebook
                    files += add_link_to_notebook(files[-1], notebook, "pdf" in formats, False, "python" in formats)
                    
                elif format == "rst":
                    # we add a link to the notebook
                    files += add_link_to_notebook(files[-1], notebook, "pdf" in formats, "html" in formats, "python" in formats)
        
        copy = [ ]
        for f in files:
            dest = os.path.join(outfold, os.path.split(f)[-1])
            if not f.endswith(".tex"):
                try:
                    shutil.copy(f, outfold)
                    fLOG("copy ",f, " to ", outfold, "[",dest,"]")
                except shutil.SameFileError:
                    fLOG("w,file ", dest, "already exists")
                    pass
                if not os.path.exists(dest):
                    raise FileNotFoundError(dest)
            copy.append ( dest )
            
        # image
        for image in os.listdir(build):
            if image.endswith(".png") or image.endswith(".html"):
                image = os.path.join(build,image)
                dest = os.path.join(outfold, os.path.split(image)[-1])
                try:
                    shutil.copy(image, outfold)
                    fLOG("copy ",image, " to ", outfold, "[",dest,"]")
                except shutil.SameFileError:
                    fLOG("w,file ", dest, "already exists")
                    pass
                if not os.path.exists(dest):
                    raise FileNotFoundError(dest)
                copy.append ( dest )
        
        return copy
    else :
        raise NotImplementedError("not implemented on linux")

def add_link_to_notebook(file, nb, pdf, html, python):
    """
    add a link to the notebook in HTML format
    
    @param      file        notebook.html
    @param      nb          notebook (.ipynb)
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    
    The function does some cleaning too in the files.
    """
    ext = os.path.splitext(file)[-1]
    
    fold,name = os.path.split(file)
    noext = os.path.splitext(name)[0]
    res = [ os.path.join(fold, os.path.split(nb)[-1]) ]
    if not os.path.exists(res[-1]):
        shutil.copy(nb, fold)

    if ext == ".html":
        
        with open(file, "r", encoding="utf8") as f :
            text = f.read()
            
        link = '''
                <div style="position:fixed;text-align:center;align:right;width:15%;bottom:50px;right:20px;background:#DDDDDD;">
                <p>
                {0}
                </p>
                </div>
                '''
                
        links = [ '<b>links</b><br /><a href="{0}.ipynb">{0}.ipynb</a>'.format(noext) ]
        if pdf: 
            links.append( '<a href="{0}.pdf">{0}.pdf</a>'.format(noext))
        if python: 
            links.append( '<a href="{0}.py">{0}.py</a>'.format(noext))
        link = link.format( "\n<br />".join(links) )
                
        text = text.replace("</body>", link + "\n</body>")
        text = text.replace("<title>[]</title>", "<title>%s</title>" % name)
        if "<h1>" not in text : 
            text = text.replace("<body>", "<body><h1>%s</h1>" % name)

        with open(file, "w", encoding="utf8") as f :
            f.write(text)
        
        return res
        
    elif ext == ".rst":
        with open(file, "r", encoding="utf8") as f :
            lines = f.readlines()
            
        for pos in range(0,len(lines)):
            lines[pos] = lines[pos].replace(".. code:: python","::")
            if lines[pos].startswith(".. image::"):
                filename = lines[pos][len(".. image::"):].strip()
                filename = os.path.split(filename) [-1]
                lines[pos] = ".. image:: ../../_static/" + filename.replace(" ","%20")
            
        for pos,line in enumerate(lines):
            line = line.strip("\n\r")
            if len(line) > 0 and line == "=" * len(line):
                lines[pos] = lines[pos].replace("=","*")
                pos2 = pos-1
                l = len(lines[pos])
                while len(lines[pos2])!=l: pos2-=1
                sep = "" if lines[pos2].endswith("\n") else "\n"
                lines[pos2] = "{0}{2}{1}".format(lines[pos],lines[pos2], sep)
                for p in range(pos2+1,pos):
                    if lines[p] == "\n": lines[p] = ""
                break
                
        pos += 1
        if pos >= len(lines):
            raise HelpGenException("unable to find a title")
            
        # label
        label = "\n.. _{0}:\n\n".format (name.replace(" ","").replace("_","").replace(":","").replace(".",""))
        lines.insert(0,label)
            
        # links
        links = [ '**Links:**','','    * :download:`{0}.ipynb <{0}.ipynb>`'.format(noext) ]
        if html: 
            links.append('    * :download:`{0}.html <{0}.html>`'.format(noext))
        if pdf: 
            links.append('    * :download:`{0}.pdf <{0}.pdf>`'.format(noext))
        if python: 
            links.append('    * :download:`{0}.py <{0}.py>`'.format(noext))
        lines[pos] = "{0}\n\n{1}\n\n**Notebook:**\n\n".format(lines[pos],"\n".join(links))
                
        with open(file, "w", encoding="utf8") as f :
            f.write("".join(lines))
        
        return res
         
    else :
        raise HelpGenException("unable to add a link to this extension: " + ext)

def add_notebook_page(nbs, fileout):
    """
    creates a rst page with links to all notebooks
    
    @param      nbs             list of notebooks to consider
    @param      fileout         file to create
    @return                     created file name
    """
    rst = [ _ for _ in nbs if _.endswith(".rst") ]

    rows = ["", ".. _l-notebooks:","","","Notebooks","=========",""]

    exp = re.compile("[.][.] _([-a-zA-Z0-9_]+):")
    rst = sorted(rst)
    for file in rst :
        with open(file,"r",encoding="utf8") as f : cont = f.read()
        found = exp.findall(cont)
        if len(found) == 0: raise HelpGenException("unable to find a label in " + file)
        rows.append ("    * :ref:`{0}`".format(found[0]))
        
    rows.append("")
    with open(fileout, "w", encoding="utf8") as f :
        f.write("\n".join(rows))
    return file
    

