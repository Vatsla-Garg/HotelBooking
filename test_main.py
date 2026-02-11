from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import DbUser, DbHotel,DbHotelManager
from main import app
import random
from db.database import Base, get_db

#In-memory SQLite for tests
#1)setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # file-based SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables in the test DB
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
    response = client.post("/token",
    data = {"username": "malak@gmail.com", "password": "Azerty@123"})
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