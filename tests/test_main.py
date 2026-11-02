from fastapi.testclient import TestClient
from pathlib import Path
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(str(Path(__file__).resolve().parents[1]))

from database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_inventory.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_crud_items():
    create_response = client.post(
        "/items/",
        json={"name": "Keyboard", "description": "Mechanical", "quantity": 10},
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["name"] == "Keyboard"
    assert created["description"] == "Mechanical"
    assert created["quantity"] == 10

    item_id = created["id"]

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == item_id

    update_response = client.put(
        f"/items/{item_id}",
        json={"name": "Keyboard Pro", "description": "Hot-swappable", "quantity": 8},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Keyboard Pro"
    assert updated["quantity"] == 8

    list_response = client.get("/items/")
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 1

    delete_response = client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Item deleted"

    missing_response = client.get(f"/items/{item_id}")
    assert missing_response.status_code == 404
