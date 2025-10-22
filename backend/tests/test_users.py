from flask_jwt_extended import create_access_token

def test_user_list(client, app):
    with app.app_context():
        token = create_access_token(identity=1)
    response = client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
