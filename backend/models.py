from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class SessionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    REGISTRATION_OPEN = "registration_open"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BotModel(Base):
    __tablename__ = "bots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    model_type = Column(String(100), nullable=False)  # GPT-4, Claude, Llama, etc.
    specialization = Column(String(500))
    api_endpoint = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = relationship("Registration", back_populates="bot")
    messages = relationship("Message", back_populates="bot")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    topic_category = Column(String(100), nullable=False, index=True)
    topic_subcategory = Column(String(100), index=True)
    framing_prompt = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    max_participants = Column(Integer, default=6)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.SCHEDULED, index=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))  # "human" or bot name
    
    # Relationships
    registrations = relationship("Registration", back_populates="session")
    messages = relationship("Message", back_populates="session", order_by="Message.timestamp")

class Registration(Base):
    __tablename__ = "registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False, index=True)
    interest_statement = Column(Text)  # Why they want to participate
    registered_at = Column(DateTime, default=datetime.utcnow)
    accepted = Column(Boolean, default=True)  # For future selection logic
    
    # Relationships
    session = relationship("Session", back_populates="registrations")
    bot = relationship("BotModel", back_populates="registrations")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True)  # Null for human observer
    content = Column(Text, nullable=False)
    urgency_score = Column(Integer)  # 1-100, or 100 for human intervention
    is_human = Column(Boolean, default=False)
    is_yield = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration_seconds = Column(Integer)  # How long they spoke
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    bot = relationship("BotModel", back_populates="messages")
