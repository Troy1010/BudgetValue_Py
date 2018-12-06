def GetAllChildren(vItem):
    return GetAllChildren_Helper(vItem).GetAllChildren()


class GetAllChildren_Helper():
    def __init__(self, vItem):
        self.cChildren = [vItem]
        self.AppendChildren(vItem)

    def GetAllChildren(self):
        return self.cChildren

    def AppendChildren(self, vItem):
        for vChild in vItem.winfo_children():
            self.cChildren.append(vChild)
            self.AppendChildren(vChild)
