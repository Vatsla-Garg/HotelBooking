import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.enums import Role
from db.hash import Hash
from db.models import DbUser
from main import app
from datetime import date, timedelta
from db.database import Base, get_db, SessionLocal, engine

#In-memory SQLite for tests
#1)setup test DB
# Test database in memory
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}).connect()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Replace engine globally
engine.dispose()
engine = test_engine
SessionLocal.configure(bind=test_engine)

# Recreate tables in test DB
Base.metadata.drop_all(bind=test_engine)
Base.metadata.create_all(bind=test_engine)

#2) override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db # This affects only FastAPI dependency injection

#Create TestClient
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def _ensure_user(email: str, username: str, password: str, role: str):
    response = client.post(
        "/user/",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": role,
        },
    )
    assert response.status_code in (200, 400)

    login_response = client.post("/token", data={"username": email, "password": password})
    assert login_response.status_code == 200
    return login_response.json().get("access_token")

@pytest.fixture
def guest_login():
    return _ensure_user(
        email="guest@gmail.com",
        username="guest",
        password="Azerty@123",
        role="GUEST",
    )

@pytest.fixture
def manager_login():
    return _ensure_user(
        email="manager@gmail.com",
        username="Manager",
        password="Azerty@123",
        role="HOTEL_MANAGER",
    )

