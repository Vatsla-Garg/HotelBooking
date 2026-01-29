# HotelBooking
HotelBooking is a FastAPI-based backend application for managing hotel bookings.  
It provides APIs for handling hotels, rooms, and reservations.

# Tech Stack
- python 3.14
- FastAPI
- uvicorn
- Git & GitHub

# Project Structure

# Git workflow
- **main**: production ready code
- **develop**: integration branch
- **feature/***: Feature specific branch

# Setup instructions
`1.`Clone the repository:  git clone git@github.com:Vatsla-Garg/HotelBooking.git
   ```bash
   git clone git@github.com:Vatsla-Garg/HotelBooking.git
   ```
`2.`Navigate to the project directory: cd HotelBooking
   ```bash
   cd HotelBooking
   ```
`3.`Install dependencies: pip install -r requirements.txt
   ```bash
   pip install -r requirements.txt
   ```
`4.`Run the server: 
   ```bash
  uvicorn main:app --reload
   ```

`5.`Open API docs: Swagger UI: http://127.0.0.1:8000/docs
