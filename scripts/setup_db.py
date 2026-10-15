import sqlite3
import os
import logging


# Setup lightweight logs
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("SQL Connection Setup")


def initialize_db():
    # Relative Paths
    db_path = 'data/db/ops.sqlite'
    schema_path = 'data/seeds/schema.sql'
    seed_data_path = 'data/seeds/seed_data.sql'

    # Create the target directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok = True)
    conn = None

    try:
        # Connect to the database and initialise the cursor
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logger.info(f"Connected to database at {db_path}")

        # 1. Read and execute the schema
        with open(schema_path, 'r') as schema_file:
            cursor.executescript(schema_file.read())
            logger.info("Schema created successfully")

        # 2. Read and execute the seed data script
        with open(seed_data_path, 'r') as seed_data:
            cursor.executescript(seed_data.read())
            logger.info("Seed data created successfully")

        # Save the changes
        conn.commit()
        logger.info("Database initialization complete")
    except sqlite3.Error as e:
        logger.exception(f"Database Error: {e}")
    except FileNotFoundError as e:
        logger.exception(f"File Error: Make sure your SQL files exist. {e}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    initialize_db()
