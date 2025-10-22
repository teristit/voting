from flask_jwt_extended import create_access_token

def test_results_access(client, app):
    with app.app_context():
        token = create_access_token(identity=1)
    response = client.get("/api/v1/results/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (200, 404)
