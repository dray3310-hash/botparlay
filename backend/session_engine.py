"""
Session Engine: Manages live session state, urgency scoring, and floor control
"""
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
from collections import defaultdict

@dataclass
class UrgencyBid:
    bot_id: int
    bot_name: str
    score: int  # 1-100
    timestamp: datetime

@dataclass
class ActiveSpeaker:
    bot_id: int
    bot_name: str
    started_at: datetime
    max_duration: int = 420  # 7 minutes in seconds

class SessionEngine:
    """
    Manages the state of a live session including:
    - Urgency score collection
    - Floor assignment
    - Time tracking
    - Human intervention
    """
    
    def __init__(self, session_id: int, duration_minutes: int = 60):
        self.session_id = session_id
        self.duration_minutes = duration_minutes
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        
        # Urgency tracking
        self.urgency_bids: Dict[int, UrgencyBid] = {}  # bot_id -> UrgencyBid
        self.active_speaker: Optional[ActiveSpeaker] = None
        
        # Human observer
        self.human_intervention_used = False
        
        # Message queue for live broadcast
        self.message_queue: List[dict] = []
        
    def start_session(self):
        """Start the session timer"""
        self.started_at = datetime.utcnow()
        
    def submit_urgency(self, bot_id: int, bot_name: str, score: int) -> bool:
        """
        Bot submits urgency score.
        Returns True if accepted, False if rejected (e.g., already speaking)
        """
        if not self.started_at:
            return False
            
        if self.is_ended():
            return False
            
        if self.active_speaker and self.active_speaker.bot_id == bot_id:
            return False  # Can't bid while speaking
            
        # Validate score
        if not (1 <= score <= 100):
            return False
            
        self.urgency_bids[bot_id] = UrgencyBid(
            bot_id=bot_id,
            bot_name=bot_name,
            score=score,
            timestamp=datetime.utcnow()
        )
        
        return True
        
    def get_next_speaker(self) -> Optional[UrgencyBid]:
        """
        Get the bot with highest urgency score.
        Returns None if no bids or if someone is still speaking.
        """
        if self.active_speaker:
            # Check if speaker's time is up
            elapsed = (datetime.utcnow() - self.active_speaker.started_at).total_seconds()
            if elapsed < self.active_speaker.max_duration:
                return None  # Still speaking
            else:
                # Time's up, force release
                self.release_floor()
        
        if not self.urgency_bids:
            return None
            
        # Find highest urgency
        highest = max(self.urgency_bids.values(), key=lambda b: b.score)
        return highest
        
    def grant_floor(self, bot_id: int, bot_name: str) -> bool:
        """Grant speaking floor to a bot"""
        if self.active_speaker:
            return False
            
        if bot_id not in self.urgency_bids:
            return False
            
        self.active_speaker = ActiveSpeaker(
            bot_id=bot_id,
            bot_name=bot_name,
            started_at=datetime.utcnow()
        )
        
        # Clear urgency bids after granting floor
        self.urgency_bids.clear()
        
        return True
        
    def release_floor(self):
        """Release the speaking floor"""
        self.active_speaker = None
        
    def yield_floor(self, bot_id: int) -> bool:
        """Bot yields their speaking turn"""
        if not self.active_speaker or self.active_speaker.bot_id != bot_id:
            return False
            
        self.release_floor()
        return True
        
    def human_intervene(self) -> bool:
        """
        Human observer uses their one intervention.
        Returns True if allowed, False if already used.
        """
        if self.human_intervention_used:
            return False
            
        # Human gets urgency 100 and immediately takes floor
        self.active_speaker = ActiveSpeaker(
            bot_id=-1,  # Special ID for human
            bot_name="Human Observer",
            started_at=datetime.utcnow()
        )
        
        self.human_intervention_used = True
        self.urgency_bids.clear()  # Clear all bids
        
        return True
        
    def get_time_remaining(self) -> int:
        """Get remaining time in seconds"""
        if not self.started_at:
            return self.duration_minutes * 60
            
        elapsed = (datetime.utcnow() - self.started_at).total_seconds()
        total = self.duration_minutes * 60
        remaining = max(0, int(total - elapsed))
        
        return remaining
        
    def is_ended(self) -> bool:
        """Check if session has ended"""
        if self.ended_at:
            return True
            
        if not self.started_at:
            return False
            
        elapsed = (datetime.utcnow() - self.started_at).total_seconds()
        if elapsed >= self.duration_minutes * 60:
            self.ended_at = datetime.utcnow()
            return True
            
        return False
        
    def should_warn_time(self) -> bool:
        """Check if we should show 7-minute warning"""
        remaining = self.get_time_remaining()
        return 400 <= remaining <= 420  # Between 6:40 and 7:00 remaining
        
    def get_status(self) -> dict:
        """Get current session status for live viewers"""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "time_remaining": self.get_time_remaining(),
            "is_ended": self.is_ended(),
            "active_speaker": {
                "bot_id": self.active_speaker.bot_id,
                "bot_name": self.active_speaker.bot_name,
                "speaking_for": int((datetime.utcnow() - self.active_speaker.started_at).total_seconds())
            } if self.active_speaker else None,
            "human_intervention_available": not self.human_intervention_used,
            "participant_count": len(self.urgency_bids)
        }

# Global registry of active sessions
active_sessions: Dict[int, SessionEngine] = {}

def get_session_engine(session_id: int, duration_minutes: int = 60) -> SessionEngine:
    """Get or create a session engine"""
    if session_id not in active_sessions:
        active_sessions[session_id] = SessionEngine(session_id, duration_minutes)
    return active_sessions[session_id]
