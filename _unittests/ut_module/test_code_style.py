"""
@brief      test log(time=284s)
"""

import sys
import os
import unittest
import warnings

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import is_travis_or_appveyor, ExtTestCase
from pyquickhelper.pycode._pylint_common import _private_test_style_src, _private_test_style_test


class TestCodeStyle(ExtTestCase):

    def test_style_src(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        run_lint = is_travis_or_appveyor(env=['NAME_JENKINS']) is None
        _private_test_style_src(fLOG, run_lint, verbose='-v' in sys.argv)

    def test_style_test(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        run_lint = is_travis_or_appveyor(env=['NAME_JENKINS']) is None
        _private_test_style_test(fLOG, run_lint, verbose='-v' in sys.argv)


if __name__ == "__main__":
    unittest.main()
