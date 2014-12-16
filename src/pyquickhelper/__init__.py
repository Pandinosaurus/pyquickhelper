# -*- coding: utf-8 -*-
"""
Main files, contains the version, the url to the documention.
"""

import sys
if sys.version_info[0] < 3 :
    raise ImportError("pyquickhelper only works with Python 3")

__version__ = "0.9"
__author__ = "Xavier Dupré"
__github__ = "https://github.com/sdpython/pyquickhelper"
__url__ = "http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html"
__downloadUrl__ = "http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper"
__license__ = "BSD License"

def check():
    """
    Checks the library is working.
    It raises an exception if it does not.

    @return         boolean
    """
    from .funcwin import check_icon
    from .loghelper import check_log
    check_icon()
    check_log()
    return True

from .loghelper.flog                    import fLOG, run_cmd, unzip, noLOG, removedirs
from .loghelper.url_helper              import get_url_content
from .funcwin.frame_params              import open_window_params
from .funcwin.frame_function            import open_window_function
from .funcwin.main_window               import main_loop_functions
from .loghelper.convert_helper          import str_to_datetime
from .sync.synchelper                   import explore_folder, synchronize_folder, has_been_updated
from .pandashelper.readh                import read_url
from .pandashelper.tblformat            import df_to_rst, df_to_html
from .pandashelper.tblfunction          import isempty, isnan
from .helpgen                           import get_help_usage
from .helpgen.sphinx_main               import generate_help_sphinx, process_notebooks
from .ipythonhelper.kindofcompletion    import AutoCompletion, AutoCompletionFile
from .sync.visual_sync                  import create_visual_diff_through_html, create_visual_diff_through_html_files
from .serverdoc.documentation_server    import run_doc_server
from .pycode.code_helper                import remove_extra_spaces, remove_extra_spaces_folder
from .ipythonhelper.html_forms          import open_html_form
from .ipythonhelper.magic_parser        import MagicCommandParser
from .helpgen.utils_sphinx_config       import NbImage
from .unittests.utils_tests             import main_wrapper_tests