def test_health_endpoint(client):
    """Ensure that /api/v1/health responds 200 and returns JSON {'status': 'ok'}"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
