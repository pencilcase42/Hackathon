import openai
import json
import os
import sys

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
    sys.exit(1)

client = openai.OpenAI(api_key=api_key)

def interactive_query_refinement(initial_query):

    conversation = [
        {
            "role": "system", 
            "content": (
                "You are an intelligent research assistant helping refine research queries for an arXiv API. "
                "Your role is to produce keywords and date for the API, which are specific enough, and are related to the user's query"
                "You may ask some clarifying questions to gather more detail"
                "When you have gathered sufficient detail, you may suggest an alternative query to the user and ask if they are satisfied "
                "Always ask the user if they are satisfied with the current state of the query at the end of every response you give, and if the user indicates they are satisfied, you must output only the final answer in valid JSON format with exactly two keys: "
                "'keywords' (an array of strings representing research topics, with '+' instead of spaces between words; do not include any time-related terms) and "
                "'date' (a date range string formatted as [YYYYMMDDTTTT+TO+YYYYMMDDTTTT] in GMT, using '202503090000' as the current date). "
                "Do not output the final JSON until you are confident that you have enough detail from the user. "
            )
        },
        {"role": "user", "content": initial_query}
    ]
    
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            temperature=0.7
        )
        agent_reply = response.choices[0].message.content.strip()
        print("Agent:", agent_reply)
        
        try:
            final_output = json.loads(agent_reply)
            if isinstance(final_output, dict) and "keywords" in final_output and "date" in final_output:
                return final_output
        except json.JSONDecodeError:
            pass
        
        user_response = input("Your response (or type 'satisfied' if you are done): ").strip()
        # If user signals satisfaction, add a message indicating no further clarification is needed.
        if user_response.lower() in ['satisfied', 'done', 'no further clarification']:
            conversation.append({"role": "user", "content": "I am satisfied with the details; please provide the final JSON answer."})
        else:
            conversation.append({"role": "user", "content": user_response})
        

if __name__ == "__main__":
    user_query = input("Enter your research query: ").strip()
    refined_output = interactive_query_refinement(user_query)
    
    print("\nFinal refined query:")
    print("Extracted Keywords:", refined_output["keywords"])
    print("Date Range:", refined_output["date"])
