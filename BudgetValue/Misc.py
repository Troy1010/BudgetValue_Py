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


def select_text(widget):
    widget.select_range(0, 'end')
    widget.icursor('end')


def GetRow(cell):
    return cell.grid_info()['row']


def GetCell(table, cRowColumnPair):
    return table.grid_slaves(cRowColumnPair[0], cRowColumnPair[1])[0]
