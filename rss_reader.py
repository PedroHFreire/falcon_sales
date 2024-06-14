import os
import requests
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
import pytz

def fetch_and_log_rss_feeds(rss_urls_path, feed_logs_path, data_lake_folder):
    """
    Fetch and log RSS feeds from multiple URLs.
    
    Args:
    rss_urls_path (str): Path to the spreadsheet containing RSS URLs.
    feed_logs_path (str): Path to the spreadsheet for logging feed runs.
    data_lake_folder (str): Folder to save the raw XML files.
    """
    # Read the RSS feed URLs from the spreadsheet
    rss_urls_df = pd.read_excel(rss_urls_path)

    # Ensure the data_lake_folder exists
    os.makedirs(data_lake_folder, exist_ok=True)

    # Initialize an empty list to store log entries
    log_entries = []

    # Check if the feed_logs file exists
    if os.path.exists(feed_logs_path):
        # Read the existing logs
        feed_logs_df = pd.read_excel(feed_logs_path)
    else:
        # Create an empty DataFrame if the file does not exist
        feed_logs_df = pd.DataFrame(columns=['run_id', 'rss_url_id', 'date', 'response', 'item_count'])

    # Get the next run_id
    next_run_id = feed_logs_df['run_id'].max() + 1 if not feed_logs_df.empty else 1

    # Define the UTC timezone
    utc = pytz.UTC

    # Loop through each RSS feed URL
    for index, row in rss_urls_df.iterrows():
        feed_id = row['id']
        rss_url = row['rss_url']
        # Fetch the RSS feed data
        response = requests.get(rss_url)
        date_now = datetime.now(utc).strftime("%Y-%m-%d %H:%M:%S")
        item_count = 0
        new_items = []

        if response.status_code == 200:
            rss_content = response.content
            # Parse the XML to count the number of items and filter new items
            root = ET.fromstring(rss_content)
            items = root.findall('.//item')

            # Get the latest publication date from the previous runs for this URL
            latest_pub_date_str = feed_logs_df.loc[feed_logs_df['rss_url_id'] == feed_id, 'date'].max()
            latest_pub_date = datetime.min.replace(tzinfo=utc) if pd.isna(latest_pub_date_str) else datetime.strptime(latest_pub_date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)

            print(f"Latest publication date for feed_id {feed_id}: {latest_pub_date}")

            for item in items:
                pub_date_str = item.find('pubDate').text
                pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z").astimezone(utc)  # Convert to UTC

                print(f"Item publication date: {pub_date}, Latest recorded date: {latest_pub_date}")

                if pub_date > latest_pub_date:
                    new_items.append(item)
                    item_count += 1

            # Save the new items to a file named after the run_id
            if new_items:
                output_path = os.path.join(data_lake_folder, f'{next_run_id}.xml')
                new_rss_feed = ET.Element("rss")
                channel = ET.SubElement(new_rss_feed, "channel")
                for new_item in new_items:
                    channel.append(new_item)
                tree = ET.ElementTree(new_rss_feed)
                tree.write(output_path)
                print(f"New RSS feed data for run_id {next_run_id} has been written to {output_path}")
            else:
                print(f"No new items for run_id {next_run_id}")

        else:
            print(f"Failed to fetch the RSS feed for {feed_id}. Status code: {response.status_code}")

        # Append log entry
        log_entries.append({
            'run_id': next_run_id,
            'rss_url_id': feed_id,
            'date': date_now,
            'response': response.status_code,
            'item_count': item_count
        })
        next_run_id += 1

    # Create a DataFrame for log entries
    logs_df = pd.DataFrame(log_entries)

    # Append the new logs to the existing logs
    combined_logs_df = pd.concat([feed_logs_df, logs_df], ignore_index=True)

    # Save the logs to the feed_logs spreadsheet
    combined_logs_df.to_excel(feed_logs_path, index=False)
    print(f"Feed logs have been updated at {feed_logs_path}")

# Example usage
rss_urls_path = 'rss_urls.xlsx'
feed_logs_path = 'feed_logs.xlsx'
data_lake_folder = 'data_lake'
fetch_and_log_rss_feeds(rss_urls_path, feed_logs_path, data_lake_folder)