from BudgetValue._Logger import BVLog  # noqa
import sqlite3
import pandas
import TM_CommonPy as TM  # noqa
import os


class BudgetValueModel():
    connection = sqlite3.connect("SpendingsHistory.db")

    def ImportHistory(self, sFilePath):
        sheet = pandas.read_csv(sFilePath)
        sName = os.path.basename(sFilePath)
        try:
            sheet.to_sql(sName, self.connection, index=False)
        except ValueError:
            BVLog.debug("Sheet already exists:" + sName)
        self.connection.commit()
