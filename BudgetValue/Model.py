from BudgetValue._Logger import BVLog  # noqa
import sqlite3
import pandas as pd
import TM_CommonPy as TM  # noqa
import os
from pathlib import Path


class Model():
    def __init__(self):
        self.sPath = str(Path.home()) \
            + "/Documents/BudgetValue/SpendingsHistory.db"
        TM.TryMkdir(os.path.dirname(self.sPath))
        self.connection = sqlite3.connect(self.sPath)
        self.SpendingHistory = SpendingHistory(self)


class SpendingHistory():
    def __init__(self, vModel):
        self.vModel = vModel

    def Import(self, sFilePath):
        columns = ["Catagory", "Timestamp",
                   "Title", "Amount", "Description"]
        # Determine data
        data = []
        extension = os.path.splitext(sFilePath)[1][1:]
        if extension == 'csv':
            for index, row in pd.read_csv(sFilePath).iterrows():
                data.append(["<DefaultCatagory>", row[0], row[2],
                             row[3] if not pd.isnull(row[3]) else row[4], row[5]])
        else:
            BVLog.debug("Unrecognized file extension:" + extension)
            return
        # Write to database
        sheet = pd.DataFrame(columns=columns, data=data)
        name = "SpendingHistory"
        try:
            sheet.to_sql(
                name, self.vModel.connection, index=False)
        except ValueError:
            BVLog.debug("Sheet already exists:" + name)
            self.vModel.connection.execute("DROP TABLE " + name)
            sheet.to_sql(
                name, self.vModel.connection, index=False)
        self.vModel.connection.commit()

    def GetTable(self):
        cursor = self.vModel.connection.cursor()
        try:
            cursor.execute("SELECT * FROM 'SpendingHistory'")
        except sqlite3.OperationalError:
            pass
        return cursor

    def GetHeader(self):
        cursor = self.vModel.connection.cursor()
        try:
            cursor.execute("SELECT * FROM 'SpendingHistory'")
        except sqlite3.OperationalError:
            return []
        return [description[0] for description in cursor.description]
