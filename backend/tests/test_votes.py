from flask_jwt_extended import create_access_token

def test_vote_submission(client, app):
    with app.app_context():
        token = create_access_token(identity=1)
    payload = {
        "session_id": 1,
        "votes": [
            {"target_id": 2, "score": 8},
            {"target_id": 3, "score": 9}
        ]
    }
    response = client.post("/api/v1/votes/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"
