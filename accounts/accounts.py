from sqlalchemy import Column, String, Integer, Date, DECIMAL, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class PositionData(Base):
    __tablename__ = 'position_data'
    account_number = Column(String(50), primary_key=True)
    position_type = Column(String(50), primary_key=True)
    amount = Column(DECIMAL)
    additional_info = Column(JSON)

class AccountData(Base):
    __tablename__ = 'account_data'
    account_number = Column(String(50), primary_key=True)
    account_type = Column(String(50))
    configuration_name = Column(String(50))
    configuration_version = Column(Integer)
    tenant_name = Column(String(50))
    additional_info = Column(JSON)

class TransactionData(Base):
    __tablename__ = 'transaction_data'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number = Column(String(50), ForeignKey('account_data.account_number'))
    transaction_id = Column(String(50))
    amount = Column(DECIMAL)
    action_date = Column(Date)
    value_date = Column(Date)
    transaction_type = Column(String(50))
    payment_id = Column(String(50))
    system_generated = Column(Boolean)
    additional_info = Column(JSON)