@pytest.fixture
def admin_login():
    db = TestingSessionLocal()
    admin = db.query(DbUser).filter(DbUser.email == "admin@gmail.com").first()
    if not admin:
        admin = DbUser(
            role=Role.ADMIN,
            email="admin@gmail.com",
            password=Hash.bcrypt("Azerty@123"),
            username="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    response = client.post("/token", data={"username": admin.email, "password": "Azerty@123"})
    return response.json().get("access_token")

@pytest.fixture
def create_features(admin_login):
    token = admin_login
    response = client.post(
                "/features/",
                json={
                    "feature": "Wifi"
                },
                headers={"Authorization": f"Bearer {token}"}
                )
    assert response.status_code == 201
    return response.json()["id"]

@pytest.fixture
def create_hotel(manager_login, create_features):
    token = manager_login
    feature_id = create_features
    response = client.post(
        "/hotel/",
        json={
            "hotel_name": "HolidayInn",
            "description": "friendly",
            "phone_number": "+21623228230",
            "street_name": "Boterbloem straat",
            "city": "weert",
            "country": "netherlands",
            "postcode": "116 CD",
            "feature_ids": [feature_id]
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    return response, token


@pytest.fixture
def create_rooms_for_hotel(create_hotel):
    response, token = create_hotel
    pass


@pytest.fixture
def create_hotel_and_room(create_hotel):
    hotel_response, token = create_hotel
    assert hotel_response.status_code == 201
    hotel_id = hotel_response.json()["id"]

    room_response = client.post(
        "/room/",
        json={
            "hotel_id": hotel_id,
            "room_number": "101",
            "room_type": "double",
            "price_per_night": 120.0,
            "available": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert room_response.status_code == 200
    room_id = room_response.json()["id"]
    return hotel_id, room_id

@pytest.fixture
def guest2_login():
    return _ensure_user(
        email="guest2@gmail.com",
        username="guest2",
        password="Azerty@123",
        role="GUEST",
    )

def test_admin_created_on_startup():
    with TestClient(app):  # triggers startup event
        db = TestingSessionLocal()
        try:
            admin = db.query(DbUser).filter(DbUser.role == Role.ADMIN).first()
            assert admin is not None
            assert admin.email == "admin@gmail.com"
            assert admin.username == "admin"
        finally:
            db.close()

def test_admin_login(admin_login):
    response = admin_login
    assert response is not None

def test_auth_error():
    response = client.post("/token",
    data = {"username": "", "password": ""})
    access_token = response.json().get("access_token")
    assert access_token is None
    # data is used because it's a form data
    #message = response.json().get("detail")[0].get("msg")
    #assert message == "field required"


# Features tests
def test_add_feature(create_features):
    feature_id = create_features
    assert feature_id > 0

# Booking tests
def test_post_hotel(create_hotel):
    response, token = create_hotel
    assert response.status_code == 201

def test_get_hotels(create_hotel):
    response, token = create_hotel
    assert response.status_code == 201
    response = client.get("/hotel/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_get_hotels_by_manager(create_hotel):
    response, token = create_hotel
    response = client.get(
        "/hotel/hotels-by-manager",
    headers={
            "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200

def test_get_hotel_by_id(create_hotel):
    hotel_id = 1
    response = client.get(f"/hotel/{hotel_id}")
    assert response.status_code == 200

def test_update_hotel(create_hotel):
    response, token = create_hotel
    assert response.status_code == 201
    payload = {"hotel_name": "New Hotel Name"}
    hotel_id = 1
    response = client.patch(
        f"/hotel/{hotel_id}",
        json = payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json().get("hotel_name") == "New Hotel Name"

def test_rate_hotel(create_hotel, guest_login):
    response, token = create_hotel
    assert response.status_code == 201
    token = guest_login
    payload = {"rate": 5}
    hotel_id = 1
    response = client.patch(
        f"/hotel/rate/{hotel_id}",
        json = payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json().get("rating_sum") == 5
    assert response.json().get("rating_count") == 1
    response = client.get(f"/hotel/rating/{hotel_id}")
    assert response.status_code == 200

def test_delete_hotel():
    pass

# Booking tests
def test_booking_requires_authentication(create_hotel_and_room):
    hotel_id, room_id = create_hotel_and_room
    checkin = date.today() + timedelta(days=3)
    checkout = date.today() + timedelta(days=5)
    response = client.post(
        "/booking/",
        json={
            "hotel_id": hotel_id,
            "room_id": room_id,
            "checkin_date": checkin.isoformat(),
            "checkout_date": checkout.isoformat(),
            "person_number": 1,
            "room_count": 1
        }
    )
    assert response.status_code == 401

def test_booking_rejects_non_guest(create_hotel_and_room, manager_login):
    hotel_id, room_id = create_hotel_and_room
    manager_token = manager_login
    checkin = date.today() + timedelta(days=3)
    checkout = date.today() + timedelta(days=5)
    response = client.post(
        "/booking/",
        json={
            "hotel_id": hotel_id,
            "room_id": room_id,
            "checkin_date": checkin.isoformat(),
            "checkout_date": checkout.isoformat(),
            "person_number": 1,
            "room_count": 1
        },
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 403

def test_booking_overlap_rejected(create_hotel_and_room, guest_login):
    hotel_id, room_id = create_hotel_and_room
    guest_token = guest_login
    first_checkin = date.today() + timedelta(days=7)
    first_checkout = date.today() + timedelta(days=10)
    first_response = client.post(
        "/booking/",
        json={
            "hotel_id": hotel_id,
            "room_id": room_id,
            "checkin_date": first_checkin.isoformat(),
            "checkout_date": first_checkout.isoformat(),
            "person_number": 2,
            "room_count": 1
        },
        headers={"Authorization": f"Bearer {guest_token}"}
    )
    assert first_response.status_code == 200

    overlap_response = client.post(
        "/booking/",
        json={
            "hotel_id": hotel_id,
            "room_id": room_id,
            "checkin_date": (date.today() + timedelta(days=8)).isoformat(),
            "checkout_date": (date.today() + timedelta(days=11)).isoformat(),
            "person_number": 2,
            "room_count": 1
        },
        headers={"Authorization": f"Bearer {guest_token}"}
    )
    assert overlap_response.status_code == 400
    assert "overlap" in overlap_response.json().get("detail", "").lower()

def test_booking_status_confirmed_and_total_price(create_hotel_and_room, guest_login):
    hotel_id, room_id = create_hotel_and_room
    guest_token = guest_login
    checkin = date.today() + timedelta(days=12)
    checkout = date.today() + timedelta(days=15)
    response = client.post(
        "/booking/",
        json={
            "hotel_id": hotel_id,
            "room_id": room_id,
            "checkin_date": checkin.isoformat(),
            "checkout_date": checkout.isoformat(),
            "person_number": 2,
            "room_count": 2
        },
        headers={"Authorization": f"Bearer {guest_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["booking_status"] == "CONFIRMED"
    # 3 nights * 120.0 price_per_night * 2 rooms
    assert data["total_price"] == 360.0

def test_booking_checkin_in_past_rejected(create_hotel_and_room, guest_login):
    token = guest_login
    hotel_id, room_id = create_hotel_and_room

    res = client.post(
        "/booking/",
        json={
            "hotel_id": hotel_id,
            "room_id": room_id,
            "checkin_date": (date.today() - timedelta(days=1)).isoformat(),
            "checkout_date": (date.today() + timedelta(days=2)).isoformat(),
            "person_number": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 400
    assert "today" in res.json().get("detail", "").lower()

def test_guest_cannot_delete_other_users_booking(create_hotel_and_room, guest_login, guest2_login):
    hotel_id, room_id = create_hotel_and_room

    # guest1 creates booking
    g1 = guest_login
    create_res = client.post(
        "/booking/",
        json={
            "hotel_id": hotel_id,
            "room_id": room_id,
            "checkin_date": (date.today() + timedelta(days=3)).isoformat(),
            "checkout_date": (date.today() + timedelta(days=5)).isoformat(),
            "person_number": 1,
        },
        headers={"Authorization": f"Bearer {g1}"},
    )
    assert create_res.status_code == 200
    booking_id = create_res.json()["id"]

    # guest2 tries delete
    g2 = guest2_login
    del_res = client.delete(f"/booking/{booking_id}", headers={"Authorization": f"Bearer {g2}"})
    assert del_res.status_code == 404