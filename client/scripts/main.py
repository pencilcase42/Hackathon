import os
import sys  # Add sys import
from db_init import init_db
from arxiv_api_modified import getPDFs
from pdf_summary import download_file

if __name__ == "__main__":
    # Redirect any stdout to stderr
    original_stdout = sys.stdout
    sys.stdout = sys.stderr
    
    try:
        # Initialize DB with clearing (since we're fetching fresh papers)
        db = init_db(clear=True)
        papers = getPDFs()
        
        for paper in papers:
            summary = download_file(paper['link'])
            paper['summary'] = summary
            db.insert(paper)
        # Make sure this goes to stderr, not stdout
        print("Paper fetched and saved successfully", file=sys.stderr)
    except Exception as e:
        print(f"Error in main.py: {e}", file=sys.stderr)
    finally:
        # Restore stdout
        sys.stdout = original_stdout
    
    