import os
import pickle
import BudgetValue as BV
import rx
from . import Misc  # noqa
from .Categories import Categories  # noqa
import time
import TM_CommonPy as TM  # noqa
import pandas as pd
from BudgetValue._Logger import Log  # noqa
import time  # noqa
from datetime import datetime  # noqa
from datetime import date  # noqa


class TransactionHistory(Misc.List_ValueStream):
    def __init__(self, vModel):
        super().__init__()
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "TransactionHistory.pickle")
        # subscribe _merged_amountStream_stream
        self.cDisposables = {}
        self._merged_amountStream_stream = rx.subjects.Subject()

        def MergeAmountStreamStreams(vValueAddPair):
            if vValueAddPair.bAdd:
                self.cDisposables[vValueAddPair.value] = vValueAddPair.value.categoryAmounts._amountStream_stream.subscribe(self._merged_amountStream_stream)
            else:
                self.cDisposables[vValueAddPair.value].dispose()
                del self.cDisposables[vValueAddPair.value]
        self._value_stream.subscribe(MergeAmountStreamStreams)

    def ClearAllTransactions(self):
        self.clear()

    def Import(self, sFilePath):
        # save old record
        self.SaveArchive()
        #
        extension = os.path.splitext(sFilePath)[1][1:]
        assert extension == 'csv'
        data_frame = pd.read_csv(sFilePath)
        for i, column_name in enumerate(data_frame.columns):
            if "Description" in column_name:
                description_column = i
            if "Amount" == column_name:
                withdrawal_column = i
                deposit_column = i
            if "Withdrawal" in column_name:
                withdrawal_column = i
            if "Deposit" in column_name:
                deposit_column = i
        assert description_column
        assert withdrawal_column
        assert deposit_column
        for index, row in data_frame.iterrows():
            if withdrawal_column != deposit_column:
                if not pd.isnull(row[withdrawal_column]):
                    amount = row[withdrawal_column]
                    bSpend = True
                else:
                    amount = row[deposit_column]
                    bSpend = False
            else:
                amount = row[withdrawal_column]
                bSpend = amount <= 0
            if not self.IsAlreadyHere_ByProperties(BV.ValidateTimestamp(time.time()), amount, row[description_column]):
                self.AddTransaction(bSpend, amount, timestamp=BV.ValidateTimestamp(time.time()), description=row[description_column])

    def Iter_Spend(self):
        for transaction in self:
            if transaction.IsSpend():
                yield transaction

    def Iter_Income(self):
        for transaction in self:
            if transaction.IsIncome() or transaction.IsOverride():
                yield transaction

    def GetIncome(self):
        return list(self.Iter_Income())

    def GetSpends(self):
        return list(self.Iter_Spend())

    def IsAlreadyHere_ByProperties(self, timestamp, amount, description):
        for transaction_iter in self:
            if self.IsSame_ByProperties(transaction_iter, timestamp, amount, description):
                return True
        return False

    def IsSame_ByProperties(self, transaction, timestamp, amount, description):
        if date.fromtimestamp(transaction.timestamp) != date.fromtimestamp(timestamp):
            return False
        if transaction.amount != BV.MakeValid_Money(amount):
            return False
        if str(transaction.description) != str(description):
            return False
        return True

    def AddTransaction(self, bSpend, amount=None, timestamp=None, description=None):
        transaction = Transaction(self.vModel, self, bSpend)
        self.append(transaction)
        if amount is not None:
            transaction.amount = amount
        if timestamp is not None:
            transaction.timestamp = timestamp
        if description is not None:
            transaction.description = description
        return transaction

    def RemoveTransaction(self, transaction):
        if isinstance(transaction, Transaction):
            self.remove(transaction)
        elif isinstance(transaction, int):
            del self[transaction]

    def GetArchivedTransactionHistories(self):
        archived_transaction_histories = list(f for f in os.listdir(self.vModel.sWorkspace) if f.startswith(os.path.basename(self.sSaveFile)[0:os.path.basename(self.sSaveFile).index('.pickle')]))
        value_to_remove = None
        for x in archived_transaction_histories:
            if os.path.basename(x) == os.path.basename(self.sSaveFile):
                value_to_remove = x
                break
        if value_to_remove is not None:
            archived_transaction_histories.remove(value_to_remove)
        return archived_transaction_histories

    def SaveArchive(self):
        # determine save_name
        save_name = self.sSaveFile[0:self.sSaveFile.index('.pickle')] + " " + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H.%M')
        if os.path.exists(save_name+'.pickle'):
            relevant_save_files = list(f for f in os.listdir(self.vModel.sWorkspace) if f.startswith(os.path.basename(save_name)))
            if relevant_save_files == []:
                Log("relevant_save_files is empty")
            file_dictated_index = 2
            for file_name in relevant_save_files:
                if '(' in file_name:
                    position_of_start_parenthesis = file_name.index('(')
                    position_of_end_parenthesis = file_name.index(')', position_of_start_parenthesis)
                    file_dictated_index = max(file_dictated_index, 1 + int(file_name[position_of_start_parenthesis+1:position_of_end_parenthesis]))
            save_name = save_name + " ("+str(file_dictated_index)+")"
        save_name += '.pickle'
        # if over 20 archives, delete oldest one
        archived_transaction_histories = self.GetArchivedTransactionHistories()
        while len(archived_transaction_histories) >= 20:
            oldCWD = os.getcwd()
            os.chdir(self.vModel.sWorkspace)
            file_to_delete = min(archived_transaction_histories, key=os.path.getctime)
            TM.Delete(file_to_delete)
            archived_transaction_histories.remove(file_to_delete)
            os.chdir(oldCWD)
        # save
        self.Save(save_name=save_name)

    def Save(self, save_name=None):
        if save_name is None:
            save_name = self.sSaveFile
        # construct data
        data = list()
        for transaction in self:
            data.append(transaction.GetSavable())
        # dump save
        Log("Saving file:"+save_name)
        with open(save_name, 'wb') as f:
            pickle.dump(data, f)

    def Load(self, save_name=None):
        if save_name is None:
            save_name = self.sSaveFile
        if not os.path.exists(save_name):
            return
        with open(save_name, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for transaction_savable in data:
            transaction = Transaction(self.vModel, self, False)
            self.append(transaction)
            transaction.LoadSavable(transaction_savable)


class Transaction():
    def __init__(self, vModel, parent, bSpend):
        self.parent = parent
        self.vModel = vModel
        # non-derivative data
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        self.timestamp_stream = rx.subjects.BehaviorSubject(time.time())
        self.description_stream = rx.subjects.BehaviorSubject("")
        self.categoryAmounts = CategoryAmounts(vModel, self)
        self.bSpend = bSpend
        self.cValidationSources = None  # FIX: use
        self.bAlertNonValidation = True  # FIX: use

    def SetOneCategory(self, category):
        self.categoryAmounts.clear()
        self.categoryAmounts.AddCategory(category, amount=self.amount)

    def AddCategory(self, category, amount=None):
        self.categoryAmounts.AddCategory(category, amount=amount)

    def GetCategorySummary(self):
        if len(self.categoryAmounts) == 0:
            return Categories.default_category.name
        elif len(self.categoryAmounts) == 1:
            return list(self.categoryAmounts.values())[0].category.name
        else:
            return "<Multiple Categories>"

    def IsOverride(self):
        return not self.bSpend

    def IsSpend(self):
        return self.bSpend

    def IsIncome(self):
        return not self.bSpend

    def destroy(self):
        self.categoryAmounts.clear()
        self.amount = 0

    @property
    def description(self):
        return self.description_stream.value

    @description.setter
    def description(self, value):
        self.description_stream.on_next(value)

    @property
    def timestamp(self):
        return self.timestamp_stream.value

    @timestamp.setter
    def timestamp(self, value):
        self.timestamp_stream.on_next(value)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))

    def GetSavable(self):
        return {'amount': self.amount,
                'timestamp': self.timestamp,
                'description': self.description,
                'categoryAmounts': {categoryName: y.amount for (categoryName, y) in self.categoryAmounts.items()},
                'bSpend': self.bSpend
                }

    def LoadSavable(self, vSavable):
        self.amount = vSavable['amount']
        self.timestamp = vSavable['timestamp']
        self.description = vSavable['description']
        if 'bSpend' in vSavable:
            self.bSpend = vSavable['bSpend']
        for categoryName, amount in vSavable['categoryAmounts'].items():
            if categoryName not in self.vModel.Categories:  # fix: should not exist
                continue
            self.categoryAmounts.AddCategory(self.vModel.Categories[categoryName], amount)


