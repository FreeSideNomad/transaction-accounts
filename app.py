import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from accounts.configuration import ConfigurationData, Base
from accounts.repository import SQLAlchemyConfigurationRepository
from urllib.parse import quote

POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "database")

# URL encode the password
POSTGRES_PASSWORD_ENCODED = quote(POSTGRES_PASSWORD)

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD_ENCODED}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app =  FastAPI(
    title="Transact Rule Configuration API",
    description="API to manage configurations for Transact Rules",
    version="1.0.0"
)

class ConfigurationRequest(BaseModel):
    name: str = Field(..., max_length=50)
    label: str = Field(..., max_length=50)
    account_types: List[dict]
    tenant_name: Optional[str] = Field(None, max_length=50)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/configurations", response_model=List[ConfigurationRequest])
def get_all_configurations(db: Session = Depends(get_db)):
    repo = SQLAlchemyConfigurationRepository(db)
    return repo.get_all_configurations()

@app.get("/configurations/{name}", response_model=ConfigurationRequest)
def get_latest_configuration_by_name(name: str, db: Session = Depends(get_db)):
    repo = SQLAlchemyConfigurationRepository(db)
    config = repo.get_latest_configuration_by_name(name)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@app.post("/configurations", response_model=ConfigurationRequest)
def save_configuration(config: ConfigurationRequest, db: Session = Depends(get_db)):
    repo = SQLAlchemyConfigurationRepository(db)
    config_data = ConfigurationData(**config.dict())
    saved_config = repo.save(config_data)
    return saved_config

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)