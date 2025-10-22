# backend/tests/test_auth.py
import pytest
from backend.services import telegram_auth  # убедись, что путь корректный

def test_dummy(client, monkeypatch):
    # Патчинг функции, которую реально вызывает код API
    monkeypatch.setattr(telegram_auth, "verify_telegram_init_data",
                        lambda x: {"id": 1, "first_name": "T"})
    
    r = client.post("/api/v1/auth/telegram", json={"init_data": "fake"})
    assert r.status_code == 200
