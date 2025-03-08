from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
load_dotenv()

class DB:
    def __init__(self):
        self.db_name = os.getenv("DB_NAME", "db")
        self.uri = os.getenv("DB_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        print(f"Connected to MongoDB database: '{self.db_name}' at URI: '{self.uri}'")

    def clear_database(self):
        self.client.drop_database(self.db_name)
        print(f"Database '{self.db_name}' has been cleared.")

if __name__ == "__main__":
    # Initialize the database
    arxiv_db = DB()
    # Clear the database (use with caution)
    arxiv_db.clear_database()