import sqlalchemy
from sqlalchemy import create_engine, text

# Connect without selecting a database
# NOTE: Assuming root:@localhost based on config
engine = create_engine("mysql+pymysql://root:@localhost/")

try:
    with engine.connect() as conn:
        print("Creating database 'photo_platform'...")
        conn.execute(text("CREATE DATABASE IF NOT EXISTS photo_platform"))
        print("Database created successfully!")
except Exception as e:
    print(f"Failed to create database: {e}")
