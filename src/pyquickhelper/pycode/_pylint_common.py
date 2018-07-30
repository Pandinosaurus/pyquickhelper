"""
@file
@brief Check code style.

.. versionadded:: 1.8
"""
import os
from .utils_tests_helper import check_pep8


def _run_cmd_filter(name):
    if "yaml_helper_yaml.py" in name:
        return True
    if "test_yaml.py" in name:
        return True
    return False


def _private_test_style_src(fLOG, run_lint, verbose=False, pattern=".*[.]py$"):
    thi = os.path.abspath(os.path.dirname(__file__))
    src_ = os.path.normpath(os.path.join(thi, "..", ".."))
    check_pep8(src_, fLOG=fLOG, run_lint=run_lint, verbose=verbose, pattern=pattern,
               run_cmd_filter=_run_cmd_filter,
               pylint_ignore=('C0103', 'C1801', 'R0201', 'R1705', 'W0108', 'W0613',
                              'W0201', 'W0212', 'W0603', 'W0622',
                              'W0511', 'C0412', 'R1702', 'E0702',
                              'W0640', 'C0111', 'R0914', 'C0302',
                              'W0703', 'C0325', 'R1703', 'R0915',
                              'R0912', 'W0123', 'R0913', 'R0912',
                              'R0911', 'R0916', 'C0200', 'W0223',
                              'W0122', 'E1003', 'R0205', 'E0001',
                              'W0143'),
               skip=["ftp_transfer_files.py:374: [E731]",
                     "_nbconvert_config.py:",
                     "convert_doc_sphinx_helper.py:31: [E402]",
                     "magic_class.py:12: [E402]",
                     "windows_scripts.py:724",
                     "Redefining built-in 'open'",
                     "Redefining built-in 'StringIO'",
                     "Redefining built-in 'FileNotFoundError'",
                     "Redefining built-in 'format'",
                     "benchmark.py:241",
                     "encryption_cli.py:13",
                     "encryption_cli.py:56",
                     "Redefining built-in 'ConnectionResetError'",
                     "Unable to import 'urllib2'",
                     "Unable to import 'httplib'",
                     "Unable to import 'urlparse'",
                     "Unable to import 'StringIO'",
                     #
                     "bokeh_plot.py",
                     "sphinx_rst_builder.py",
                     "Unused variable 'bokeh'",
                     "Unused variable 'plt'",
                     "Unused variable 'toctitle'",
                     "sphinx_template_extension.py:121: W0123: Use of eval",
                     "sphinx_runpython_extension.py:99",
                     "sphinx_runpython_extension.py:106",
                     "sphinx_runpython_extension.py:107",
                     "sphinx_runpython_extension.py:154",
                     "sphinx_runpython_extension.py:190",
                     "sphinx_runpython_extension.py:189",
                     "sphinx_runpython_extension.py:519",
                     "download_helper.py:95",
                     "download_helper.py:105",
                     "file_tree_node.py:384",
                     "ftp_transfer.py",
                     "ftp_transfer_mock.py:19",
                     "Redefining name 'fLOG' from outer scope",
                     "default_conf.py",
                     "Instance of '_MemoryBuilder' has no ",
                     "sphinx_runpython_extension.py:159",
                     "sphinx_postcontents_extension.py174",
                     "Use % formatting in logging functions",
                     "Class 'BlogPostListDirective' has no 'blogpostlist' member",
                     "sphinx_autosignature.py:78",
                     "import_object_helper.py:50",
                     "Instance of 'BlogPost' has no '",
                     'blog_post.py:121',
                     "server_helper.py:31",
                     "Module 'sys' has no 'real_prefix'",
                     "Unable to import 'src.pyquickhelper.pycode.get_pip'",
                     "utils_tests_private.py:321",
                     "unittestclass.py",
                     "clean_helper.py:11",
                     "Redefining name 'rss_update_run_server' from outer scope",
                     "Unable to import 'pysvn'",
                     "pygit_helper.py:782",
                     "internet_helper.py:107",
                     "synchelper.py:428",
                     "synchelper.py:429",
                     "winzipfile.py:73",
                     "process_notebooks.py:817",
                     "Instance of '_AdditionalVisitDepart' has no '",
                     "Instance of '_WriterWithCustomDirectives' has no ",
                     "_nbconvert_preprocessor.py:14",
                     "js_helper.py:186",
                     "No name 'brown' in module 'sphinx.util.console'",
                     "Redefining argument with the local name 'dir'",
                     "pysvn_helper.py:53",
                     "pygit_helper.py:74",
                     "pypi_helper.py:8",
                     "No name 'svg2png' in module 'cairosvg'",
                     "process_notebooks.py:1099",
                     "sphinxm_convert_doc_helper.py:325: W0612",
                     "sphinxm_convert_doc_helper.py:395: R1710",
                     "sphinxm_convert_doc_helper.py:398: R1710",
                     "No name 'bold' in module 'sphinx.util.console'",
                     "No name 'darkgreen' in module 'sphinx.util.console'",
                     "Redefining name 'HTMLTranslator' from outer scope",
                     "Redefining name 'LaTeXTranslator' from outer scope",
                     "Unused variable 'sphinx.builders.latex.transforms'",
                     "Class 'Theme' has no 'themes' member",
                     "sphinxm_mock_app.py:110: R1706",
                     "sphinxm_mock_app.py:334: E1101",
                     "Instance of 'MockSphinxApp' has no '_added_objects' member",
                     "sphinxm_mock_app.py:384: E0211",
                     "sphinx_main.py:431: E1111",
                     "sphinx_main.py:731: R1704",
                     "sphinx_main.py:429: E1111",
                     "sphinx_main.py:729: R1704",
                     "utils_sphinx_doc.py:1071: R1704",
                     "utils_sphinx_doc.py:1771: C0112",
                     "utils_sphinx_doc_helpers.py:779: W0102",
                     "utils_sphinx_doc_helpers.py:912: W0631",
                     "sphinx_postcontents_extension.py:159: W0612",
                     "sphinx_postcontents_extension.py:174: W1302",
                     "sphinx_bigger_extension.py:78: W1505",
                     "import_object_helper.py:20: W0211",
                     "gitlab_helper.py:88",
                     "history_helper.py:256: R1710",
                     "jenkins_server.py:193: W0221",
                     "jenkins_server.py:170: E1101",
                     "jenkins_helper.py:58: W0102",
                     "magic_parser.py:166: C0123",
                     "magic_parser.py:168: C0123",
                     "js_helper.py:55: W0102",
                     "js_helper.py:43: W0621",
                     "sphinxm_convert_doc_sphinx_helper.py:457: W0612",
                     "sphinxm_convert_doc_sphinx_helper.py:607: W0231",
                     "sphinxm_convert_doc_sphinx_helper.py:637: W0231",
                     "sphinxm_convert_doc_sphinx_helper.py:848: W0231",
                     "sphinxm_convert_doc_sphinx_helper.py:876: W0231",
                     "sphinxm_convert_doc_sphinx_helper.py:943: W0231",
                     "sphinxm_convert_doc_sphinx_helper.py:1329",
                     "sphinxm_convert_doc_sphinx_helper.py:1351: W0221",
                     "sphinxm_convert_doc_sphinx_helper.py:1425: [E901]",
                     "Unused import sphinx.builders.latex.transforms",
                     "utils_sphinx_doc.py:126: W0621",
                     "utils_sphinx_doc.py:279: W0621",
                     "utils_sphinx_doc.py:685: W0102",
                     "utils_sphinx_doc.py:908: W0621",
                     "_my_doxypy.py:373: W0612",
                     "_my_doxypy.py:571: W0621",
                     "__init__.py:1: R0401",
                     "texts_language.py:1: R0401",
                     "blog_helper.py:35: E0401",
                     "run_cmd.py:15: E0401",
                     "jenkins_server.py:188: E1101",
                     "jenkins_server.py:160: W0221",
                     "utils_sphinx_config.py:51: E1101",
                     "winzipfile.py:77: E1101",
                     "winzipfile.py:76: E1121",
                     "winzipfile.py:65: E1101",
                     "winzipfile.py:63: E1101",
                     "winzipfile.py:26: W0221",
                     "pygit_helper.py:1: R0401",
                     "excs.py:1: R0401",
                     "documentation_server.py:30: E0401",
                     "Unable to import 'src.pyquickhelper.helpgen.sphinxm_mock_app'",
                     "venv_helper.py:209: R1714",
                     "venv_helper.py:237: R1714",
                     "venv_helper.py:242: R1714",
                     "utils_tests_helper.py:36",
                     "sphinxm_convert_doc_helper.py:20: E0401",
                     "No name 'sphinxm_mock_app' in module 'src.pyquickhelper.helpgen'",
                     "cli_helper.py:233: R1714",
                     ])


