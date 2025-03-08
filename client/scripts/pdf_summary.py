import openai
import time
import requests
import os

def download_file(url):
    # Create a temporary file using the OS module
    temp_filename = "temp_downloaded_file.pdf"  # Temporary filename

    try:
        # Download the file
        response = requests.get(url)
        response.raise_for_status()  # Ensure request was successful

        # Write the content to a file
        with open(temp_filename, "wb") as temp_file:
            temp_file.write(response.content)

        print(f"Temporary file created at: {temp_filename}")

        # Upload the file to OpenAI
        with open(temp_filename, "rb") as file:
            upload_response = openai.files.create(
                file=file,
                purpose="assistants"
            )

        file_id = upload_response.id
        print(f"Uploaded file ID: {file_id}")

    finally:
        # Delete the temporary file after upload
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            print(f"Temporary file {temp_filename} deleted.")

    # Return the file_id for further processing
    return pdf_summary(file_id)


def pdf_summary(file_id):

    # Step 2: Create an Assistant with 'file_search' and attach the file here
    assistant = openai.beta.assistants.create(
        name="PDF Analyzer",
        instructions="You are an AI that can analyze and summarize PDFs.",
        tools=[{"type": "file_search"}],
        model="gpt-4o-mini",
    )
    assistant_id = assistant.id
    print(f"Assistant ID: {assistant_id}")

    # Step 3: Create a new thread - (creating new conversation thread)
    thread = openai.beta.threads.create()
    thread_id = thread.id
    print(f"Thread ID: {thread_id}")

    # Step 4: Add a user message to the thread
    message = openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content="Summarize the key points from this PDF in 100 words or less. Please provide your answer in plain text with no markdown.",
        attachments=[
        {
            "file_id": file_id,
            "tools": [{"type": "file_search"}]
        }]
    )

    # Step 5: Run the Assistant (No file_id needed here!)
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id  #  Just reference the assistant
    )

    print(f"Run ID: {run.id}")

    #Step 6: Wait for the assistant to process the request
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        
        if run_status.status == "completed":
            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            
            # Collect all messages into a single string
            assistant_response = "\n".join(msg.content[0].text.value for msg in messages.data)

            # Print the complete response as a single string
            return assistant_response
            

        print("Waiting for response...")
        time.sleep(2)  # Prevent spamming the API


