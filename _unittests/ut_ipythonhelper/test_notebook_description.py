"""
@brief      test log(time=3s)
"""

import sys
import os
import unittest
import warnings

from pyquickhelper.ipythonhelper import read_nb
from pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_appveyor
from pyquickhelper.loghelper import fLOG


class TestNotebookDescription(ExtTestCase):

    def test_notebook_description(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_number")
        nbfile = os.path.join(temp, "..", "data", "pyensae_text2table.ipynb")
        assert os.path.exists(nbfile)
        nb = read_nb(nbfile)
        header, desc = nb.get_description()
        self.assertEqual(header, "Not so clean text to tables (pandas fails)")
        exp = "Converting a flat file to a table can be tricky sometimes. Most of the time, it goes well as follows:"
        self.assertEqual(desc, exp)

    @skipif_appveyor("cannot load library 'libcairo.so': error 0x7e")
    def test_notebook_thumbnail(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_number")
        nbfile = os.path.join(temp, "..", "data", "pyensae_text2table.ipynb")
        self.assertExists(nbfile)
        fLOG("reading", nbfile)
        nb = read_nb(nbfile)
        fLOG("creating thumbnail")
        image = nb.get_thumbnail()
        fLOG(type(image))

        temp = get_temp_folder(__file__, "temp_notebook_thumbnail")
        name = os.path.join(temp, "pyensae_text2table.thumb.png")
        fLOG("saving")
        image.save(name)
        self.assertExists(name)

        nbfile = os.path.join(temp, "..", "data", "notebook_with_svg.ipynb")
        self.assertExists(nbfile)
        fLOG("reading", nbfile)
        nb = read_nb(nbfile)
        fLOG("creating thumbnail")
        image = nb.get_thumbnail()
        name = os.path.join(temp, "notebook_with_svg.thumb.png")
        fLOG("saving")
        image.save(name)
        self.assertExists(name)

        nbfile = os.path.join(temp, "..", "data", "example_corrplot.ipynb")
        self.assertExists(nbfile)
        fLOG("reading", nbfile)
        nb = read_nb(nbfile)
        fLOG("creating thumbnail")
        image = nb.get_thumbnail()
        name = os.path.join(temp, "example_corrplot.thumb.png")
        fLOG("saving")
        image.save(name)
        self.assertExists(name)


if __name__ == "__main__":
    unittest.main()
