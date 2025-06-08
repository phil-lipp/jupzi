import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.calendar_events import CalendarEvent
from app.models.polls import Poll, PollOption, PollVote
from app.models.jobs import Job, JobMetadata

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    # Create tables
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

def test_calendar_event_creation(db_session):
    # Create a job
    job = Job(
        name="Test Job",
        type="calendar",
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(job)
    db_session.commit()

    # Create a calendar event
    event = CalendarEvent(
        title="Test Event",
        description="Test Description",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=1),
        location="Test Location",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        job_id=job.id
    )
    db_session.add(event)
    db_session.commit()

    # Query the event
    saved_event = db_session.query(CalendarEvent).first()
    assert saved_event.title == "Test Event"
    assert saved_event.description == "Test Description"
    assert saved_event.job_id == job.id

def test_calendar_event_validation(db_session):
    # Test invalid date range
    with pytest.raises(ValueError):
        event = CalendarEvent(
            title="Invalid Event",
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow(),  # End time before start time
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(event)
        db_session.commit()

def test_calendar_event_update(db_session):
    # Create initial event
    event = CalendarEvent(
        title="Original Title",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=1),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(event)
    db_session.commit()

    # Update event
    event.title = "Updated Title"
    event.description = "New Description"
    db_session.commit()

    # Verify update
    updated_event = db_session.query(CalendarEvent).first()
    assert updated_event.title == "Updated Title"
    assert updated_event.description == "New Description"

def test_poll_creation(db_session):
    # Create a poll
    poll = Poll(
        title="Test Poll",
        creator_id=123,
        is_anonymous=False,
        allows_multiple_answers=True,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    db_session.add(poll)
    db_session.commit()

    # Create poll options
    option1 = PollOption(
        poll_id=poll.id,
        text="Option 1",
        created_at=datetime.utcnow()
    )
    option2 = PollOption(
        poll_id=poll.id,
        text="Option 2",
        created_at=datetime.utcnow()
    )
    db_session.add_all([option1, option2])
    db_session.commit()

    # Create poll votes
    vote1 = PollVote(
        poll_id=poll.id,
        option_id=option1.id,
        user_id=456,
        created_at=datetime.utcnow()
    )
    vote2 = PollVote(
        poll_id=poll.id,
        option_id=option2.id,
        user_id=789,
        created_at=datetime.utcnow()
    )
    db_session.add_all([vote1, vote2])
    db_session.commit()

    # Query the poll and verify relationships
    saved_poll = db_session.query(Poll).first()
    assert saved_poll.title == "Test Poll"
    assert len(saved_poll.options) == 2
    assert len(saved_poll.votes) == 2
    assert saved_poll.options[0].text == "Option 1"
    assert saved_poll.options[1].text == "Option 2"

def test_poll_validation(db_session):
    # Test poll with no options
    with pytest.raises(ValueError):
        poll = Poll(
            title="Invalid Poll",
            creator_id=123,
            is_anonymous=False,
            allows_multiple_answers=True,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() - timedelta(days=1)  # Expired poll
        )
        db_session.add(poll)
        db_session.commit()

def test_poll_vote_validation(db_session):
    # Create poll and option
    poll = Poll(
        title="Test Poll",
        creator_id=123,
        is_anonymous=False,
        allows_multiple_answers=False,  # Single answer only
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    db_session.add(poll)
    db_session.commit()

    option = PollOption(
        poll_id=poll.id,
        text="Option 1",
        created_at=datetime.utcnow()
    )
    db_session.add(option)
    db_session.commit()

    # Test duplicate vote
    vote1 = PollVote(
        poll_id=poll.id,
        option_id=option.id,
        user_id=456,
        created_at=datetime.utcnow()
    )
    db_session.add(vote1)
    db_session.commit()

    with pytest.raises(ValueError):
        vote2 = PollVote(
            poll_id=poll.id,
            option_id=option.id,
            user_id=456,  # Same user
            created_at=datetime.utcnow()
        )
        db_session.add(vote2)
        db_session.commit()

def test_job_metadata(db_session):
    # Create a job
    job = Job(
        name="Test Job",
        type="test",
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(job)
    db_session.commit()

    # Create job metadata
    metadata = JobMetadata(
        job_id=job.id,
        key="test_key",
        value="test_value",
        created_at=datetime.utcnow()
    )
    db_session.add(metadata)
    db_session.commit()

    # Query the job and verify metadata
    saved_job = db_session.query(Job).first()
    assert saved_job.name == "Test Job"
    assert len(saved_job.metadata) == 1
    assert saved_job.metadata[0].key == "test_key"
    assert saved_job.metadata[0].value == "test_value"

def test_job_status_transitions(db_session):
    # Create a job
    job = Job(
        name="Test Job",
        type="test",
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(job)
    db_session.commit()

    # Test valid status transition
    job.status = "active"
    db_session.commit()
    assert job.status == "active"

    # Test invalid status transition
    with pytest.raises(ValueError):
        job.status = "invalid_status"
        db_session.commit()

def test_job_scheduling(db_session):
    # Create a job with scheduling
    job = Job(
        name="Scheduled Job",
        type="test",
        status="pending",
        start_time=datetime.utcnow(),
        next_run=datetime.utcnow() + timedelta(hours=1),
        cron_expression="0 * * * *",  # Every hour
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(job)
    db_session.commit()

    # Verify scheduling
    saved_job = db_session.query(Job).first()
    assert saved_job.cron_expression == "0 * * * *"
    assert saved_job.next_run is not None
    assert saved_job.next_run > datetime.utcnow() 