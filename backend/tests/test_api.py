"""API-level tests via TestClient (offline: fake retrieval + mock LLM)."""

from tests.conftest import AUTH


# --- auth ---
def test_requires_auth(client):
    assert client.get("/patients").status_code == 403


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in {"healthy", "degraded"}


# --- patients ---
def _create_patient(client, name="John Doe"):
    return client.post(
        "/patients",
        headers=AUTH,
        json={"name": name, "date_of_birth": "1980-06-15", "gender": "male"},
    )


def test_patient_crud_and_search(client):
    r = _create_patient(client, "Alice Smith")
    assert r.status_code == 201
    pid = r.json()["patient_id"]

    assert client.get(f"/patients/{pid}", headers=AUTH).status_code == 200
    assert client.get("/patients/NOPE", headers=AUTH).status_code == 404

    listing = client.get("/patients", headers=AUTH, params={"search": "Alice"}).json()
    assert listing["total"] >= 1
    assert any(p["patient_id"] == pid for p in listing["results"])


# --- validation ---
def test_vitals_validation_422(client):
    pid = _create_patient(client).json()["patient_id"]
    r = client.post(
        "/consultations",
        headers=AUTH,
        json={
            "patient_id": pid,
            "chief_complaint": "headache",
            "vital_signs": {
                "blood_pressure": "999/999",
                "heart_rate": 80,
                "temperature_celsius": 37.0,
                "respiratory_rate": 16,
                "oxygen_saturation": 98,
            },
        },
    )
    assert r.status_code == 422


# --- consultation (RAG) ---
def test_consultation_happy_path(client):
    pid = _create_patient(client).json()["patient_id"]
    r = client.post(
        "/consultations",
        headers=AUTH,
        json={"patient_id": pid, "chief_complaint": "Persistent headache and fever"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["sources"], "expected retrieved sources"
    assert body["sources"][0]["credibility"] == "peer_reviewed"
    assert "disclaimer" in body


def test_consultation_unknown_patient_404(client):
    r = client.post(
        "/consultations",
        headers=AUTH,
        json={"patient_id": "P-NOPE", "chief_complaint": "fever and cough"},
    )
    assert r.status_code == 404


def test_consultation_never_500_on_llm_error(client_broken_llm):
    """Even if the LLM blows up, the consultation degrades gracefully (201)."""
    pid = _create_patient(client_broken_llm).json()["patient_id"]
    r = client_broken_llm.post(
        "/consultations",
        headers=AUTH,
        json={"patient_id": pid, "chief_complaint": "chest pain"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["sources"], "degraded response should still include sources"
    assert any("error" in n.lower() or "unavailable" in n.lower() for n in body["uncertainty_notes"])


# --- knowledge search ---
def test_knowledge_search(client):
    r = client.post(
        "/knowledge/search",
        headers=AUTH,
        json={"query": "fever headache neck stiffness", "top_k": 3},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["documents"]
    assert body["documents"][0]["credibility"] == "peer_reviewed"
