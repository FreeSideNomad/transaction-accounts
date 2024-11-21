from abc import ABC, abstractmethod
from typing import List, Optional
from accounts.configuration import ConfigurationData
from accounts.accounts import AccountData, PositionData, TransactionData
from sqlalchemy.orm import Session

class ConfigurationRepository(ABC):

    @abstractmethod
    def get_all_configurations(self) -> List[ConfigurationData]:
        pass

    @abstractmethod
    def get_latest_configuration_by_name(self, name: str) -> Optional[ConfigurationData]:
        pass

    @abstractmethod
    def save(self, configuration: ConfigurationData) -> ConfigurationData:
        pass

class InMemoryConfigurationRepository(ConfigurationRepository):
    def __init__(self):
        self.configurations = []

    def get_all_configurations(self) -> List[ConfigurationData]:
        return self.configurations

    def get_latest_configuration_by_name(self, name: str) -> Optional[ConfigurationData]:
        configurations = [config for config in self.configurations if config.name == name]
        if not configurations:
            return None
        return max(configurations, key=lambda config: config.version)

    def save(self, configuration: ConfigurationData) -> ConfigurationData:
        latest_config = self.get_latest_configuration_by_name(configuration.name)
        if latest_config:
            configuration.version = latest_config.version + 1
        else:
            configuration.version = 1
        self.configurations.append(configuration)
        return configuration



class SQLAlchemyConfigurationRepository(ConfigurationRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_all_configurations(self) -> List[ConfigurationData]:
        return self.session.query(ConfigurationData).all()

    def get_latest_configuration_by_name(self, name: str) -> Optional[ConfigurationData]:
        return self.session.query(ConfigurationData).filter_by(name=name).order_by(ConfigurationData.version.desc()).first()

    def save(self, configuration: ConfigurationData) -> ConfigurationData:
        latest_config = self.get_latest_configuration_by_name(configuration.name)
        if latest_config:
            configuration.version = latest_config.version + 1
        else:
            configuration.version = 1
        self.session.add(configuration)
        self.session.commit()
        return configuration

class AccountRepository(ABC):

    @abstractmethod
    def create_account(self, account: AccountData, positions: List[PositionData], transactions: List[TransactionData]):
        pass

    @abstractmethod
    def update_account_additional_info(self, account_number: str, additional_info: dict):
        pass

    @abstractmethod
    def create_transactions(self, positions: List[PositionData], transactions: List[TransactionData]):
        pass

    @abstractmethod
    def get_account_data(self, account_number: str) -> dict:
        pass

class InMemoryAccountRepository(AccountRepository):
    def __init__(self):
        self.accounts = {}
        self.positions = []
        self.transactions = []

    def create_account(self, account: AccountData, positions: List[PositionData], transactions: List[TransactionData]):
        self.accounts[account.account_number] = account
        self.positions.extend(positions)
        self.transactions.extend(transactions)

    def update_account_additional_info(self, account_number: str, additional_info: dict):
        if account_number in self.accounts:
            self.accounts[account_number].additional_info = additional_info

    def create_transactions(self, positions: List[PositionData], transactions: List[TransactionData]):
        for position in positions:
            existing_position = next((p for p in self.positions if p.account_number == position.account_number and p.position_type == position.position_type), None)
            if existing_position:
                existing_position.amount = position.amount
                existing_position.additional_info = position.additional_info
            else:
                self.positions.append(position)
        self.transactions.extend(transactions)

    def get_account_data(self, account_number: str) -> dict:
        account = self.accounts.get(account_number)
        positions = [p for p in self.positions if p.account_number == account_number]
        transactions = [t for t in self.transactions if t.account_number == account_number]
        return {
            "account": account,
            "positions": positions,
            "transactions": transactions
        }


class SQLAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: Session):
        self.session = session

    def create_account(self, account: AccountData, positions: List[PositionData], transactions: List[TransactionData]):
        self.session.add(account)
        self.session.add_all(positions)
        self.session.add_all(transactions)
        self.session.commit()

    def update_account_additional_info(self, account_number: str, additional_info: dict):
        account = self.session.query(AccountData).filter_by(account_number=account_number).first()
        if account:
            account.additional_info = additional_info
            self.session.commit()

    def create_transactions(self, positions: List[PositionData], transactions: List[TransactionData]):
        with self.session.begin():
            for position in positions:
                existing_position = self.session.query(PositionData).filter_by(account_number=position.account_number, position_type=position.position_type).first()
                if existing_position:
                    existing_position.amount = position.amount
                    existing_position.additional_info = position.additional_info
                else:
                    self.session.add(position)
            self.session.add_all(transactions)

    def get_account_data(self, account_number: str) -> dict:
        account = self.session.query(AccountData).filter_by(account_number=account_number).first()
        positions = self.session.query(PositionData).filter_by(account_number=account_number).all()
        transactions = self.session.query(TransactionData).filter_by(account_number=account_number).all()
        return {
            "account": account,
            "positions": positions,
            "transactions": transactions
        }