import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, default='')
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    location = Column(String)
    priority = Column(Integer, nullable=False, default=0)
    date_added = Column(DateTime, nullable=False, server_default=text("NOW()"))
    date_due = Column(DateTime, nullable=True)
    date_completed = Column(DateTime, nullable=True)
    status = Column(String)
    categories = Column(ARRAY(String))
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="tasks")


# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
