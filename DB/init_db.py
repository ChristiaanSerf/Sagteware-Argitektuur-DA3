#!/usr/bin/env python3
"""
PostgreSQL Database Initialization Script
Creates tables for User, Game, and UserGameBridge
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_database():
    """Create the database if it doesn't exist"""
    # Connect to default postgres database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'nsarg')
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create database if it doesn't exist
    db_name = os.getenv('DB_NAME', 'nsarg_db')
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created successfully")
    else:
        print(f"Database '{db_name}' already exists")
    
    cursor.close()
    conn.close()

def create_tables():
    """Create the required tables"""
    # Connect to the specific database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'nsarg')
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create User table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "User" (
            UserID SERIAL PRIMARY KEY,
            UserName VARCHAR(100) NOT NULL UNIQUE,
            User_Steam_ID CHAR(17) NOT NULL UNIQUE
        )
    """)
    print("User table created/verified")
    
    # Create Game table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Game (
            GameID SERIAL PRIMARY KEY,
            GameName VARCHAR(100) NOT NULL UNIQUE
        )
    """)
    print("Game table created/verified")
    
    # Create UserGameBridge table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserGameBridge (
            UserID INTEGER NOT NULL,
            GameID INTEGER NOT NULL,
            GameRating DECIMAL(3,2) CHECK (GameRating >= 0 AND GameRating <= 5),
            SystemRating DECIMAL(3,2) CHECK (SystemRating >= 0 AND SystemRating <= 5),
            PRIMARY KEY (UserID, GameID),
            FOREIGN KEY (UserID) REFERENCES "User"(UserID) ON DELETE CASCADE,
            FOREIGN KEY (GameID) REFERENCES Game(GameID) ON DELETE CASCADE
        )
    """)
    print("UserGameBridge table created/verified")

    # Create MatchTemplate table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MatchTemplate (
            TemplateID SERIAL PRIMARY KEY,
            GameID INTEGER NOT NULL,
            match_type VARCHAR(100) NOT NULL,
            Win_condition VARCHAR(255) NOT NULL,
            playersCount_Team1 INTEGER NOT NULL,
            playersCount_Team2 INTEGER NOT NULL,
            FOREIGN KEY (GameID) REFERENCES Game(GameID) ON DELETE CASCADE
        )
    """)
    print("MatchTemplate table created/verified")

     # Create Match table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Match (
            MatchID SERIAL PRIMARY KEY,
            TemplateID INTEGER NOT NULL,
            MatchDateTime TIMESTAMP NOT NULL,
            WinningTeam INTEGER,
            FOREIGN KEY (TemplateID) REFERENCES MatchTemplate(TemplateID) ON DELETE CASCADE
        )
    """)
    print("Match table created/verified")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserMatchBridge (
            UserID INTEGER NOT NULL,
            MatchID INTEGER NOT NULL,
            Team INTEGER NOT NULL,
            KDA DECIMAL(5,2),
            ADR DECIMAL(6,2),
            Rating DECIMAL(4,2),
            PRIMARY KEY (UserID, MatchID),
            FOREIGN KEY (UserID) REFERENCES "User"(UserID) ON DELETE CASCADE,
            FOREIGN KEY (MatchID) REFERENCES Match(MatchID) ON DELETE CASCADE
        )
    """)
    print("UserMatchBridge table created/verified")
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_username ON \"User\"(UserName)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_gamename ON Game(GameName)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usergamebridge_userid ON UserGameBridge(UserID)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usergamebridge_gameid ON UserGameBridge(GameID)")
    print("Indexes created/verified")
    
    cursor.close()
    conn.close()


def main():
    """Main function to initialize the database"""
    try:
        print("Starting database initialization...")
        create_database()
        create_tables()
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
