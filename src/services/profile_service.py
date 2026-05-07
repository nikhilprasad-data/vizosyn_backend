from fastapi import HTTPException, status
from src.models import Location
     
def get_location_id(user_location: dict, db):
     """Retrieves an existing location ID or creates a new location record."""
     
     city      = user_location.get("city")
     state     = user_location.get("state")

     existing_location = db.query(Location).filter(Location.city == city,Location.state == state).first()

     if existing_location:
          return existing_location.id
     
     new_location   = Location(
          city      = city,
          state     = state 
     )

     try:
          db.add(new_location)
          db.commit()
          db.refresh(new_location)
          return new_location.id
     
     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error"   
          )