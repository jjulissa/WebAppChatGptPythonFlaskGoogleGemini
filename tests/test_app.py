# tests/test_app.py 

import os
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register(client):
    response = client.post('/auth/register', json={
        "email": "test@example.com",
        "password": "test123"
    })
    assert response.status_code == 201

def test_login(client):
    response = client.post('/auth/login', json={
        "email": "test@example.com",
        "password": "test123"
    })
    assert response.status_code == 200

def test_send_without_token(client):
    response = client.post('/chat/send', json={"content": "Hola"})
    assert response.status_code == 401  # No JWT, debe rechazar
