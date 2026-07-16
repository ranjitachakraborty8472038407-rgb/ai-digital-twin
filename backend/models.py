from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    image_url = Column(String)
    defect_type = Column(String)
    severity = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
