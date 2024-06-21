import openai
import pandas as pd

# Load your API key from an environment variable or secret management service
openai.api_key = 'your-openai-api-key'

# Define few-shot examples
examples = [
    {
        "description": "Looking for a video editor with experience in Adobe Premiere Pro to create marketing videos for social media.",
        "score": 9,
        "justification": "This job matches my skills in video editing and experience with Adobe Premiere Pro, and the marketing focus aligns with my interests."
    },
    {
        "description": "Seeking a graphic designer to create logos and branding materials for a new startup.",
        "score": 5,
        "justification": "While I have experience in graphic design, logo creation is not my primary expertise. However, branding materials are within my skill set."
    },
    {
        "description": "Need a virtual assistant to handle data entry and customer support tasks for an e-commerce business.",
        "score": 6,
        "justification": "I have experience in data entry and customer support, but the e-commerce industry is not my main area of expertise."
    }
]

# Function to create a single prompt for an example
def create_single_prompt(description, criteria):
    return f"Evaluate the following job description based on these criteria: {criteria}.\n\nJob Description: {description}\nScore: \nJustification: "

# Function to evaluate a single job description using separate prompts for each example
def evaluate_job_multi_prompt(description, examples, criteria):
    responses = []
    for example in examples:
        prompt = create_single_prompt(example['description'], criteria)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a job evaluator."},
                {"role": "user", "content": prompt}
            ]
        )
        responses.append(response.choices[0].message['content'].strip())
    
    new_prompt = create_single_prompt(description, criteria)
    new_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a job evaluator."},
            {"role": "user", "content": new_prompt}
        ]
    )
    
    responses.append(new_response.choices[0].message['content'].strip())
    return responses

# Load job descriptions from your filtered dataset
jobs_df = pd.read_excel('filtered_jobs.xlsx')

# Define your criteria
criteria = "Relevance to my skills, industry focus, project type, and budget or hourly rate"

# Evaluate jobs using multi-prompt approach
jobs_df['evaluations'] = jobs_df['description'].apply(lambda x: evaluate_job_multi_prompt(x, examples, criteria))

# Parse and aggregate the evaluations to get scores and justifications
def parse_evaluations(evaluations):
    scores = []
    justifications = []
    for eval_text in evaluations:
        parts = eval_text.split('-')
        if len(parts) == 2:
            score, justification = parts
            scores.append(int(score.strip()))
            justifications.append(justification.strip())
    return scores, justifications

jobs_df['scores'], jobs_df['justifications'] = zip(*jobs_df['evaluations'].apply(parse_evaluations))

# Calculate the mean score for each job
jobs_df['mean_score'] = jobs_df['scores'].apply(lambda x: sum(x) / len(x) if x else 0)

# Select top 7 jobs
top_jobs = jobs_df.nlargest(7, 'mean_score')

# Output the top jobs
print(top_jobs[['description', 'mean_score', 'justifications']])

# Save the top jobs to a new Excel file
top_jobs.to_excel('top_jobs.xlsx', index=False)