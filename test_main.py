from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import DbUser, DbHotel, DbHotelManager, DbRoom
from main import app
import random
from datetime import date, timedelta
from db.database import Base, get_db

#In-memory SQLite for tests
#1)setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # file-based SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Recreate tables in test DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

#2) override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

#Create TestClient
client = TestClient(app)

def login():
    email = "malak@gmail.com"
    password = "Azerty@123"
    response = client.post("/token", data={"username": email, "password": password})
    token = response.json().get("access_token")
    if token:
        return token

    create_response = client.post(
        "/user/",
        json={
            "username": "Malak",
            "email": email,
            "password": password,
            "role": "HOTEL_MANAGER"
        }
    )
    assert create_response.status_code == 200
    response = client.post("/token", data={"username": email, "password": password})
    return response.json().get("access_token")

def generate_random_hotel_name():
    hotel_names=["Radisson", "IBIS", "HolidayInn"]
    rand_index = random.randint(0, len(hotel_names)-1)
    rand_int = random.randint(1, 100)
    hotel = hotel_names[rand_index]+str(rand_int)
    return hotel

def generate_random_email():
    email = "malak"+ str(random.randint(1, 100))+"@gmail.com"
    return email

def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}

def create_user_and_login(role: str):
    email = f"{role.lower()}_{random.randint(1000,999999)}@example.com"
    password = "Azerty@123"
    create_response = client.post(
        "/user/",
        json={
            "username": role.lower(),
            "email": email,
            "password": password,
            "role": role
        }
    )
    assert create_response.status_code == 200
    login_response = client.post(
        "/token",
        data={"username": email, "password": password}
    )
    assert login_response.status_code == 200
    return create_response.json(), login_response.json()["access_token"]

def create_hotel_and_room():
    _, manager_token = create_user_and_login("HOTEL_MANAGER")
    hotel_name = generate_random_hotel_name()
    hotel_response = client.post(
        "/hotel/",
        json={
            "hotel_name": hotel_name,
            "description": "friendly",
            "phone_number": "+21623228230",
            "street_name": "Boterbloem straat",
            "city": "weert",
            "country": "netherlands",
            "postcode": "116 cd"
        },
        headers=auth_headers(manager_token)
    )
    assert hotel_response.status_code == 200
    hotel_id = hotel_response.json()["id"]

    db = TestingSessionLocal()
    try:
        room = DbRoom(
            hotel_id=hotel_id,
            room_number=f"R-{random.randint(100, 999)}",
            room_type="STANDARD",
            price_per_night=120.0,
            is_active=True
        )
        db.add(room)
        db.commit()
        db.refresh(room)
        return hotel_id, room.id
    finally:
        db.close()

def test_create_hotel_manager():
    email = generate_random_email()
    response = client.post(
        "/user/",
        json={
                "username": "Malak",
                "email": email,
                "password": "Azerty@123",
                "role": "HOTEL_MANAGER"
        }
    )
    assert response.status_code == 200

def test_get_hotels():
    response = client.get("/hotel/")
    assert response.status_code == 200

def test_auth_error():
    response = client.post("/token",
    data = {"username": "", "password": ""})
    access_token = response.json().get("access_token")
    assert access_token is None
    # data is used because it's a form data
    #message = response.json().get("detail")[0].get("msg")
    #assert message == "field required"

def test_auth_success():
    token = login()
    assert token is not None

def test_post_hotel():
    token = login()
    hotel_name = generate_random_hotel_name()
    response = client.post(
        "/hotel/",
        json={
            "hotel_name": hotel_name,
            "description": "friendly",
            "phone_number": "+21623228230",
            "street_name": "Boterbloem straat",
            "city": "weert",
            "country": "netherlands",
            "postcode": "116 cd"
    },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    #assert response.json()["hotel_name"] == hotel_name

def test_get_hotels_by_manager():
    token = login()
    response = client.get(
        "/hotel/hotels-by-manager",
    headers={
            "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
def test_get_hotel_by_id():
    hotel_id = 1
    response = client.get(f"/hotel/{hotel_id}")
    assert response.status_code == 200
def test_update_hotel():
    payload = {"hotel_name": "New Hotel Name"}
    hotel_id = 1
    response = client.patch(
        f"/hotel/{hotel_id}",
        json = payload
    )
    assert response.status_code == 200
    assert response.json().get("hotel_name") == "New Hotel Name"

def test_rate_hotel():
    payload = {"rate": 5}
    hotel_id = 1
    response = client.patch(
        f"/hotel/rate/{hotel_id}",
        json = payload
    )
    assert response.status_code == 200
    #assert response.json().get("rating_sum") == 5
    #assert response.json().get("rating_count") == 1

def test_get_hotel_rates():
    hotel_id = 1
    response = client.get(f"/hotel/rating/{hotel_id}")
    assert response.status_code == 200

def test_delete_hotel():
    pass

def test_booking_requires_authentication():
    hotel_id, room_id = create_hotel_and_room()
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

def test_booking_rejects_non_guest():
    hotel_id, room_id = create_hotel_and_room()
    _, manager_token = create_user_and_login("HOTEL_MANAGER")
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
        headers=auth_headers(manager_token)
    )
    assert response.status_code == 403

def test_booking_overlap_rejected():
    hotel_id, room_id = create_hotel_and_room()
    _, guest_token = create_user_and_login("GUEST")
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
        headers=auth_headers(guest_token)
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
        headers=auth_headers(guest_token)
    )
    assert overlap_response.status_code == 400
    assert "overlap" in overlap_response.json().get("detail", "").lower()

def test_booking_status_confirmed_and_total_price():
    hotel_id, room_id = create_hotel_and_room()
    _, guest_token = create_user_and_login("GUEST")
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
        headers=auth_headers(guest_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["booking_status"] == "CONFIRMED"
    # 3 nights * 120.0 price_per_night * 2 rooms
    assert data["total_price"] == 720.0
