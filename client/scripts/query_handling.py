import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_api_parameters(user_query):
    prompt_template = f"""
You are an intelligent research assistant. A user has just asked the following research question: 

"{user_query}"

Your tasks are as follows:
1. Evaluate if the query is specific enough for retrieving relevant research papers. If it is too vague, list at least two clarifying questions that you would ask the user.
2. If the query is sufficiently specific, generate a JSON object with the following parameters for an API call:
    - "keywords": a list of key terms extracted from the query,
    - "date_range": a suggested date range if the query implies a temporal focus,
    - "subject_area": the primary subject area inferred from the query,
    - "additional_filters": any additional filters you think are relevant.

If the query is ambiguous, first provide the clarifying questions and do not generate parameters until more details are provided.

Please output your answer in the following JSON format:
{{
  "clarifying_questions": [ ... ],
  "api_parameters": {{ ... }}
}}

Make sure that if clarifying questions are provided, the "api_parameters" field is left empty.
    """
    
    response = openai.Completion.create(
        engine="gpt-4o-mini",
        prompt=prompt_template,
        temperature=0.3,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    result_text = response.choices[0].text.strip()
    try:
        result = json.loads(result_text)
    except json.JSONDecodeError:
        result = {"error": "Failed to parse response", "raw_output": result_text}
    
    return result

if __name__ == "__main__":
    user_query = input("Enter your research question: ")
    result = generate_api_parameters(user_query)
    print(json.dumps(result, indent=2))
