from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Access your API token
access_token = os.getenv('ACCESS_TOKEN')

# Define the API endpoint
url = "https://api.upwork.com/v3/jobs/search"

# Set the headers with your authorization token
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Define the search parameters, including location filter for the US
params = {
    'q': 'video editing',
    'location': 'United States'
}

# Make the GET request to the Upwork API
response = requests.get(url, headers=headers, params=params)

# Check the response status and print the result
if response.status_code == 200:
    print(response.json())  # Prints the job data returned from the API
else:
    print(f"Failed to retrieve data: {response.status_code}")