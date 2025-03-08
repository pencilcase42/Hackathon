import os
from db_init import init_db
from arxiv_api_modified import getPDFs

if __name__ == "__main__":
    db = init_db()
    papers = getPDFs()
    for paper in papers:
        db.insert(paper)
    
    print(db.get_all_papers()[1])
    
    