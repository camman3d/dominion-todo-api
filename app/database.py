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
    salt = Column(String)
    is_admin = Column(Boolean, default=False)

    # One-to-many relationship: one user can have many tasks
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    credit_transactions = relationship("CreditTransaction", back_populates="user", cascade="all, delete-orphan")

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
    prompts = relationship("TaskPrompt", back_populates="task", cascade="all, delete-orphan")

class AIPrompt(Base):
    __tablename__ = 'ai_prompts'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    cost = Column(Integer)
    prompt_template = Column(String)
    returns_json = Column(Boolean, default=False)

    task_prompts = relationship("TaskPrompt", back_populates="ai_prompt", cascade="all, delete-orphan")

class TaskPrompt(Base):
    __tablename__ = 'task_prompts'
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    ai_prompt_id = Column(Integer, ForeignKey('ai_prompts.id'))
    date_added = Column(DateTime, nullable=False, server_default=text("NOW()"))
    result = Column(String)

    task = relationship("Task", back_populates="prompts")
    ai_prompt = relationship("AIPrompt", back_populates="task_prompts")
    credit_transaction = relationship("CreditTransaction", back_populates="task_prompt", uselist=False)

class CreditTransaction(Base):
    __tablename__ = 'credit_transactions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer, nullable=False)  # Positive for purchases, negative for usage
    date = Column(DateTime, nullable=False, server_default=text("NOW()"))
    stripe_payment_id = Column(String, nullable=True)  # Only for purchases
    task_prompt_id = Column(Integer, ForeignKey('task_prompts.id'), nullable=True)  # Only for usage

    user = relationship("User", back_populates="credit_transactions")
    task_prompt = relationship("TaskPrompt", back_populates="credit_transaction")


# Create tables
# Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
