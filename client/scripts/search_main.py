import openai
import json
import os
import sys
import shutil
import datetime
from datetime import timedelta
import urllib.request as libreq
import urllib.parse
import feedparser


def getPDFs(params, test=False):
    inputs, daterange, sortby, sortorder = params['keywords'], params['date_range'], params['sortBy'], params['sortOrder']
    
    
    
    inputs = ['all:' + '+'.join(input.split(' ')) for input in inputs]
    search_query = '%28' + '+AND+'.join(inputs) + '%29'
    start = 0
    max_results = 10

    # today = datetime.datetime.today()
    # today_str = today.strftime('%Y%m%d%H%M')
    # search_start_date = today - timedelta(days=time_frame)
    # search_start_date_str = search_start_date.strftime('%Y%m%d') + '0000'
    # daterange = f'{search_start_date_str}+TO+{today_str}'
    
    base_url = 'http://export.arxiv.org/api/query?'

    query_string = (
    f"search_query={search_query}+AND+submittedDate:{daterange}"
    f"&start={start}&max_results={max_results}&sortBy={sortby}&sortOrder={sortorder}"
)
    
    full_url = base_url + query_string 

    with libreq.urlopen(full_url) as url:
        r = url.read()
    feed = feedparser.parse(r)

    if test:
        print(f'Feed title: {feed.feed.get("title", "No Title")}')
        print(f'Feed last updated: {feed.feed.get("updated", "Unknown")}')
        print(f'Total results: {feed.feed.get("opensearch_totalresults", "Unknown")}')
        print(f'Items per page: {feed.feed.get("opensearch_itemsperpage", "Unknown")}')
        print(f'Start index: {feed.feed.get("opensearch_startindex", "Unknown")}')
    
    
    folder = 'outputs'
    if os.path.exists(folder):
        shutil.rmtree(folder)  # Deletes existing folder
    os.makedirs(folder, exist_ok=True)  # Creates a new empty folder

   
    for entry in feed.entries:
        output = {
            'arxiv_id': entry.id.split('/abs/')[-1],
            'published': entry.published,
            'title': entry.title,
            'authors': ', '.join(author.name for author in getattr(entry, 'authors', [])),
            'abs_link': '',
            'pdf_link': '',
            'journal_ref': getattr(entry, 'arxiv_journal_ref', 'No journal ref found'),
            'primary_Category': '',
            'all_Categories': '',
            'abstract': entry.summary
        }

        for link in entry.links:
            if link.rel == 'alternate':
                output['abs_link'] = link.href
            elif link.get('title') == 'pdf':
                output['pdf_link'] = link.href

        if hasattr(entry, 'tags') and entry.tags:
            output['primary_Category'] = entry.tags[0]['term']
            output['all_Categories'] = ', '.join(t['term'] for t in entry.tags)

        json_path = os.path.join(folder, f'{output["arxiv_id"]}.json')
        with open(json_path, 'w') as outfile:
            json.dump(output, outfile, indent=4)
            if test:
                print(f'Saved: {json_path}')

def create_arxiv_query_prompt(user_input_query): # UPDATE WITH CHANGES
    prompt_text = f"""
A user has just asked the following research question:

"{user_input_query}"

You are a helpful assistant that extracts relevant information for constructing queries to the arXiv API. A user has provided a research-related query. Your task is to extract the essential keywords from the query and determine a time range in GMT formatted as follows:

[YYYYMMDDTTTT+TO+YYYYMMDDTTTT]

- Keywords: Create a list of keywords that accurately represent the research subject matter. The keywords must be strictly about the research topic and must not include any time-related references. The keywords should also contain information from the user's query itself.
- Date: Generate a date string following the format where YYYY is the four-digit year, MM is the two-digit month, DD is the two-digit day, and TTTT represents the time in 24-hour format to the minute (HHMM). Use GMT time for this output. The current data is 202503090000.

Your response must be a valid JSON object with exactly two keys: "keywords" (an array of strings) and "date" (a string formatted as specified). Do not include any additional text or commentary.

Example output (do not include comments in your actual response):

{{
  "keywords": ["transformer+models", "efficiency+improvements"],
  "date": "202503091200+TO+202503091245"
}}
    """

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "arxiv_query",
            "schema": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of keywords related to the research subject matter. Must not include any time-related terms."
                    },
                    "date": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "A date range formatted as [YYYYMMDDTTTT+TO+YYYYMMDDTTTT] in GMT."
                    }
                },
                "required": ["keywords", "date"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

    return {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an intelligent research assistant."},
            {"role": "user", "content": prompt_text}
        ],
        "response_format": response_format
    }

api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)

user_query = input("Enter your research query: ")
prompt_data = create_arxiv_query_prompt(user_query)
try:
    response = client.chat.completions.create(**prompt_data)

    output = json.loads(response.choices[0].message.content)
    print("Extracted Keywords:", output["keywords"],file=sys.stderr)
    print("Date Range:", output["date"],file=sys.stderr)

except Exception as e:
    print(f"Error calling OpenAI API: {e}", file=sys.stderr)

getPDFs(params=output)



