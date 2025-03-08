import urllib, urllib.request
import urllib.request as libreq
from datetime import datetime,timedelta
import feedparser
import json
import os
import shutil


def getPDFs(keywords = ['ai'], tags = ['cs.SE'], time_frame = 10,test=False):
    
    keywords = ['all:' + word for word in keywords]
    tags = ['cat:' + tag for tag in tags]
    search_query = '%28' + '+OR+'.join(keywords + tags) + '%29'
    #id_list = ''
    start = 0
    max_results = 10

    today = datetime.today()
    today_str = today.strftime('%Y%m%d%H%M')
    
    search_start_date = today - timedelta(days=time_frame)
    search_start_date_str = search_start_date.strftime('%Y%m%d') + '0000'
    
    daterange = f"{search_start_date_str}+TO+{today_str}"
    
    with libreq.urlopen(f'http://export.arxiv.org/api/query?search_query={search_query}+AND+submittedDate:[{daterange}]&start={start}&max_results={max_results}') as url:
      r = url.read()
    feed = feedparser.parse(r)

    if test:
        # Print out feed information
        print(f'Feed title: {feed.feed.title}')
        print(f'Feed last updated: {feed.feed.updated}')

        # Print OpenSearch metadata
        print(f'totalResults for this query: {feed.feed.opensearch_totalresults}')
        print(f'itemsPerPage for this query: {feed.feed.opensearch_itemsperpage}')
        print(f'startIndex for this query: {feed.feed.opensearch_startindex}')
    
    folder = 'outputs'
    if os.path.exists(folder):
        shutil.rmtree(folder)  # Deletes the entire folder and its contents
        os.makedirs(folder, exist_ok=True)  # Recreate the empty folder
    
    # Run through each entry and print out information
    for entry in feed.entries:
        output = {
        'arxiv_id':'',
        'published':'',
        'title':'',
        'authors':'',
        'abs_link':'',
        'pdf_link':'',
        'journal_ref':'',
        'primary_Category':'',
        'all_Categories':'',
        'abstract':''
    }
        
        output['arxiv_id'] = entry.id.split("/abs/")[-1]
        output['published'] = entry.published
        output['title'] = entry.title
        
        try:
            output['authors'] = ", ".join(author.name for author in entry.authors)
        except AttributeError:
            pass

        # Get the links to the abs page and PDF for this e-print
        # add doi later if we include articles outside arxiv
        for link in entry.links:
            if link.rel == 'alternate':
                output['abs_link'] = link.href
            elif link.title == 'pdf':
                output['pdf_link'] = link.href
        
        # The journal reference, comments, and primary_category sections live under the arxiv namespace
        try:
            journal_ref = entry.arxiv_journal_ref
        except AttributeError:
            journal_ref = 'No journal ref found'
        output['journal_ref'] = journal_ref
        
        
        # Primary category (dirty hack to get it)
        output['primary_Category'] = entry.tags[0]["term"]
        
        # Get all categories
        all_categories = [t['term'] for t in entry.tags]
        output['all_Categories'] = ", ".join(all_categories)
        
        # The abstract is in the <summary> element
        output['abstract'] = entry.summary
        
        with open(f"{folder}\{output['arxiv_id']}.json", "w") as outfile:
            json.dump(output, outfile, indent=4)
            if test:
                print("saved")

getPDFs(test=True)


