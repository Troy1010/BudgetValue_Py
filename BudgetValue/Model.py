from BudgetValue._Logger import BVLog  # noqa
import sqlite3
import pandas
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
        sheet = pandas.read_csv(sFilePath)
        sName = os.path.basename(sFilePath)
        try:
            sheet.to_sql(sName, self.vModel.connection, index=False)
        except ValueError:
            BVLog.debug("Sheet already exists:" + sName)
        self.vModel.connection.commit()

    def GetTable(self):
        cursor = self.vModel.connection.cursor()
        cursor.execute("SELECT * FROM 'transactions.csv'")
        return cursor

    def GetHeader(self):
        cursor = self.vModel.connection.cursor()
        cursor.execute("SELECT * FROM 'transactions.csv'")
        return [description[0] for description in cursor.description]
