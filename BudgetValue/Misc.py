import decimal
from decimal import Decimal
from ._Logger import BVLog  # noqa
from ._Logger import Log  # noqa
import TM_CommonPy as TM  # noqa
from datetime import datetime
import time  # noqa


def ValidateTimestamp(timestamp):
    if isinstance(timestamp, str):
        return datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
    elif isinstance(timestamp, datetime) or timestamp is None:
        return timestamp
    else:
        return datetime.fromtimestamp(timestamp)


def DisplayTimestamp(timestamp):
    if timestamp is None:
        return "<no timestamp>"
    else:
        return timestamp.strftime('%Y-%m-%d %H:%M')


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
    if value is None:
        value = 0
    try:
        returning = Decimal(str(value)).quantize(Decimal('0.01'), rounding=decimal.ROUND_UP)
        if returning % 1 == 0:
            returning = returning.quantize(Decimal('1.'))
    except decimal.InvalidOperation:
        returning = Decimal(0)
    return returning


def MakeValid_Money_ZeroIsNone(value):
    value = MakeValid_Money(value)
    return None if not value or value == 0 else value


def MakeValid_Money_Negative(value):
    value = MakeValid_Money(value)
    if value > 0:
        return Decimal(0)
    else:
        return value


def MakeValid_Money_Negative_ZeroIsNone(value):
    value = MakeValid_Money_Negative(value)
    return None if not value or value == 0 else value


def DisplayZeroIsNone(value):
    return None if not value or value == 0 else value
