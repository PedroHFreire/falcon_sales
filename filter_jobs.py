import pandas as pd
import re

# Function to calculate the middle of the hourly range
def calculate_mid_range(hourly_range):
    if pd.isna(hourly_range):
        return None
    try:
        # Remove any extra characters like $, commas, etc.
        cleaned_range = re.sub(r'[\$,]', '', hourly_range)
        # Split the range
        if '-' in cleaned_range:
            parts = cleaned_range.split('-')
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            return (low + high) / 2
        else:
            # If there's no range, just return the single value
            return float(cleaned_range.strip())
    except ValueError:
        return None

# Function to clean and convert the Budget column to numerical values
def clean_budget(budget):
    if pd.isna(budget):
        return None
    try:
        # Remove any extra characters like $, commas, etc.
        cleaned_budget = re.sub(r'[\$,]', '', budget)
        return float(cleaned_budget.strip())
    except ValueError:
        return None

def main():
    # Load the datasets
    data = pd.read_excel('rss_feed.xlsx')
    feed_logs = pd.read_excel('feed_logs.xlsx')
    
    # Merge the datasets on 'run_id'
    merged_data = data.merge(feed_logs[['run_id', 'rss_url_id']], on='run_id', how='left')
    
    # Apply the function to the Hourly Range column
    merged_data['Hourly Range Mid'] = merged_data['Hourly Range'].apply(calculate_mid_range)
    
    # Apply the function to the Budget column
    merged_data['Budget Numeric'] = merged_data['Budget'].apply(clean_budget)
    
    # Create the 'us_only' column
    merged_data['us_only'] = merged_data['rss_url_id'].apply(lambda x: 1 if x == 2 else 0)
    
    # Filter the jobs based on the criteria
    filtered_data = merged_data[
        (merged_data['Hourly Range Mid'] >= 15) |
        (merged_data['Budget Numeric'] >= 200) |
        (merged_data['Hourly Range'].isna() & merged_data['Budget'].isna())
    ]
    
    # Save the transformed dataset
    filtered_data.to_excel('filtered_dataset.xlsx', index=False)

if __name__ == '__main__':
    main()