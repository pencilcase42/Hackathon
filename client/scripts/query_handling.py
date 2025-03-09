import openai
import json
import os
import sys

api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)

def create_arxiv_query_prompt(user_query):
    prompt_text = f"""
A user has just asked the following research question:

"{user_query}"

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

if __name__ == "__main__":
    if client is None:
        print("Error: OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    user_query = input("Enter your research query: ")
    prompt_data = create_arxiv_query_prompt(user_query)

    try:
        response = client.chat.completions.create(**prompt_data)

        output = json.loads(response.choices[0].message.content)
        print("Extracted Keywords:", output["keywords"])
        print("Date Range:", output["date"])

    except Exception as e:
        print(f"Error calling OpenAI API: {e}", file=sys.stderr)
