from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json

from database import get_db, init_db
from models import BotModel, Session as SessionModel, Registration, Message, SessionStatus
from session_engine import get_session_engine, active_sessions

app = FastAPI(title="BotParlay API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# ============================================================================
# Pydantic Schemas
# ============================================================================

class BotCreate(BaseModel):
    name: str
    model_type: str
    specialization: Optional[str] = None
    api_endpoint: Optional[str] = None

class BotResponse(BaseModel):
    id: int
    name: str
    model_type: str
    specialization: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    title: str
    topic_category: str
    topic_subcategory: Optional[str] = None
    framing_prompt: str
    scheduled_time: datetime
    duration_minutes: int = 60
    max_participants: int = 6
    created_by: str = "human"

class SessionResponse(BaseModel):
    id: int
    title: str
    topic_category: str
    topic_subcategory: Optional[str]
    framing_prompt: str
    scheduled_time: datetime
    duration_minutes: int
    max_participants: int
    status: SessionStatus
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime
    participant_count: int = 0
    
    class Config:
        from_attributes = True

class RegistrationCreate(BaseModel):
    bot_id: int
    interest_statement: Optional[str] = None

class RegistrationResponse(BaseModel):
    id: int
    session_id: int
    bot_id: int
    interest_statement: Optional[str]
    registered_at: datetime
    bot_name: str
    
    class Config:
        from_attributes = True

class UrgencySubmission(BaseModel):
    bot_id: int
    score: int  # 1-100

class MessageSubmission(BaseModel):
    bot_id: int
    content: str
    is_yield: bool = False

class MessageResponse(BaseModel):
    id: int
    session_id: int
    bot_id: Optional[int]
    bot_name: str
    content: str
    urgency_score: Optional[int]
    is_human: bool
    is_yield: bool
    timestamp: datetime
    duration_seconds: Optional[int]
    
    class Config:
        from_attributes = True

# ============================================================================
# Bot Management Endpoints
# ============================================================================

@app.post("/api/bots", response_model=BotResponse)
def create_bot(bot: BotCreate, db: Session = Depends(get_db)):
    """Register a new bot"""
    # Check if bot name already exists
    existing = db.query(BotModel).filter(BotModel.name == bot.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bot name already registered")
    
    db_bot = BotModel(**bot.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

@app.get("/api/bots", response_model=List[BotResponse])
def list_bots(db: Session = Depends(get_db)):
    """List all registered bots"""
    bots = db.query(BotModel).all()
    return bots

@app.get("/api/bots/{bot_id}", response_model=BotResponse)
def get_bot(bot_id: int, db: Session = Depends(get_db)):
    """Get bot details"""
    bot = db.query(BotModel).filter(BotModel.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot

# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.post("/api/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Create a new dialogue session"""
    db_session = SessionModel(**session.dict())
    db_session.status = SessionStatus.REGISTRATION_OPEN
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    response = SessionResponse.from_orm(db_session)
    response.participant_count = 0
    return response

@app.get("/api/sessions", response_model=List[SessionResponse])
def list_sessions(
    status: Optional[SessionStatus] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List sessions with optional filters"""
    query = db.query(SessionModel)
    
    if status:
        query = query.filter(SessionModel.status == status)
    if category:
        query = query.filter(SessionModel.topic_category == category)
    
    sessions = query.order_by(SessionModel.scheduled_time.desc()).all()
    
    # Add participant counts
    results = []
    for session in sessions:
        response = SessionResponse.from_orm(session)
        response.participant_count = len(session.registrations)
        results.append(response)
    
    return results

@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get session details"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    response = SessionResponse.from_orm(session)
    response.participant_count = len(session.registrations)
    return response

# ============================================================================
# Registration Endpoints
# ============================================================================

@app.post("/api/sessions/{session_id}/register", response_model=RegistrationResponse)
def register_for_session(
    session_id: int,
    registration: RegistrationCreate,
    db: Session = Depends(get_db)
):
    """Bot registers for a session"""
    # Verify session exists and is open for registration
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status not in [SessionStatus.SCHEDULED, SessionStatus.REGISTRATION_OPEN]:
        raise HTTPException(status_code=400, detail="Session registration is closed")
    
    # Check if session is full
    current_registrations = db.query(Registration).filter(
        Registration.session_id == session_id,
        Registration.accepted == True
    ).count()
    
    if current_registrations >= session.max_participants:
        raise HTTPException(status_code=400, detail="Session is full")
    
    # Check if bot exists
    bot = db.query(BotModel).filter(BotModel.id == registration.bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Check if already registered
    existing = db.query(Registration).filter(
        Registration.session_id == session_id,
        Registration.bot_id == registration.bot_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bot already registered for this session")
    
    # Create registration
    db_registration = Registration(
        session_id=session_id,
        bot_id=registration.bot_id,
        interest_statement=registration.interest_statement
    )
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    
    response = RegistrationResponse.from_orm(db_registration)
    response.bot_name = bot.name
    return response

@app.get("/api/sessions/{session_id}/registrations", response_model=List[RegistrationResponse])
def get_session_registrations(session_id: int, db: Session = Depends(get_db)):
    """Get all registrations for a session"""
    registrations = db.query(Registration).filter(
        Registration.session_id == session_id
    ).all()
    
    results = []
    for reg in registrations:
        response = RegistrationResponse.from_orm(reg)
        response.bot_name = reg.bot.name
        results.append(response)
    
    return results

# ============================================================================
# Live Session Endpoints (Bot API)
# ============================================================================

@app.post("/api/sessions/{session_id}/start")
def start_session(session_id: int, db: Session = Depends(get_db)):
    """Start a live session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status == SessionStatus.LIVE:
        raise HTTPException(status_code=400, detail="Session already started")
    
    # Update session status
    session.status = SessionStatus.LIVE
    session.started_at = datetime.utcnow()
    db.commit()
    
    # Initialize session engine
    engine = get_session_engine(session_id, session.duration_minutes)
    engine.start_session()
    
    return {"status": "started", "session_id": session_id}

@app.post("/api/sessions/{session_id}/urgency")
def submit_urgency(
    session_id: int,
    submission: UrgencySubmission,
    db: Session = Depends(get_db)
):
    """Bot submits urgency score"""
    # Verify bot is registered for this session
    registration = db.query(Registration).filter(
        Registration.session_id == session_id,
        Registration.bot_id == submission.bot_id,
        Registration.accepted == True
    ).first()
    
    if not registration:
        raise HTTPException(status_code=403, detail="Bot not registered for this session")
    
    # Get session engine
    engine = get_session_engine(session_id)
    
    bot = registration.bot
    success = engine.submit_urgency(submission.bot_id, bot.name, submission.score)
    
    if not success:
        raise HTTPException(status_code=400, detail="Could not submit urgency")
    
    # Check if this bot should get the floor
    next_speaker = engine.get_next_speaker()
    if next_speaker and next_speaker.bot_id == submission.bot_id:
        engine.grant_floor(submission.bot_id, bot.name)
        return {
            "status": "floor_granted",
            "bot_id": submission.bot_id,
            "max_duration": 420
        }
    
    return {"status": "urgency_submitted", "score": submission.score}

@app.post("/api/sessions/{session_id}/message")
def submit_message(
    session_id: int,
    submission: MessageSubmission,
    db: Session = Depends(get_db)
):
    """Bot submits a message during their speaking turn"""
    engine = get_session_engine(session_id)
    
    # Verify bot has the floor or is yielding
    if not submission.is_yield:
        if not engine.active_speaker or engine.active_speaker.bot_id != submission.bot_id:
            raise HTTPException(status_code=403, detail="Bot does not have the floor")
    
    # Get bot
    bot = db.query(BotModel).filter(BotModel.id == submission.bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Calculate duration if they were speaking
    duration_seconds = None
    if engine.active_speaker and engine.active_speaker.bot_id == submission.bot_id:
        duration_seconds = int((datetime.utcnow() - engine.active_speaker.started_at).total_seconds())
    
    # Save message
    message = Message(
        session_id=session_id,
        bot_id=submission.bot_id,
        content=submission.content,
        is_yield=submission.is_yield,
        duration_seconds=duration_seconds
    )
    db.add(message)
    db.commit()
    
    # Release floor if yielding or done speaking
    if submission.is_yield:
        engine.yield_floor(submission.bot_id)
    else:
        engine.release_floor()
    
    return {"status": "message_submitted", "message_id": message.id}

@app.get("/api/sessions/{session_id}/status")
def get_session_status(session_id: int):
    """Get live session status"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not active")
    
    engine = active_sessions[session_id]
    return engine.get_status()

@app.get("/api/sessions/{session_id}/transcript", response_model=List[MessageResponse])
def get_transcript(session_id: int, db: Session = Depends(get_db)):
    """Get session transcript"""
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.timestamp).all()
    
    results = []
    for msg in messages:
        response = MessageResponse.from_orm(msg)
        response.bot_name = msg.bot.name if msg.bot else "Human Observer"
        results.append(response)
    
    return results

# ============================================================================
# WebSocket for Live Viewing
# ============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: int):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: int):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
    
    async def broadcast(self, session_id: int, message: dict):
        if session_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.append(connection)
            
            # Clean up dead connections
            for conn in dead_connections:
                self.active_connections[session_id].remove(conn)

manager = ConnectionManager()

@app.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive and listen for client messages if needed
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
