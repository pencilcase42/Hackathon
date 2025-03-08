import urllib.request as libreq
from datetime import datetime, timedelta
import feedparser
import json
import sys

def getPDFs(topic='ai', time_frame=10, test=False):
    try:
        # Topic will be search query 
        search_query = topic.replace(" ", "_")
        start = 0
        max_results = 10
        prefix = 'all'
        
        today = datetime.today()
        today_str = today.strftime('%Y%m%d%H%M')
        
        search_start_date = today - timedelta(days=time_frame)
        search_start_date_str = search_start_date.strftime('%Y%m%d') + '0000'
        
        daterange = f"{search_start_date_str}+TO+{today_str}"
        
        # Construct the arXiv API URL
        arxiv_url = f'http://export.arxiv.org/api/query?search_query={prefix}:{search_query}+AND+submittedDate:[{daterange}]&start={start}&max_results={max_results}'
        
        # Make the request to arXiv
        with libreq.urlopen(arxiv_url) as url:
            r = url.read()
        
        feed = feedparser.parse(r)
        
        if test:
            # Print out feed information (this will go to stderr)
            print(f'Feed title: {feed.feed.title}', file=sys.stderr)
            print(f'Feed last updated: {feed.feed.updated}', file=sys.stderr)
            print(f'totalResults for this query: {feed.feed.opensearch_totalresults}', file=sys.stderr)
        
        # Create a list to hold all papers
        papers = []
        
        # Process each entry
        for entry in feed.entries:
            # Create a paper object with the structure expected by our frontend
            paper = {
                'id': entry.id.split("/abs/")[-1],  # Use arXiv ID as our ID
                'title': entry.title,
                'author': ", ".join(author.name for author in entry.authors) if hasattr(entry, 'authors') else "Unknown",
                'date': entry.published.split('T')[0],  # Format as YYYY-MM-DD
                'tags': [t['term'] for t in entry.tags],
                'summary': entry.summary
            }
            
            papers.append(paper)
        
        # Output the papers as JSON to stdout
        print(json.dumps(papers))
        
    except Exception as e:
        # If any error occurs, return an error object
        error_obj = {"error": str(e)}
        print(json.dumps(error_obj))
        if test:
            print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

# If the script is run directly, use default parameters
if __name__ == "__main__":
    # Check if arguments were provided
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        topic = 'ai'
        
    if len(sys.argv) > 2:
        time_frame = int(sys.argv[2])
    else:
        time_frame = 10
        
    getPDFs(topic=topic, time_frame=time_frame, test=True)
