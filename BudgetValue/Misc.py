import TM_CommonPy as TM


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
    if value.is_integer():
        return int(value)
    return float('{0:.2f}'.format(TM.Ceil(value, 2)))
