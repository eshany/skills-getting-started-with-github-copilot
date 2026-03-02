"""
Tests for the root endpoint (GET /).
"""

def test_root_redirects_to_static(client):
    """Test that the root endpoint redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_root_redirect_with_follow(client):
    """Test that following redirect works correctly"""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()
