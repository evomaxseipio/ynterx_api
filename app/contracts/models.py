from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Adjust this import according to your database setup
# from app.database import Base  # Replace with your actual Base import

Base = declarative_base()  # Remove this line if you already have Base defined elsewhere

class Contract(Base):
    """SQLAlchemy model for storing contract records in database"""
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    client_name = Column(String, index=True)
    contract_date = Column(String)
    amount = Column(String)
    description = Column(Text)
    template_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    original_data = Column(Text)  # Store the complete JSON data as string
    file_size = Column(Integer)  # File size in bytes

    def __repr__(self):
        return f"<Contract(id={self.id}, filename='{self.filename}', client='{self.client_name}')>"

class Template(Base):
    """SQLAlchemy model for storing template information"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(String, default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)  # Track how many times template was used

    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', filename='{self.filename}')>"
