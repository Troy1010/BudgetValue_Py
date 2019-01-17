from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import sqlite3
import pandas as pd
import os
from decimal import Decimal


class SpendingHistory():
    def __init__(self, vModel):
        self.vModel = vModel

    def Import(self, sFilePath):
        columns = ["Category", "Timestamp", "Title", "Amount", "Description"]
        # Determine data
        data = []
        extension = os.path.splitext(sFilePath)[1][1:]
        if extension == 'csv':
            for index, row in pd.read_csv(sFilePath).iterrows():
                data.append(["<DefaultCategory>", row[0], row[2],
                             row[3] if not pd.isnull(row[3]) else row[4], row[5]])
        else:
            BVLog.debug("Unrecognized file extension:" + extension)
            return
        # Write to database
        sheet = pd.DataFrame(columns=columns, data=data)
        name = "SpendingHistory"
        try:
            self.vModel.connection.execute("DROP TABLE " + name)
        except sqlite3.OperationalError:  # table already doesn't exist
            pass
        sheet.to_sql(name, self.vModel.connection, index=True)
        self.vModel.connection.commit()

    def GetTotalOfAmountsOfCategory(self, category):
        categoryCursor = self.vModel.connection.cursor()
        try:
            categoryCursor.execute("SELECT category FROM 'SpendingHistory'")
        except sqlite3.OperationalError:  # SpendingHistory doesn't exist
            pass
        amountCursor = self.vModel.connection.cursor()
        try:
            amountCursor.execute("SELECT amount FROM 'SpendingHistory'")
        except sqlite3.OperationalError:  # SpendingHistory doesn't exist
            pass
        cCategories = [x[0] for x in categoryCursor]
        cAmounts = [x[0] for x in amountCursor]
        dTotal = Decimal(0)
        for category_, amount in zip(cCategories, cAmounts):
            if str(category_) == str(category):
                dTotal += Decimal(str(amount))
        return dTotal

    def GetTable(self):
        cursor = self.vModel.connection.cursor()
        try:
            cursor.execute("SELECT * FROM 'SpendingHistory'")
        except sqlite3.OperationalError:  # SpendingHistory doesn't exist
            pass
        return cursor

    def GetHeader(self):
        try:
            header = [description[0] for description in self.GetTable().description]
        except TypeError:  # GetTable() was not iterable
            header = []
        return header

    def Update(self, cRowColumnPair, value):
        cursor = self.GetTable()
        cursor.execute(
            """ UPDATE 'SpendingHistory'
                SET """ + str(cRowColumnPair[1]) + """ = ?
                WHERE `index` = ?
                """,
            [value, cRowColumnPair[0]]
        )
        self.vModel.connection.commit()
