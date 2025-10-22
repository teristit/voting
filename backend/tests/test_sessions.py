from flask_jwt_extended import create_access_token

def test_create_session(client, app):
    with app.app_context():
        token = create_access_token(identity=1)
    data = {"start_date": "2025-10-20", "end_date": "2025-10-26", "active": True}
    response = client.post("/api/v1/sessions/", json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

def test_get_sessions(client, app):
    with app.app_context():
        token = create_access_token(identity=1)
    response = client.get("/api/v1/sessions/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
