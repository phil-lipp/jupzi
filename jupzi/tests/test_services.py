import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.telegram_service import TelegramService
from app.services.poll_service import PollService
from app.services.calendar_service import CalendarService
from app.models.polls import Poll, PollOption, PollVote
from app.models.calendar_events import CalendarEvent
from app.models.jobs import Job

@pytest.fixture
def mock_telegram_bot():
    with patch('app.services.telegram_service.TelegramBot') as mock:
        yield mock

@pytest.fixture
def mock_job_scheduler():
    with patch('app.services.calendar_service.JobScheduler') as mock:
        yield mock

@pytest.fixture
def telegram_service(mock_telegram_bot):
    return TelegramService()

@pytest.fixture
def poll_service(telegram_service):
    return PollService(telegram_service)

@pytest.fixture
def calendar_service(telegram_service, mock_job_scheduler):
    return CalendarService(telegram_service, mock_job_scheduler)

def test_create_poll(poll_service, db_session):
    # Test data
    title = "Test Poll"
    options = ["Option 1", "Option 2", "Option 3"]
    creator_id = 123
    is_anonymous = False
    allows_multiple_answers = True

    # Create poll
    poll = poll_service.create_poll(
        title=title,
        options=options,
        creator_id=creator_id,
        is_anonymous=is_anonymous,
        allows_multiple_answers=allows_multiple_answers,
        db=db_session
    )

    # Verify poll creation
    assert poll.title == title
    assert poll.creator_id == creator_id
    assert poll.is_anonymous == is_anonymous
    assert poll.allows_multiple_answers == allows_multiple_answers
    assert len(poll.options) == len(options)
    assert all(opt.text in options for opt in poll.options)

def test_vote_poll(poll_service, db_session):
    # Create test poll
    poll = Poll(
        title="Test Poll",
        creator_id=123,
        is_anonymous=False,
        allows_multiple_answers=False,
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

    # Test voting
    vote = poll_service.vote_poll(
        poll_id=poll.id,
        option_id=option.id,
        user_id=456,
        db=db_session
    )

    # Verify vote
    assert vote.poll_id == poll.id
    assert vote.option_id == option.id
    assert vote.user_id == 456

    # Test duplicate vote
    with pytest.raises(ValueError):
        poll_service.vote_poll(
            poll_id=poll.id,
            option_id=option.id,
            user_id=456,
            db=db_session
        )

def test_create_calendar_event(calendar_service, db_session):
    # Test data
    title = "Test Event"
    description = "Test Description"
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=1)
    location = "Test Location"

    # Create event
    event = calendar_service.create_event(
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time,
        location=location,
        db=db_session
    )

    # Verify event creation
    assert event.title == title
    assert event.description == description
    assert event.start_time == start_time
    assert event.end_time == end_time
    assert event.location == location

def test_schedule_calendar_event(calendar_service, db_session, mock_job_scheduler):
    # Create test event
    event = CalendarEvent(
        title="Test Event",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=1),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(event)
    db_session.commit()

    # Schedule event
    job = calendar_service.schedule_event(
        event_id=event.id,
        cron_expression="0 * * * *",  # Every hour
        db=db_session
    )

    # Verify job creation
    assert job.type == "calendar"
    assert job.status == "active"
    assert job.cron_expression == "0 * * * *"
    mock_job_scheduler.add_job.assert_called_once()

def test_telegram_notification(telegram_service, mock_telegram_bot):
    # Test data
    chat_id = 123
    message = "Test notification"

    # Send notification
    telegram_service.send_notification(chat_id, message)

    # Verify bot call
    mock_telegram_bot.send_message.assert_called_once_with(
        chat_id=chat_id,
        text=message
    )

def test_poll_notification(poll_service, telegram_service, mock_telegram_bot):
    # Create test poll
    poll = Poll(
        title="Test Poll",
        creator_id=123,
        is_anonymous=False,
        allows_multiple_answers=True,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=1)
    )

    # Send poll notification
    poll_service.notify_poll_creation(poll, 456)  # 456 is the chat_id

    # Verify bot call
    mock_telegram_bot.send_poll.assert_called_once()
    call_args = mock_telegram_bot.send_poll.call_args[1]
    assert call_args["chat_id"] == 456
    assert call_args["question"] == poll.title 