class CategoryAmounts(Misc.Dict_TotalStream):
    def __init__(self, vModel, parent):
        super().__init__()
        self.parent = parent
        self.vModel = vModel
        # derivative data
        self.balance_stream = rx.subjects.BehaviorSubject(0)
        # manually merge balance_stream into parent's cCategoryTotals
        self.parent.parent._merged_amountStream_stream.on_next(Misc.StreamInfo(True, self.balance_stream, Categories.default_category.name))
        # subscribe balance_stream
        rx.Observable.combine_latest(
            self.parent.amount_stream,
            self.total_stream,
            lambda amount, categories_total: amount - categories_total
        ).subscribe(self.balance_stream)
        # category_summary_stream
        self.category_summary_stream = rx.subjects.BehaviorSubject(Categories.default_category.name)
        # subscribe category_summary_stream

        def OnNewAmountStream(amountStreamInfo):
            # fix: self.parent.GetCategorySummary() does not work here, but there should be an easier way
            assert isinstance(amountStreamInfo, BV.Model.StreamInfo)
            length_adjustment = -1 + 2*(amountStreamInfo.bAdd)
            if len(self) + length_adjustment == 0:
                category_summary = Categories.default_category.name
            elif len(self) + length_adjustment == 1:
                if length_adjustment == 1:
                    category_summary = amountStreamInfo.categoryName
                else:
                    category_summary = list(self.values())[0].category.name
            else:
                category_summary = "<Multiple Categories>"
            self.category_summary_stream.on_next(category_summary)
        self._amountStream_stream.subscribe(OnNewAmountStream)

    def GetAll(self):
        cAll = dict(self)
        default_category_amount = CategoryAmount(self)
        default_category_amount.category = Categories.default_category
        default_category_amount.amount_stream = self.balance_stream
        cAll[Categories.default_category.name] = default_category_amount
        return cAll

    def AddCategory(self, category, amount=None):
        if category == Categories.default_category:
            return
        self[category.name] = CategoryAmount(self)
        self[category.name].category = category
        if amount is not None:
            self[category.name].amount = amount

    def RemoveCategory(self, category):
        assert(category != Categories.default_category)
        if isinstance(category, str):
            del self[category]
        else:
            del self[category.name]


class CategoryAmount():
    def __init__(self, parent):
        self.parent = parent
        self.category_stream = rx.subjects.BehaviorSubject(Categories.default_category)
        self.amount_stream = rx.subjects.BehaviorSubject(0)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))

    @property
    def category(self):
        return self.category_stream.value

    @category.setter
    def category(self, value):
        if isinstance(value, str) and value in Categories:
            value = Categories[value]
        assert isinstance(value, BV.Model.Category)
        self.category_stream.on_next(value)
