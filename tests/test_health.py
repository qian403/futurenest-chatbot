import json


def test_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data.get('status') == 'ok'
