import os
import unittest
import TM_CommonPy as TM
from nose.plugins.attrib import attr
# Settings
bPostDelete = False
# Globals
vCounter = TM.Counter()


class Test_BudgetValue(unittest.TestCase):
    sTestWorkspace = "_TestWorkspace_SameFolder/"

    @classmethod
    def setUpClass(self):
        self.sOldCWD = os.getcwd()
        os.chdir(os.path.dirname(__file__))
        TM.Copy("res/Examples_Backup", self.sTestWorkspace,
                bPreDelete=True, bCDInto=True)

    @classmethod
    def tearDownClass(self):
        global bPostDelete
        if bPostDelete:
            os.chdir(os.path.dirname(__file__))
            TM.Delete(self.sTestWorkspace)
        os.chdir(self.sOldCWD)

    # ------Tests
    @attr(**{'count': vCounter(), __name__.rsplit(".", 1)[-1]: True})
    def test_Dummy(self):
        self.assertTrue(True)
