import os
import unittest
import TM_CommonPy as TM
from nose.plugins.attrib import attr
from ._Logger import BVLog_LogTests
import BudgetValue as BV
import decimal
# Settings
bPostDelete = False
# Globals
vCounter = TM.Counter()


class Test_BudgetValue(unittest.TestCase):
    sTestWorkspace = "TestWorkspace/"

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
    def test_rewqrweqr(self):
        BV.Misc.Hello()

    @attr(**{'count': vCounter(), __name__.rsplit(".", 1)[-1]: True})
    def test_MakeValid_Money_float(self):
        v = 1.234
        v = BV.MakeValid_Money(v)
        BVLog_LogTests.debug(v)
        self.assertEqual(v, decimal.Decimal(repr(1.24)))

    @attr(**{'count': vCounter(), __name__.rsplit(".", 1)[-1]: True})
    def test_MakeValid_Money_int(self):
        v = 4
        v = BV.MakeValid_Money(v)
        BVLog_LogTests.debug(v)
        self.assertEqual(v, decimal.Decimal(repr(4)))

    @attr(**{'count': vCounter(), __name__.rsplit(".", 1)[-1]: True})
    def test_PaycheckPlanRaisesSetKeyTypeError(self):
        with self.assertRaises(TypeError):
            vModel = BV.Model.Model()
            vModel.PaycheckPlan["qwer"] = 1
