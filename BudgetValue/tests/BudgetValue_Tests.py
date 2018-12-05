##region Settings
bSkip=False
bSkipSome=False
bPostDelete=False
##endregion
import unittest
from nose.tools import *
import os, sys
import TM_CommonPy as TM

@unittest.skipIf(bSkip,"Skip Setting")
class Test_BudgetValue(unittest.TestCase):
    sTestWorkspace = "TestWorkspace/"

    @classmethod
    def setUpClass(self):
        os.chdir(os.path.join('BudgetValue','tests'))
        TM.Delete(self.sTestWorkspace)

    @classmethod
    def tearDownClass(self):
        global bPostDelete
        if bPostDelete:
            TM.Delete(self.sTestWorkspace)
        os.chdir(os.path.join('..','..'))

    # ------Tests

    @unittest.skipIf(bSkipSome,"SkipSome Setting")
    def test_DummyTest(self):
        with TM.CopyContext("res/Examples_Backup",self.sTestWorkspace+TM.FnName(),bPostDelete=False):
            self.assertTrue(True)
