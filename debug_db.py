import os
from sqlalchemy import create_engine, text
from config import Config

def test_connection():
    print(f"Testing connection to: {Config.SQLALCHEMY_DATABASE_URI}")
    try:
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Connection successful!", result.fetchone())
            
            print("Checking tables...")
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print("Tables found:", tables)
            
            if 'users' in tables and 'albums' in tables:
                print("Core tables exist.")
            else:
                print("WARNING: Core tables (users, albums) are MISSING. Did you run 'flask db upgrade'?")

    except Exception as e:
        print("\nConnection FAILED!")
        print("Error details:", str(e))

if __name__ == "__main__":
    test_connection()
