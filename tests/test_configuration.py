import json
import unittest
import yaml
from accounts.metadata import *
from tests.test_config import create_savings_account


class TestConfiguration(unittest.TestCase):

    def test_serialize(self):
        # Function to filter out None values
        def filter_none(d):
            return {k: v for k, v in d.items() if v is not None}

        account_type = create_savings_account()

        # serialize config to text using Pydantic

        text = account_type.model_dump_json()

        data = json.loads(text, object_hook=filter_none)

        account_type2 = AccountType.model_validate(data, strict=False)

        text2 = account_type2.model_dump_json()

        self.assertEqual(text, text2)


class RateTest(unittest.TestCase):
    def test_get_max_when_empy(self):
        rate_type = RateType(name='rates', label='Rates')

        max_value = rate_type.get_max_to_amount(value_date=date(2019, 7, 1))

        self.assertEqual(Decimal(0), max_value)

    def test_get_max_when_non_empy(self):
        rate_type = RateType(name='rates', label='Rates')

        rate_type.add_tier(date(2019, 1, 1), Decimal(100), Decimal(5))

        max_value = rate_type.get_max_to_amount(date(2019, 1, 1))

        self.assertEqual(Decimal(100), max_value)


if __name__ == '__main__':
    unittest.main()
