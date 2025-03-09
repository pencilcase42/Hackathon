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
import time
import matplotlib.pyplot as plt
import networkx as nx
def getPDFs(inputs, daterange, sortby = 'relevance', sortorder = 'descending', test=False):
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
    print("WE ARE HERE \n \n \n \n \n", file=sys.stderr)
    print(feed.entries, file=sys.stderr)
    papers = []
   
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

        papers.append(output)
    return papers

def web_query_refinement(user_query, previous_conversation=None):
    """
    Process a user query for the web interface.
    
    Args:
        user_query: Current user query
        previous_conversation: Previous conversation history
        
    Returns:
        A dict with message, conversation, is_final flag, and search_params if finalized
    """
    # Initialize conversation with system prompt
    system_prompt = {
        "role": "system", 
        "content": (
            '''
            You are a research assistant helping a user refine their query, and ultimately extracting parameters from their query in JSON format. Adhere to the following steps and rules:

            1. **First User Query**:
            - Ask a clarifying question. Encourage the user to provide more detail about their research interest, suggest possible extensions to their query, or any relevant date range.
            - If the user has not specified a date range, prompt them for it.

            2. **Subsequent Responses**:
            - Always begin with `Suggested Query: "<sentence>"`.
                - This should be a natural-language sentence that concisely reflects the user's latest intent.
                - For example: `Suggested Query: "I want to find the latest machine learning methods for image classification."`
            - After providing the suggested query, feel free to ask any clarifying questions you need.
            - End each response with an offer to finalize, e.g., "If you are satisfied with the current search query, I can proceed with the search."

            3. **Final Response**:
            - When the user explicitly indicates they are satisfied or done refining, output **only** a JSON object with the structure:
                {
                "keywords": [...],
                "date": ["YYYYMMDDTTTT+TO+YYYYMMDDTTTT"]
                }
            - "keywords" should be a list of keyword or phrase strings derived from or related to the user's final query. They must be joined by plus signs instead of spaces, for example: "machine+learning".
            - "date" must be a single-element list with exactly one date-range string in the specified format. If the user has never clarified any date range, default to the past month using actual dates/times (e.g., `["202502090000+TO+202503090000"]`). Make sure the length of <start_date> and <end_date> is 12.
            - Do not include any other text or explanations—only the JSON.

            4. **Restrictions**:
            - Do **not** reveal or mention the JSON or parameter extraction process before the final answer.
            - Do **not** mention any system or code structures, nor any APIs or how you're obtaining or formatting the data
            - Do **not** reveal the fact that you are searching arXiv.
            - Do **not** ask the user what resources they want you to look through, because we are only going to use arxiv.

            - Stay in character as a knowledgeable research assistant; be concise, clear, and helpful.

            Follow these guidelines for each user interaction.

            Respect the conversation flow: the user can provide more detail or confirm their query at any time. 
            '''
        )
    }
    
    # Check if we already have a conversation history
    if previous_conversation and len(previous_conversation) > 0:
        # Use existing conversation, but make sure we have the system prompt
        if previous_conversation[0].get("role") != "system":
            messages = [system_prompt] + previous_conversation
        else:
            messages = previous_conversation
        
        # Add the latest user query
        messages.append({"role": "user", "content": user_query})
    else:
        # Start new conversation
        messages = [
            system_prompt,
            {"role": "user", "content": user_query}
        ]
    
    # Get response from OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )
    
    # Extract assistant's reply
    assistant_reply = response.choices[0].message.content.strip()
    
    # Add assistant's response to the conversation history
    updated_conversation = messages + [{"role": "assistant", "content": assistant_reply}]
    
    # Check if this is a final JSON response
    if user_query.lower() in ['satisfied', 'done', 'no further clarification', 'i am satisfied']:
        final_messages = updated_conversation + [
            {"role": "user", "content": "I am satisfied with the details; please provide the final JSON answer."}
        ]
        
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=final_messages,
            temperature=0.1
        )
        print("FINAL RESPONSE \n \n \n \n \n", file=sys.stderr)
        final_reply = final_response.choices[0].message.content
        print(final_reply, file=sys.stderr)
        first_bracket=0
        second_bracket=0
        for i in range(len(final_reply)):
            if final_reply[i]=="{":
                first_bracket=i
            elif final_reply[i]=="}": 
                second_bracket=i    
        final_reply=final_reply[first_bracket:second_bracket+1]  
        # Try to extract JSON from the response
        search_params = json.loads(final_reply)
        print(search_params, file=sys.stderr)
        updated_conversation = final_messages + [{"role": "assistant", "content": final_reply}]
        assistant_reply = final_reply  # Use the final reply for the message
    
        # Process the keywords and date from the search params
        keywords = search_params.get("keywords", [])
        
        # Handle date format - convert it to our expected format
        date_range = search_params.get("date", [])
        print("OUTPUTS \n \n \n \n \n", file=sys.stderr)
        print(keywords, file=sys.stderr)
        print(date_range, file=sys.stderr)
        
        # Format for our output
        search_params_formatted = {
            "keywords": keywords,
            "date": date_range
        }
        print("RETURNING VALUES \n \n \n \n \n",file=sys.stderr)
        return {
            "is_final": True,
            "search_params": search_params_formatted,
            "conversation": updated_conversation,
            "message": "I'll search for papers based on your refined query."
        }
    
    else:
        # Not a final request, return conversation for further refinement
        return {
            "is_final": False,
            "conversation": updated_conversation,
            "message": assistant_reply
        }

