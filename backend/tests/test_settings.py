from flask_jwt_extended import create_access_token

def test_update_setting(client, app):
    with app.app_context():
        token = create_access_token(identity=1)
    data = {"value": {"enabled": True}}
    response = client.patch("/api/v1/settings/notifications_enabled", json=data,
                            headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"
