from fastapi.testclient import TestClient
from app.main import app
import pytest
import uuid

client = TestClient(app)

def test_full_document_lifecycle():
    """Test: Create User -> Create Document -> Retrieve Document."""
    
    # Generate a unique email so we don't hit "Email already registered" errors
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Test User {unique_id}",
        "email": f"test-{unique_id}@example.com",
        "password": "securepassword123"
    }
    
    # 1. Create a User
    user_res = client.post("/users/", json=user_data)
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    # 2. Create a Document
    doc_res = client.post(f"/documents/?owner_id={user_id}", json={"title": "My Test Doc"})
    assert doc_res.status_code == 200
    doc_id = doc_res.json()["id"]

    # 3. Retrieve the Document
    get_res = client.get(f"/documents/{doc_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == doc_id
    assert data["revision"] == 0

def test_404_on_missing_document():
    """Test: Ensure we get a 404 for a non-existent ID."""
    response = client.get("/documents/i-do-not-exist-at-all")
    assert response.status_code == 404
