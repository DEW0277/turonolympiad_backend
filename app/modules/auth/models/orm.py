import uuid
from app.database.base import Base
from sqlalchemy import Column, Integer, String, Boolean


class User(Base):
    __tablename__ = "users"

    id = Column(String(36),primary_key=True,default=lambda: str(uuid.uuid4()),index=True)
    
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    phone_number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)