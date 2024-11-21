import unittest
from accounts.accounts import AccountData, PositionData, TransactionData
from accounts.repository import InMemoryAccountRepository

class TestInMemoryAccountRepository(unittest.TestCase):

    def setUp(self):
        self.repo = InMemoryAccountRepository()

    def test_create_account(self):
        account = AccountData(account_number="123", additional_info={})
        positions = [PositionData(account_number="123", position_type="type1", amount=100, additional_info={})]
        transactions = [TransactionData(account_number="123", transaction_type="type1", amount=100, additional_info={})]
        self.repo.create_account(account, positions, transactions)
        account_data = self.repo.get_account_data("123")
        self.assertEqual(account_data["account"].account_number, "123")
        self.assertEqual(len(account_data["positions"]), 1)
        self.assertEqual(len(account_data["transactions"]), 1)

    def test_update_account_additional_info(self):
        account = AccountData(account_number="123", additional_info={})
        self.repo.create_account(account, [], [])
        self.repo.update_account_additional_info("123", {"key": "value"})
        account_data = self.repo.get_account_data("123")
        self.assertEqual(account_data["account"].additional_info, {"key": "value"})

    def test_create_transactions(self):
        account = AccountData(account_number="123", additional_info={})
        self.repo.create_account(account, [], [])
        positions = [PositionData(account_number="123", position_type="type1", amount=100, additional_info={})]
        transactions = [TransactionData(account_number="123", transaction_type="type1", amount=100, additional_info={})]
        self.repo.create_transactions(positions, transactions)
        account_data = self.repo.get_account_data("123")
        self.assertEqual(len(account_data["positions"]), 1)
        self.assertEqual(len(account_data["transactions"]), 1)

    def test_get_account_data(self):
        account = AccountData(account_number="123", additional_info={})
        positions = [PositionData(account_number="123", position_type="type1", amount=100, additional_info={})]
        transactions = [TransactionData(account_number="123", transaction_type="type1", amount=100, additional_info={})]
        self.repo.create_account(account, positions, transactions)
        account_data = self.repo.get_account_data("123")
        self.assertEqual(account_data["account"].account_number, "123")
        self.assertEqual(len(account_data["positions"]), 1)
        self.assertEqual(len(account_data["transactions"]), 1)

if __name__ == '__main__':
    unittest.main()