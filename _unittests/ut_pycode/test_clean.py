"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest
import warnings

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.pycode.code_helper import remove_extra_spaces_and_pep8, remove_extra_spaces_folder
from pyquickhelper.pycode.clean_helper import clean_exts
from pyquickhelper.pycode.ci_helper import is_travis_or_appveyor


class TestClean(ExtTestCase):

    def test_pep8(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ("travis", "appveyor"):
            return

        this = os.path.abspath(__file__.replace(".pyc", ".py"))
        try:
            diff = remove_extra_spaces_and_pep8(this)
        except IndexError as e:
            warnings.warn("probably an issue with pep8: " + str(e))
            return
        self.assertLesser(diff, 10)

    def test_extra_space(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        try:
            diff = remove_extra_spaces_folder(this)
        except IndexError as e:
            warnings.warn("probably an issue with pep8: " + str(e))
            return
        self.assertIsInstance(diff, list)

    def test_clean_exts(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        def fclean(name):
            if "stdchelper.cp37-win_amd64.pyd" in name:
                return False
            if "stdchelper_demo.cp%d%d-win_amd64.pyd" % sys.version_info[:2] in name:
                return False
            return True

        this = os.path.abspath(os.path.dirname(__file__))
        try:
            diff = clean_exts(this, fclean=fclean)
        except PermissionError as e:
            if "anaconda" in sys.executable.lower():
                # we disable it for Anaconda
                return
            raise Exception("unable to clean " + this +
                            "\nexe: " + sys.executable) from e
        self.assertIsInstance(diff, list)

    def test_clean_pep8(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_pep8_clean")
        name = os.path.join(temp, "python_try.py")
        with open(name, "w") as f:
            f.write("""
                import sys
                import os

                def f1 () :
                    #g
                    return [2,3]
                """.replace("                ", ""))
        r = remove_extra_spaces_and_pep8(name)
        self.assertGreater(r, 0)
        with open(name, "r") as f:
            content = f.read()
        self.assertEqual(content.strip(), """
                import sys
                import os


                def f1():
                    # g
                    return [2, 3]
                """.replace("                ", "").strip())
        r = remove_extra_spaces_and_pep8(name)
        self.assertEqual(r, 0)


if __name__ == "__main__":
    unittest.main()
