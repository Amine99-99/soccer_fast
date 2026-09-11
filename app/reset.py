
from sqlmodel import SQLModel, create_engine, text
from models import User
from core.db import engine


# Drop all tables
SQLModel.metadata.drop_all(engine)

# Create all tables
SQLModel.metadata.create_all(engine)
print('database reset successfully')

