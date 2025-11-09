from sqlalchemy import Column, String, Text, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.db import Base

class Note(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)
    meta = Column("metadata", JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
