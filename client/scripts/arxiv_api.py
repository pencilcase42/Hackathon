import os
import json
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


# params = {
#     "keywords": ["ai","machine+learning"],
#     "date_range": "[202401010000+TO+202412312359]",
#     "sortBy" : "relevance",
#     "sortOrder" : "descending"
# }

# getPDFs(params,test=True)
