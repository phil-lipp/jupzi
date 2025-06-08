from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from app.utils.database import Base

class Poll(Base):
    """Model for polls."""
    __tablename__ = 'polls'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    creator_id = Column(Integer, nullable=False)
    is_anonymous = Column(Boolean, default=True)
    allows_multiple_answers = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")
    votes = relationship("PollVote", back_populates="poll", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Poll(id={self.id}, title='{self.title}')>"

class PollOption(Base):
    """Model for poll options."""
    __tablename__ = 'poll_options'

    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey('polls.id'), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    poll = relationship("Poll", back_populates="options")
    votes = relationship("PollVote", back_populates="option", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PollOption(id={self.id}, text='{self.text}')>"

class PollVote(Base):
    """Model for poll votes."""
    __tablename__ = 'poll_votes'

    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey('polls.id'), nullable=False)
    option_id = Column(Integer, ForeignKey('poll_options.id'), nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    poll = relationship("Poll", back_populates="votes")
    option = relationship("PollOption", back_populates="votes")
    
    def __repr__(self):
        return f"<PollVote(id={self.id}, user_id={self.user_id})>" 