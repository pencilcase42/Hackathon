
import openai
import time
import requests
import tempfile


file_path = "/Users/ahmadkitchlew/Documents/Computing/Hackathon_AI_Agents/Hackathon/Testing_openai_API/2503.04218v1.pdf"
def download_file():
    url = "https://arxiv.org/pdf/2503.04164"

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        # Download the file
        response = requests.get(url)
        response.raise_for_status()  # Ensure request was successful

        # Write content to temporary file
        temp_file.write(response.content)
        temp_file.flush()  # Ensure data is written to disk

        print(f"Temporary file created at: {temp_file.name}")

        # Now you can process the file (e.g., read it)
        with open(file_path, "rb") as file:
            response = openai.files.create(
                file=file,
                purpose="assistants"
            )

        file_id = response.id
        print(f"Uploaded file ID: {file_id}")
        pdf_summary(file_id)


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
        content="Summarize the key points from this PDF in 500 words or less.",
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
            for msg in messages.data:
                print(msg.content[0].text.value)  #  Extract the assistant's response
            break
        print("Waiting for response...")
        time.sleep(2)


download_file()