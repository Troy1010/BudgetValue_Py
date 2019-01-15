import decimal
from decimal import Decimal
from ._Logger import BVLog


def Hello():
    BVLog.debug("Hello")


def GetAllChildren(vItem, bIncludeRoot=False):
    return GetAllChildren_Helper(vItem, bIncludeRoot=bIncludeRoot).GetAllChildren()


class GetAllChildren_Helper():
    def __init__(self, vItem, bIncludeRoot):
        self.cChildren = []
        if bIncludeRoot:
            self.cChildren.append(vItem)
        self.AppendChildren(vItem)

    def GetAllChildren(self):
        return self.cChildren

    def AppendChildren(self, vItem):
        for vChild in vItem.winfo_children():
            self.cChildren.append(vChild)
            self.AppendChildren(vChild)


def MakeValid_Money(value):
    returning = Decimal(str(value)).quantize(Decimal('0.01'), rounding=decimal.ROUND_UP)
    if returning % 1 == 0:
        returning = returning.quantize(Decimal('1.'))
    return returning
