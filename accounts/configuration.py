from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from accounts.metadata import AccountType
from accounts.session import ReadOnlySession, SessionData

Base = declarative_base()

class Configuration(BaseModel):
    name: str
    label: str
    version: int
    account_types: list[AccountType]

class TenantConfiguration(Configuration):
    tenant_name: str

class ConfigurationData(Base):
    __tablename__ = 'configuration'
    name = Column(String(50), primary_key=True)
    label = Column(String(50))
    version = Column(Integer, primary_key= True)
    account_types = Column(JSON)
    tenant_name = Column(String(50), primary_key=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'tenant_name' not in kwargs:
            session_info = SessionData.get_session_info()
            self.tenant_name = session_info.get('tenant_name', 'default_tenant') if session_info else 'default_tenant'

    def to_data(self, config: Configuration):
        self.name = config.name
        self.label = config.label
        self.version = config.version
        self.account_types = self.serialize_account_types(config.account_types)

    def from_data(self) -> Configuration:
        return Configuration(
            name=self.name,
            label=self.label,
            version=self.version,
            account_types=self.deserialize_account_types(self.account_types),
            tenant_name= ReadOnlySession.get_session_info().get('tenant_name')
        )

    @staticmethod
    def serialize_account_types(account_types: list[AccountType]) -> list[dict]:
        return [account_type.dict() for account_type in account_types]

    @staticmethod
    def deserialize_account_types(data: list[dict]) -> list[AccountType]:
        return [AccountType(**item) for item in data]