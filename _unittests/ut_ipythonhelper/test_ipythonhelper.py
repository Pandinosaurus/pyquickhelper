"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import re


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

from src.pyquickhelper import AutoCompletion, fLOG, AutoCompletionFile, open_html_form, MagicCommandParser, MagicClassWithHelpers


class TestAutoCompletion (unittest.TestCase):

    def test_completion(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        root = AutoCompletion()
        cl = root._add("name", "TestAutoCompletion")
        cl._add("method", "test_completion")
        cl._add("method2", "test_completion")
        cl = root._add("name2", "TestAutoCompletion2")
        cl._add("method3", "test_completion")
        s = str(root)
        fLOG("\n" + s)
        assert " |   |- method2" in s
        l = len(root)
        fLOG("l=", l)
        assert l == 6
        fLOG(root._)

    def test_completion_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.join(fold, "..", "..", "src")
        this = AutoCompletionFile(fold)
        l = len(this)
        assert l > 30

    def test_html_form(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        params = {"parA": "valueA", "parB": "valueB"}
        title = 'unit_test_title'
        key_save = 'jjj'
        raw = open_html_form(params, title, key_save, raw=True)
        fLOG(raw)
        assert len(raw) > 0

    def test_eval(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        params = {"x": 3, "y": 4}
        cl = MagicCommandParser()
        res = cl.eval("x+y", params, fLOG=fLOG)
        fLOG(res)
        assert res == 7

    def test_parse(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        parser = MagicCommandParser(
            description='display the first lines of a text file')
        parser.add_argument('f', type=str, help='filename')
        parser.add_argument(
            '-n',
            '--n',
            type=str,
            default=10,
            help='number of lines to display')
        parser.add_argument(
            '-e',
            '--encoding',
            default="utf8",
            help='file encoding')
        params = {"x": 3, "y": 4}
        res = parser.parse_cmd('this.py -n x+y', context=params, fLOG=fLOG)
        fLOG(res.__dict__)
        assert res.n == 7

    def test_class_magic(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        cl = MagicClassWithHelpers()
        assert cl.Context is None
        pa = cl.get_parser(MagicCommandParser, "parser_unittest")
        pa.add_argument('f', type=str, help='filename')
        pa.add_argument(
            '-n',
            '--n',
            type=str,
            default=10,
            help='number of lines to display')
        pa.add_argument(
            '-e',
            '--encoding',
            default="utf8",
            help='file encoding')
        assert pa is not None
        cl.add_context({"x": 3, "y": 4})
        assert cl.Context == {"x": 3, "y": 4}
        res = cl.get_args('this.py -n x+y', pa, print_function=fLOG)
        fLOG("**RES", res)
        assert res.n == 7


if __name__ == "__main__":
    unittest.main()
