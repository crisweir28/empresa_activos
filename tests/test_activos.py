import pytest
from run import app, seed


@pytest.fixture
def auth_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        seed()
        client.post("/login", data={"username": "admin", "password": "admin123"})
        yield client


def test_dashboard(auth_client):
    r = auth_client.get("/activos/dashboard")
    assert r.status_code == 200


def test_lista_activos(auth_client):
    r = auth_client.get("/activos/")
    assert r.status_code == 200


def test_crear_activo(auth_client):
    r = auth_client.post("/activos/nuevo", data={
        "nombre": "Teclado Test",
        "categoria": "equipo",
        "estado": "activo",
        "valor": "500",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert "Teclado Test" in r.data.decode()


def test_api_activos(auth_client):
    r = auth_client.get("/activos/api")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
