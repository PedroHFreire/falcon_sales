import openai
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Load your API key from an environment variable
openai.api_key = os.getenv('OPENAI_KEY')

# Define the filtering criteria
criteria = (
    "You are a job filter. Your task is to evaluate job descriptions based on the following criteria:\n"
    "- Includes video editing tasks such as cutting footage, color correction, audio editing, animations (especially motion graphics), screenshare videos, or voice overs for faceless videos.\n"
    "- Does not require the team to be physically present to film with the client or to film themselves presenting a product.\n"
    "- Does not require immediate turnaround (within 24/48 hours from job posting).\n"
    "- Involves using video editing software, preferably Adobe Premiere Pro.\n"
    "- The job description is in Portuguese or English.\n"
    "Respond with 'yes' or 'no' indicating if the job fits these criteria."
)

# Function to create the user prompt with title and description
def create_user_prompt(title, description):
    return f"Title: {title}\nDescription: {description}\nResponse: "

# Function to filter jobs using GPT-3.5-turbo and log the conversation
def filter_jobs(title, description, system_message):
    user_prompt = create_user_prompt(title, description)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
    )
    reply = response.choices[0].message['content'].strip()
    log_entry = {
        "title": title,
        "description": description,
        "prompt": user_prompt,
        "response": reply
    }
    conversation_log.append(log_entry)
    return reply.lower() == 'yes'

# Load job descriptions from your dataset
jobs_df = pd.read_excel('filtered_jobs.xlsx')

# Initialize a list to store the conversation logs
conversation_log = []

# Filter jobs using GPT-3.5-turbo
jobs_df['initial_fit'] = jobs_df.apply(lambda x: filter_jobs(x['title'], x['description'], criteria), axis=1)

# Keep only jobs that fit the initial criteria
filtered_jobs_df = jobs_df[jobs_df['initial_fit'] == True]

# Save the initially filtered jobs to a new Excel file
filtered_jobs_df.to_excel('llm_filtered_jobs.xlsx', index=False)

# Save the conversation log to a CSV file
conversation_log_df = pd.DataFrame(conversation_log)
conversation_log_df.to_csv('filter_conversation_log.csv', index=False)

print(f"LLM filtered jobs saved to 'llm_filtered_jobs.xlsx'. Total jobs: {filtered_jobs_df.shape[0]}")
print(f"Conversation log saved to 'conversation_log.csv'.")