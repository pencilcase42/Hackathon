import os
import sys
import json
from db_init import init_db
from arxiv_api_modified import getPDFs
from pdf_summary import download_file

LOG_PREFIX = "[MAIN]"

if __name__ == "__main__":
    # Store original stdout for reference
    original_stdout = sys.stdout
    
    try:
        # Initialize DB with clearing (since we're fetching fresh papers)
        print(f"{LOG_PREFIX} Initializing database...", file=sys.stderr)
        db = init_db(clear=True)
        
        print(f"{LOG_PREFIX} Fetching papers from arXiv...", file=sys.stderr)
        papers = getPDFs()
        
        # First, insert all papers with waiting summaries so they appear immediately
        print(f"{LOG_PREFIX} Inserting {len(papers)} papers with placeholder summaries...", file=sys.stderr)
        for paper in papers:
            db.insert(paper)
        
        # Signal that initial papers are ready for display
        print("INITIAL_PAPERS_READY", file=sys.stdout)
        sys.stdout.flush()
        
        # Process papers individually to generate summaries
        print(f"{LOG_PREFIX} Beginning to process papers for summaries...", file=sys.stderr)
        for i, paper in enumerate(papers):
            try:
                paper_id = paper['id']
                print(f"{LOG_PREFIX} Processing paper {i+1}/{len(papers)}: {paper_id}", file=sys.stderr)
                
                # Get summary
                summary = download_file(paper['link'])
                paper['summary'] = summary
                
                # Update in database
                db.insert(paper)
                
                # Signal that a paper's summary is ready
                print(f"PAPER_UPDATED:{paper_id}", file=sys.stdout)
                sys.stdout.flush()
                
            except Exception as e:
                print(f"{LOG_PREFIX} Error processing paper {paper.get('id', 'unknown')}: {e}", file=sys.stderr)
        
        # Signal completion
        print(f"{LOG_PREFIX} All papers processed successfully!", file=sys.stderr)
        print("PROCESSING_COMPLETE", file=sys.stdout)
        sys.stdout.flush()
        
    except Exception as e:
        print(f"{LOG_PREFIX} Error in main.py: {e}", file=sys.stderr)
    
    