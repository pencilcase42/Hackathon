from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
import sys  # Add sys import

# Load the environment variables from the .env file
load_dotenv()

class DB:
    def __init__(self, verbose=True):
        self.db_name = os.getenv("DB_NAME", "db")
        self.uri = os.getenv("DB_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        self.collection = self.db["papers"]
        self.verbose = verbose
        # Only log if verbose is enabled
        if self.verbose:
            print(f"Connected to MongoDB database: '{self.db_name}'", file=sys.stderr)

    def clear_database(self):
        self.client.drop_database(self.db_name)
        # Only log if verbose is enabled
        if self.verbose:
            print(f"Database '{self.db_name}' has been cleared.", file=sys.stderr)
        
    def insert(self, paper):
        try:
            # First check if this paper already exists
            existing = self.collection.find_one({"id": paper["id"]})
            
            if existing:
                # Update the existing paper, preserving the _id
                result = self.collection.update_one(
                    {"id": paper["id"]},
                    {"$set": paper}
                )
                # Only log if verbose is enabled
                if self.verbose:
                    print(f"Updated paper with id: {paper['id']}", file=sys.stderr)
                return existing["_id"]
            else:
                # Insert new paper
                result = self.collection.insert_one(paper)
                # Only log if verbose is enabled
                if self.verbose:
                    print(f"Inserted paper with _id: {result.inserted_id}", file=sys.stderr)
                return result.inserted_id
        except errors.PyMongoError as e:
            # Always log errors
            print(f"Error inserting paper: {e}", file=sys.stderr)
            return None
        
    def get_all_papers(self, verbose=True):
        try:
            papers = list(self.collection.find())
            # Only log if verbose is enabled
            if self.verbose and verbose:
                print(f"Retrieved {len(papers)} papers from database", file=sys.stderr)
            return papers
        except errors.PyMongoError as e:
            # Always log errors
            print(f"Error retrieving papers: {e}", file=sys.stderr)
            return []
        
def init_db(clear=False, verbose=True):
    # Initialize the database
    arxiv_db = DB(verbose=verbose)
    # This will erase all data in the database
    if clear:
        arxiv_db.clear_database()
        
    return arxiv_db