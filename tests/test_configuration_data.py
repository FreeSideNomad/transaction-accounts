import unittest
import json
from datetime import date
from accounts.configuration import Configuration, ConfigurationData
from accounts.metadata import AccountType
from accounts.session import SessionData
from accounts.utility import custom_json_dumps


def normalize_json(data):
    if isinstance(data, str):
        data = json.loads(data)
    return custom_json_dumps(data)

class TestConfigurationData(unittest.TestCase):

    def setUp(self):
        self.config = Configuration(
            name="config1",
            label="Config 1",
            version=1,
            account_types=[
                AccountType(name="savings", label="Savings"),
                AccountType(name="loans", label="Loans")
            ]
        )
        self.config_data = ConfigurationData(
            name="config1",
            label="Config 1",
            version=1,
            account_types=[
                {"name": "savings", "label": "Savings"},
                {"name": "loans", "label": "Loans"}
            ],
            tenant_name="tenant1"
        )

        SessionData.set_session_info("tenant1", date(2025, 1, 1), date(2025, 1, 1), "user1", "User 1")


    def test_to_data(self):
        config_data = ConfigurationData()
        config_data.to_data(self.config)

        self.assertEqual(config_data.name, self.config.name)
        self.assertEqual(config_data.label, self.config.label)
        self.assertEqual(config_data.version, self.config.version)

        config_data_json = normalize_json(config_data.account_types)
        self_config_data_json = normalize_json(self.config_data.account_types)

        self.assertEqual(config_data_json, self_config_data_json)

        self.assertEqual(config_data_json, self_config_data_json)
        self.assertEqual(config_data.tenant_name, "tenant1")
