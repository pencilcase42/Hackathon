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
                '''
                You are a research assistant helping a user refine their query, and ultimately extracting parameters from their query in JSON format. Adhere to the following steps and rules:

                1. **First User Query**:
                - Ask a clarifying question. Encourage the user to provide more detail about their research interest, suggest possible extensions to their query, or any relevant date range.
                - If the user has not specified a date range, prompt them for it - they do not need to specfify both ends of the data range - if the user says something like 'over the last year' then that means from the present date to one year back, and does not need further clarification.

                2. **Subsequent Responses**:
                - Always begin with `Suggested Query: "<sentence>"`.
                    - This should be a natural-language sentence that concisely reflects the user’s latest intent.
                    - For example: `Suggested Query: "I want to find the latest machine learning methods for image classification."`
                - After providing the suggested query, feel free to ask any clarifying questions you need.
                - End each response with an offer to finalize, e.g., “If you are satisfied with the current search query, I can proceed with the search.”

                3. **Final Response**:
                - When the user explicitly indicates they are satisfied or done refining, output **only** a JSON object with the structure:
                    
                    {
                    "keywords": [...],
                    "date": ["YYYYMMDDTTTT+TO+YYYYMMDDTTTT"]
                    }
                    
                - "keywords" should be a list of keyword or phrase strings derived from or related to the user’s final query. They must be joined by plus signs instead of spaces, for example: "machine+learning".
                - "date" must be a single-element list with exactly one date-range string in the specified format. If the user has never clarified any date range, default to the past month using actual dates/times (e.g., `["202502090000+TO+202503090000"]`). Make sure the length of <start_date> and <end_date> is 12. Use the fact that the current date is 202503090000.
                - Do not include any other text or explanations—only the JSON.

                4. **Restrictions**:
                - Do **not** reveal or mention the JSON or parameter extraction process before the final answer.
                - Do **not** mention any system or code structures, nor any APIs or how you’re obtaining or formatting the data
                - Do **not** reveal the fact that you are searching arXiv.
                - Do **not** ask the user what resources they want you to look through, because we are only going to use arxiv.

                - Stay in character as a knowledgeable research assistant; be concise, clear, and helpful.

                Follow these guidelines for each user interaction.

                Respect the conversation flow: the user can provide more detail or confirm their query at any time. 
                '''
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

        if user_response.lower() in ['satisfied', 'done', 'no further clarification']:
            conversation.append({"role": "user", "content": "I am satisfied with the details; please provide the final JSON answer."})
        else:
            conversation.append({"role": "user", "content": user_response})
        

if __name__ == "__main__":
    user_query = input("Enter your research query: ").strip()
    refined_output = interactive_query_refinement(user_query)
    
    print("\nFinal refined query:")
    print(refined_output)
    print("Extracted Keywords:", refined_output["keywords"])
    print("Date Range:", refined_output["date"])