def create_paper_evaluation_prompt(paper, search_queries, user_query):
    system_message = """You are a specialized research assistant that evaluates academic papers for relevance to a user's query.

Your task is to analyze the provided paper metadata and determine if this paper is relevant to the user's original search intent. You have access to:
1. The paper's complete metadata (ID, title, authors, publication date, tags, and abstract)
2. The search queries that were used to find this paper
3. The user's original query that initiated the search

When evaluating relevance, consider:
- How closely the paper's content aligns with the specific information needs expressed in the user query
- Whether the paper addresses the particular aspects or subtopics mentioned in the query
- If the paper's recency, authority, methodology, or findings make it particularly valuable for answering the query
- The relationship between the search queries used and both the paper content and original user intent

Provide your evaluation in a clear, structured JSON format that can be easily parsed by the calling program."""

    user_message = f"""
USER'S ORIGINAL QUERY: "{user_query}"

SEARCH QUERIES USED TO FIND THIS PAPER: {search_queries}

PAPER DETAILS:
ID: {paper['arxiv_id']}
Title: {paper['title']}
Authors: {paper['authors']}
Published: {paper['published']}
Tags: {paper['all_Categories']}
Abstract: {paper['abstract']}

Determine if this paper is relevant to the user's original query. Return your response in JSON format.
"""

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "paper_evaluation",
            "schema": {
                "type": "object",
                "properties": {
                    "is_relevant": {
                        "type": "boolean",
                        "description": "Whether the paper is relevant to the user's query"
                    },
                    "relevance_score": {
                        "type": "integer",
                        "description": "Relevance score from 1-10, with 10 being extremely relevant"
                    },
                    "justification": {
                        "type": "string",
                        "description": "A clear, concise explanation (2-3 sentences) of why the paper is or isn't relevant to the user's query"
                    },
                    "key_topics_matched": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of specific topics or concepts from the user query that this paper addresses"
                    }
                },
                "required": ["is_relevant", "relevance_score", "justification", "key_topics_matched"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

    return {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "response_format": response_format
    }
def draw_graph(papers):
    G = nx.MultiGraph()
    size = []
    labels = {}
    n = 1
    
    for paper in papers: 
        G.add_node(paper['title'])
        size.append(300 * paper['relevance']**0.5)
        labels[paper['title']] = n
        n+=1
        
        
    visited = set()
    weights = []
    for p1 in papers:
      for p2 in papers:
          i = p1['arxiv_id']
          j = p2['arxiv_id']
          
          if i!=j and j+i not in visited:
            tags1 = set(p1['all_Categories'].split(','))
            tags2 = set(p2['all_Categories'].split(','))
            
            w = len(tags1.intersection(tags2))
            
            if w > 0:
                G.add_edge(p1['title'],p2['title'],weight=w)
                weights.append(w ** 2)
            visited.add(i+j)
            

    options = {
    "font_size": 11,
    "node_size": size,
    "node_color": "white",
    "edgecolors": "black",
    "width": weights,
    "linewidths": 5,
    "labels":labels
}
    
    fig, ax = plt.subplots(figsize=(12, 12))  # Increase the size of the plot
    pos = nx.circular_layout(G)  
    
    # Draw the graph with node labels
    nx.draw(G, pos, with_labels=True, ax=ax, **options)
    
    
    plt.axis('off')  # Remove axis for better presentation
    plt.subplots_adjust(right=0.5)
    handles = [plt.Line2D([0], [0], color='w', label=f"{num}: {title}") for title,num in labels.items()]
    plt.legend(handles=handles, loc="center right", title="Node Legend",bbox_to_anchor=(2, 0.5))
    
    plt.savefig('../graph.png')

# Check for OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print(json.dumps({"error": "OPENAI_API_KEY environment variable not set"}))
    sys.exit(1)

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

# Main entry point
if __name__ == "__main__":
    # Check if running from web interface (with input file)
    if len(sys.argv) > 1:
        try:
            # Read input JSON
            with open(sys.argv[1], 'r') as f:
                input_data = json.load(f)
            
            user_query = input_data.get("query", "")
            conversation = input_data.get("conversation", [])
            
            # Process the query using the web interface version
            result = web_query_refinement(user_query, conversation)
            
            # Initialize papers list
            found_papers = []
            
            # If we have final search parameters, fetch papers
            if result.get("is_final") and "search_params" in result:
                try:
                    # Get search parameters
                    keywords = result["search_params"]["keywords"]
                    date_range = result["search_params"]["date"]
                    
                    # Log the search parameters
                    print(f"Searching for papers with keywords: {keywords}, date range: {date_range}", file=sys.stderr)
                    
                    # Fetch papers using the refined query
                    found_papers = getPDFs(inputs=keywords, daterange=date_range)
                    print("Papers found:", found_papers, file=sys.stderr)
                    # Convert papers to a simplified format for the frontend
                    simplified_papers = []
                    for paper in found_papers:
                        simplified_papers.append({
                            "id": paper.get('arxiv_id', ''),
                            "title": paper.get('title', ''),
                            "author": paper.get('authors', ''),
                            "date": paper.get('published', '').split('T')[0] if 'T' in paper.get('published', '') else paper.get('published', ''),
                            "summary": paper.get('abstract', ''),
                            "tags": paper.get('all_Categories', '').split(', ') if paper.get('all_Categories') else [],
                            "pdf_link": paper.get('pdf_link', '')
                        })
                    
                    # Enhance the message if papers were found
                    if simplified_papers:
                        # Add a summary of the papers found
                        paper_titles = "\n".join([f"- {p['title']}" for p in simplified_papers[:3]])
                        if len(simplified_papers) > 3:
                            paper_titles += f"\n...and {len(simplified_papers) - 3} more papers"
                        
                        result["message"] = f"I found {len(simplified_papers)} papers matching your criteria. Here are some of them:\n{paper_titles}"
                    else:
                        result["message"] = "I searched for papers, but couldn't find any matching your criteria. Would you like to refine your search?"
                    
                    # Use the simplified papers for the response
                    found_papers = simplified_papers
                    
                except Exception as e:
                    print(f"Error fetching papers: {str(e)}", file=sys.stderr)
                    result["message"] = f"I tried to search for papers, but encountered an error: {str(e)}"
            
            # Return JSON response
            print(json.dumps({
                "message": result["message"],
                "conversation": result["conversation"],
                "is_final": result.get("is_final", False),
                "papers": found_papers
            }))
            
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.exit(1)
    else:
        # Console interface for testing
        user_query = input("Enter your research query: ")
        result = web_query_refinement(user_query)
        print("\nAgent response:", result["message"])
        
        if result.get("is_final"):
            print("\nFinal search parameters:")
            print("Keywords:", result["search_params"]["keywords"])
            print("Date range:", result["search_params"]["date"])

        papers = getPDFs(inputs = result["search_params"]["keywords"], daterange = result["search_params"]["date"])

        for i in range(len(papers)):
            prompt_data = create_paper_evaluation_prompt(papers[i], result["search_params"]["keywords"], user_query)

            try:
                # Call the OpenAI API
                response = client.chat.completions.create(**prompt_data)

                # Extract and parse the evaluation
                evaluation = json.loads(response.choices[0].message.content)
                print("Paper ID: ", papers[i]['arxiv_id'])
                print(f"Relevant? {evaluation["is_relevant"]}")
                print(f"Relevance Score: {evaluation["relevance_score"]}")
                print(f"Justification: \n {evaluation["justification"]}\n")
                print(f"Key Topics Matched: \n {evaluation["key_topics_matched"]}")
                papers[i]["relevance"] = evaluation["relevance_score"]


            except Exception as e:
                print(f"Error calling OpenAI API: {e}", file=sys.stderr)
        draw_graph(papers)