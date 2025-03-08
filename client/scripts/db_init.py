from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
import sys  # Add sys import

# Load the environment variables from the .env file
load_dotenv()

class DB:
    def __init__(self):
        self.db_name = os.getenv("DB_NAME", "db")
        self.uri = os.getenv("DB_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        self.collection = self.db["papers"]
        # Redirect to stderr instead of stdout
        print(f"Connected to MongoDB database: '{self.db_name}' at URI: '{self.uri}'", file=sys.stderr)

    def clear_database(self):
        self.client.drop_database(self.db_name)
        # Redirect to stderr
        print(f"Database '{self.db_name}' has been cleared.", file=sys.stderr)
        
    def insert(self,paper):
        try:
            result = self.collection.insert_one(paper)
            # Redirect to stderr
            print(f"Inserted paper with _id: {result.inserted_id}", file=sys.stderr)
            return result.inserted_id
        except errors.PyMongoError as e:
            # Redirect to stderr
            print(f"Error inserting paper: {e}", file=sys.stderr)
            return None
        
    def get_all_papers(self):
        try:
            papers = list(self.collection.find())
            # Redirect to stderr
            print(f"Retrieved {len(papers)} papers from database", file=sys.stderr)
            return papers
        except errors.PyMongoError as e:
            # Redirect to stderr
            print(f"Error retrieving papers: {e}", file=sys.stderr)
            return []
        
def init_db(clear=False):
    # Initialize the database
    arxiv_db = DB()
    
    # Only clear if explicitly requested
    if clear:
        # This will erase all data in the database
        arxiv_db.clear_database()
        
    return arxiv_db