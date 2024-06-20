import pandas as pd

# Load datasets
feed_logs = pd.read_excel('feed_logs.xlsx')
rss_feed = pd.read_excel('rss_feed.xlsx')

# Merge datasets on 'run_id' to add 'rss_url_id' to 'rss_feed'
rss_feed = pd.merge(rss_feed, feed_logs[['run_id', 'rss_url_id']], on='run_id', how='left')

# Create 'Hourly Average' column
def parse_hourly_range(hourly_range):
    if pd.isna(hourly_range):
        return None
    if isinstance(hourly_range, (int, float)):
        return (hourly_range, hourly_range)
    try:
        low, high = hourly_range.strip('$').split('-')
        return (float(low), float(high))
    except ValueError:
        return None

rss_feed['Hourly Average'] = rss_feed['Hourly Range'].apply(parse_hourly_range)
rss_feed['Hourly Average'] = rss_feed['Hourly Average'].apply(lambda x: (x[0] + x[1]) / 2 if x else None)

# Convert Budget column to numeric, setting errors='coerce' to handle non-numeric values
rss_feed['Budget'] = pd.to_numeric(rss_feed['Budget'], errors='coerce')

# Define filtering criteria
hourly_rate_threshold = 15
budget_threshold = 200

# Filter jobs based on the new thresholds
filtered_jobs = rss_feed[
    (rss_feed['Hourly Average'].isna() & rss_feed['Budget'].isna()) | 
    (rss_feed['Hourly Average'] >= hourly_rate_threshold) |
    (rss_feed['Budget'] >= budget_threshold)
]

# Save the filtered data to a new Excel file
filtered_jobs.to_excel('filtered_jobs.xlsx', index=False)

print("Filtered data saved to 'filtered_jobs.xlsx'")