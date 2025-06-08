#!/usr/bin/env python
import os
import sys
import click
from alembic import command
from alembic.config import Config
from app.core.config import get_settings

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@click.group()
def cli():
    """Database management commands."""
    pass

@cli.command()
def init():
    """Initialize the database with the first migration."""
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    # Create initial migration
    command.init(alembic_cfg, "migrations")
    click.echo("Database initialized with migrations directory.")

@cli.command()
@click.option('--message', '-m', help='Migration message')
def migrate(message):
    """Create a new migration."""
    if not message:
        message = click.prompt('Enter migration message')
    
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    # Create new migration
    command.revision(alembic_cfg, message=message, autogenerate=True)
    click.echo(f"Created new migration: {message}")

@cli.command()
@click.option('--revision', '-r', default='head', help='Revision to upgrade to')
def upgrade(revision):
    """Upgrade database to a later version."""
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    # Upgrade database
    command.upgrade(alembic_cfg, revision)
    click.echo(f"Database upgraded to revision: {revision}")

@cli.command()
@click.option('--revision', '-r', default='-1', help='Revision to downgrade to')
def downgrade(revision):
    """Revert database to a previous version."""
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    # Downgrade database
    command.downgrade(alembic_cfg, revision)
    click.echo(f"Database downgraded to revision: {revision}")

@cli.command()
def current():
    """Show current database revision."""
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    # Show current revision
    command.current(alembic_cfg)
    click.echo("Current database revision shown above.")

@cli.command()
def history():
    """Show migration history."""
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    # Show migration history
    command.history(alembic_cfg)
    click.echo("Migration history shown above.")

if __name__ == '__main__':
    cli() 