import decimal
from decimal import Decimal
from ._Logger import BVLog
from ._Logger import Log  # noqa
import TM_CommonPy as TM  # noqa
from datetime import datetime
import time


def ValidateTimestamp(num):
    if isinstance(num, str):
        return time.mktime(datetime.strptime(num, '%Y-%m-%d %H:%M').timetuple())
    elif isinstance(num, datetime):
        return time.mktime(num.timetuple())
    else:
        return float(num)


def DisplayTimestamp(timestamp):
    if timestamp == 0:
        return ""
    dt = datetime.fromtimestamp(timestamp)
    str_ = dt.strftime('%Y-%m-%d %H:%M')
    return str_


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
