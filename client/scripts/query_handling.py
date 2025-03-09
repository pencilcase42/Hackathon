import os
import json
import openai
import time
import sys

def generate_api_parameters(prompt_template):

    # Step 2: Create an Assistant with 'file_search' and attach the file here
    assistant = openai.beta.assistants.create(
        name="PDF Analyzer",
        instructions="You are an intelligent research assistant. A user has just asked the following research question: ",
        model="gpt-4o-mini",
    )
    assistant_id = assistant.id
    print(f"Assistant ID: {assistant_id}", file=sys.stderr)

    # Step 3: Create a new thread - (creating new conversation thread)
    thread = openai.beta.threads.create()
    thread_id = thread.id
    print(f"Thread ID: {thread_id}", file=sys.stderr)

    # Step 4: Add a user message to the thread
    message = openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt_template
    )

    # Step 5: Run the Assistant (No file_id needed here!)
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id  #  Just reference the assistant
    )

    print(f"Run ID: {run.id}", file=sys.stderr)

    #Step 6: Wait for the assistant to process the request
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run_status.status == "completed":
            messages = openai.beta.threads.messages.list(thread_id=thread_id)

            # Find the assistant's last response only
            for msg in messages.data:
                if msg.role == "assistant":  # Ensures only the assistant's response is captured
                    return msg.content[0].text.value

        time.sleep(2)


            
        
    


if __name__ == "__main__":
    user_query = input("Enter your research question: ")
    prompt_template = f"""
A user has just asked the following research question: 

"{user_query}"

You are a helpful assistant that extracts relevant information for constructing queries to the arXiv API. A user will provide a research-related query. Your task is to extract the essential keywords from the query and determine a time range in GMT formatted as follows:

[YYYYMMDDTTTT+TO+YYYYMMDDTTTT]

Keywords: Create a list of keywords that accurately represent the research area mentioned in the user's query. Always make sure to use a '+' instead of a space between words. Ensure that the keywords are strictly about the subject matter and do not include any time references.
Date: Generate a date string following the format where YYYY is the four-digit year, MM is the two-digit month, DD is the two-digit day, and TTTT represents the time in 24-hour format to the minute (HHMM). Use GMT time for this output.give me papers related to the transformer model and how that has increased efficiancy 

Your response must be a valid JSON object with exactly two keys: "keywords" (an array of strings) and "date" (a string formatted as specified). Do not include any additional text or commentary in your output.

Example output (do not include comments in your actual response):

{{
  "keywords": ["machine+learning", "neural+networks"],
  "date": "202503091200+TO+202503091245"
}}
    """
    result = generate_api_parameters(prompt_template)
    #print(json.dumps(result, indent=2))
    print(type(result))
    print(result)