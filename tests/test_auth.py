import pytest
from run import app, seed


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        seed()
        yield client


def test_login_get(client):
    r = client.get("/login")
    assert r.status_code == 200


def test_login_correcto(client):
    r = client.post("/login", data={"username": "admin", "password": "admin123"},
                    follow_redirects=False)
    assert r.status_code == 302
    assert "/activos/dashboard" in r.headers["Location"]


def test_login_incorrecto(client):
    r = client.post("/login", data={"username": "admin", "password": "mala"},
                    follow_redirects=True)
    assert r.status_code == 200
    assert "incorrectos" in r.data.decode()


def test_redirige_sin_sesion(client):
    r = client.get("/activos/dashboard", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]
