import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from accounts.configuration import ConfigurationData, Base
from accounts.repository import SQLAlchemyConfigurationRepository

class TestSQLAlchemyConfigurationRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.Session()
        self.repo = SQLAlchemyConfigurationRepository(self.session)

    def tearDown(self):
        self.session.query(ConfigurationData).delete()
        self.session.commit()
        self.session.close()

    def test_save_new_configuration(self):
        config = ConfigurationData(name="config1", label="Config 1", version=1, account_types=[], tenant_name="tenant1")
        saved_config = self.repo.save(config)
        self.assertEqual(saved_config.version, 1)
        self.assertEqual(len(self.repo.get_all_configurations()), 1)

    def test_save_existing_configuration(self):
        config1 = ConfigurationData(name="config1", label="Config 1", version=1, account_types=[], tenant_name="tenant1")
        config2 = ConfigurationData(name="config1", label="Config 1 Updated", version=1, account_types=[], tenant_name="tenant1")
        self.repo.save(config1)
        saved_config = self.repo.save(config2)
        self.assertEqual(saved_config.version, 2)
        self.assertEqual(len(self.repo.get_all_configurations()), 2)

    def test_get_latest_configuration_by_name(self):
        config1 = ConfigurationData(name="config1", label="Config 1", version=1, account_types=[], tenant_name="tenant1")
        config2 = ConfigurationData(name="config1", label="Config 1 Updated", version=2, account_types=[], tenant_name="tenant1")
        self.repo.save(config1)
        self.repo.save(config2)
        latest_config = self.repo.get_latest_configuration_by_name("config1")
        self.assertEqual(latest_config.version, 2)
        self.assertEqual(latest_config.label, "Config 1 Updated")

    def test_get_all_configurations(self):
        config1 = ConfigurationData(name="config1", label="Config 1", version=1, account_types=[], tenant_name="tenant1")
        config2 = ConfigurationData(name="config2", label="Config 2", version=1, account_types=[], tenant_name="tenant1")
        self.repo.save(config1)
        self.repo.save(config2)
        all_configs = self.repo.get_all_configurations()
        self.assertEqual(len(all_configs), 2)

if __name__ == '__main__':
    unittest.main()