def _private_test_style_test(fLOG, run_lint, verbose=False, pattern=".*[.]py$"):
    thi = os.path.abspath(os.path.dirname(__file__))
    test_ = os.path.normpath(os.path.join(thi, "..", "..", '..', '_unittests'))
    check_pep8(test_, fLOG=fLOG, neg_pattern="temp[0-9]?_.*", pattern=pattern,
               max_line_length=200, run_lint=run_lint, verbose=verbose,
               run_cmd_filter=_run_cmd_filter,
               pylint_ignore=('C0111', 'C0103', 'R0914', 'W0212', 'C0413', 'W0621',
                              'W0703', 'W0622', 'W0122', 'R0912', 'R0201',
                              'W0613', 'C0123', 'W0640', 'E0202', 'C0412',
                              'R1702', 'W0612', 'C0411', 'E1101', 'C0122',
                              'W0201', 'E0702', 'W1503', 'C0102', 'W0223',
                              'W0611', 'R1705', 'W0631', 'W0102', 'R0205'),
               skip=["src' imported but unused",
                     "skip_' imported but unused",
                     "skip__' imported but unused",
                     "skip___' imported but unused",
                     "2test_download_pip.py",
                     "[E402] module ",
                     "Unused import src",
                     "Unused variable 'skip_",
                     "imported as skip_",
                     "Unable to import 'StringIO'",
                     "Redefining built-in 'open'",
                     "Do not use `len(SEQUENCE)`",
                     "test_file_tree_node.py:43: W0613: Unused argument 'root'",
                     "Unused variable 'fig'",
                     "ut_sphinxext\\data",
                     "ut_helpgen\\data",
                     "ut_sphinxext/data",
                     "ut_helpgen/data",
                     "Unused argument 'node'",
                     "Redefining built-in 'FileNotFoundError'",
                     "test_check_pep8_sample.py:39",
                     "test_check_pep8_sample.py:40",
                     "Unable to import 'pyquickhelper",
                     "Unable to import 'jyquickhelper",
                     "Unable to import 'exsig'",
                     "est_utils_sphinxdoc2.py:26: C0414",
                     "test_utils_sphinxdoc.py:28: C0414",
                     "test_full_documentation.py:27: C0414",
                     "test_yaml.py:23: E0401",
                     "test_yaml.py:24: E0401",
                     "test_yaml.py:25: E0401",
                     "Unable to import 'src.pyquickhelper.helpgen.sphinxm_mock_app'",
                     "Unable to import 'src.pyquickhelper.jenkinshelper",
                     "Unable to import 'src.pyquickhelper",
                     "No name 'sphinxm_mock_app' in module 'src.pyquickhelper.helpgen'",
                     ])
