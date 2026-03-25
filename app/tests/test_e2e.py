from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_end_to_end_flow():
    # Login seeded buyer/seller
    buyer_login = client.post("/api/auth/login", json={"email": "noah@usj.edu", "password": "Password123!"})
    assert buyer_login.status_code == 200
    buyer_token = buyer_login.json()["access_token"]

    seller_login = client.post("/api/auth/login", json={"email": "jane@usj.edu", "password": "Password123!"})
    assert seller_login.status_code == 200
    seller_token = seller_login.json()["access_token"]

    # Seller creates listing
    create_listing = client.post(
        "/api/listings",
        headers={"Authorization": f"Bearer {seller_token}"},
        json={"textbook_id": 2, "condition": "good", "price": 33.0, "description": "minor highlights"},
    )
    assert create_listing.status_code == 200
    listing_id = create_listing.json()["id"]

    # Buyer searches listings
    search = client.get("/api/listings", params={"max_price": 60})
    assert search.status_code == 200
    assert any(item["id"] == listing_id for item in search.json())

    # Buyer gets recommendations
    recs = client.get("/api/matches/recommendations", headers={"Authorization": f"Bearer {buyer_token}"})
    assert recs.status_code == 200
    assert isinstance(recs.json(), list)

    # Buyer starts conversation and sends message
    convo = client.post(
        "/api/conversations",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={"listing_id": listing_id},
    )
    assert convo.status_code == 200
    convo_id = convo.json()["id"]

    send = client.post(
        f"/api/conversations/{convo_id}/messages",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={"content": "Can we meet tomorrow on campus?"},
    )
    assert send.status_code == 200

    # Seller reads messages history
    history = client.get(f"/api/conversations/{convo_id}/messages", headers={"Authorization": f"Bearer {seller_token}"})
    assert history.status_code == 200
    assert len(history.json()) >= 2
