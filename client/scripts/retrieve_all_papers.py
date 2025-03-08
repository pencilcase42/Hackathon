import sys
import os

# Redirect stdout to stderr temporarily
original_stdout = sys.stdout
sys.stdout = sys.stderr

# Import libraries that might print to stdout
from db_init import init_db
import json
from bson import ObjectId
from datetime import datetime

# Restore stdout
sys.stdout = original_stdout

# Custom JSON encoder to handle MongoDB specific types
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)

def get_all_papers_from_db():
    """Retrieve all papers from MongoDB database"""
    try:
        # Initialize database connection (this may print to stderr)
        db = init_db(clear=False)
        
        # Make sure stdout is completely empty before writing our JSON
        sys.stdout.flush()
        
        # Fetch all papers from the database
        papers = db.get_all_papers()
        
        # Process papers to ensure they're JSON serializable
        processed_papers = []
        for paper in papers:
            # Create a new dict to avoid modifying the original document
            processed_paper = {}
            # Process each field to ensure it's serializable
            for key, value in paper.items():
                if key == '_id':
                    processed_paper[key] = str(value)
                else:
                    processed_paper[key] = value
            processed_papers.append(processed_paper)
        
        # Debug info to stderr
        sys.stderr.write(f"Retrieved and processed {len(processed_papers)} papers\n")
        
        # If no papers were found, return an empty array (not an error)
        if not processed_papers:
            sys.stderr.write("No papers found in the database\n")
            print(json.dumps([]))
            return []
        
        # Output the papers as JSON to stdout
        print(json.dumps(processed_papers, cls=MongoJSONEncoder))
        return processed_papers
        
    except Exception as e:
        # If any error occurs, log it to stderr and return an error object to stdout
        sys.stderr.write(f"Error retrieving papers: {str(e)}\n")
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    try:
        get_all_papers_from_db()
    except Exception as e:
        sys.stderr.write(f"Fatal error: {str(e)}\n")
        print(json.dumps({"error": str(e)}))
        sys.exit(1)