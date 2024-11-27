import pytest
from fastapi.testclient import TestClient
from app import app, get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

def test_get_all_configurations(client):
    response = client.get("/configurations")
    assert response.status_code == 200
    assert response.json() == []

def test_save_configuration(client):
    config_data = {
        "name": "test_config",
        "label": "Test Configuration",
        "account_types": [],
        "tenant_name": "test_tenant"
    }
    response = client.post("/configurations", json=config_data)
    assert response.status_code == 200
    assert response.json()["name"] == "test_config"

def test_get_latest_configuration_by_name(client):
    config_data = {
        "name": "test_config",
        "label": "Test Configuration",
        "account_types": [],
        "tenant_name": "test_tenant"
    }
    client.post("/configurations", json=config_data)
    response = client.get("/configurations/test_config")
    assert response.status_code == 200
    assert response.json()["name"] == "test_config"