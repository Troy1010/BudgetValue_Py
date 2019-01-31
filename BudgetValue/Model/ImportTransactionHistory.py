from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import sqlite3
import pandas as pd
import os
from decimal import Decimal
import rx
import BudgetValue as BV


class ImportTransactionHistory():
    def __init__(self, vModel):
        assert(isinstance(vModel, BV.Model.Model))
        self.vModel = vModel
        self.cColumnNames = ["Category", "Timestamp", "Title", "Amount", "Description"]
        self.ObserveUpdatedCategory = rx.subjects.Subject()
        self.update_stream = rx.subjects.Subject()
        # Determine cCategoryTotalStreams
        self.cCategoryTotalStreams = dict()
        for categoryName in self.vModel.Categories.keys():
            self.cCategoryTotalStreams[categoryName] = rx.subjects.BehaviorSubject(self._GetTotalOfAmountsOfCategory(categoryName))
        # stream updates to cCategoryTotalStreams

        def RedoTotals(self, cArgs):
            if cArgs['columnName'] == "Category":
                self.cCategoryTotalStreams[cArgs['old_value']].on_next(self._GetTotalOfAmountsOfCategory(cArgs['old_value']))
                self.cCategoryTotalStreams[cArgs['new_value']].on_next(self._GetTotalOfAmountsOfCategory(cArgs['new_value']))
        self.update_stream.subscribe(lambda cArgs: RedoTotals(self, cArgs))

    def Import(self, sFilePath):
        # Determine data
        data = []
        extension = os.path.splitext(sFilePath)[1][1:]
        if extension == 'csv':
            for index, row in pd.read_csv(sFilePath).iterrows():
                data.append(["<Default Category>", row[0], row[2],
                             row[3] if not pd.isnull(row[3]) else row[4], row[5]])
        else:
            BVLog.debug("Unrecognized file extension:" + extension)
            return
        # Write to database
        sheet = pd.DataFrame(columns=self.cColumnNames, data=data)
        name = "SpendingHistory"
        try:
            self.vModel.connection.execute("DROP TABLE " + name)
        except sqlite3.OperationalError:  # table already doesn't exist
            pass
        sheet.to_sql(name, self.vModel.connection, index=True)
        self.vModel.connection.commit()

    def _GetTotalOfAmountsOfCategory(self, categoryName):
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
        cCategoryNames = [x[0] for x in categoryCursor]
        cAmounts = [x[0] for x in amountCursor]
        dTotal = Decimal(0)
        for categoryName_iter, amount in zip(cCategoryNames, cAmounts):
            if categoryName_iter == str(categoryName):
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

    def GetCellValue(self, row, columnName):
        cursor = self.GetTable()
        cursor.execute(
            """ SELECT """ + columnName + """
                FROM 'SpendingHistory'
                WHERE `index` = ?
                """,
            [row]
        )
        return cursor.fetchone()[0]

    def Update(self, row, columnName, value):
        assert(columnName in self.cColumnNames)
        old_value = self.GetCellValue(row, columnName)
        cursor = self.GetTable()
        cursor.execute(
            """ UPDATE 'SpendingHistory'
                SET """ + columnName + """ = ?
                WHERE `index` = ?
                """,
            [value, row]
        )
        self.vModel.connection.commit()
        if str(columnName) == "Category":
            self.ObserveUpdatedCategory.on_next(self.vModel.Categories[value])
        self.update_stream.on_next({
            "row": row,
            "columnName": columnName,
            "new_value": value,
            "old_value": old_value,
        })
