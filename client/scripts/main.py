import os
from db_init import init_db
from arxiv_api_modified import getPDFs
from pdf_summary import download_file

if __name__ == "__main__":
    db = init_db()
    papers = getPDFs()
    summary = download_file(papers[0]['link'])
    papers[0]['summary'] = summary
    db.insert(papers[0])
    print(db.get_all_papers())
    
    