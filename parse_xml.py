import os
import shutil
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd

def parse_rss_feed(file_path):
    """
    Parse an RSS feed XML file and return the extracted data as a list of dictionaries.
    
    Args:
    file_path (str): Path to the RSS feed XML file.
    
    Returns:
    list: A list of dictionaries containing the extracted data.
    """
    try:
        # Load the RSS feed data from the file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Define the namespace
        namespace = {'content': 'http://purl.org/rss/1.0/modules/content/'}

        # Extract all items
        items = root.findall('.//item')

        # Function to extract additional fields from the HTML description
        def extract_field(description, field):
            start_tag = f"{field}</b>:"
            if start_tag in description:
                start_idx = description.find(start_tag) + len(start_tag)
                end_idx = description.find('<br', start_idx)
                return description[start_idx:end_idx].strip()
            return ""

        # Extract relevant information from each item
        data = []
        for item in items:
            title = item.find('title').text
            link = item.find('link').text
            description_html = item.find('description').text
            content_html = item.find('content:encoded', namespace).text if item.find('content:encoded', namespace) is not None else ''
            pubDate = item.find('pubDate').text
            guid = item.find('guid').text
            
            # Parse the HTML content in the description
            soup = BeautifulSoup(description_html, 'html.parser')
            description_text = soup.get_text(separator='\n')
            
            hourly_range = extract_field(description_html, "Hourly Range")
            budget = extract_field(description_html, "Budget")
            posted_on = extract_field(description_html, "Posted On")
            category = extract_field(description_html, "Category")
            skills = extract_field(description_html, "Skills")
            country = extract_field(description_html, "Country")

            data.append({
                'File Name': os.path.splitext(os.path.basename(file_path))[0],  # Add the file name without extension as the first column
                'Title': title,
                'Link': link,
                'Description': description_text,
                'Content': content_html,
                'Publication Date': pubDate,
                'GUID': guid,
                'Hourly Range': hourly_range,
                'Budget': budget,
                'Posted On': posted_on,
                'Category': category,
                'Skills': skills,
                'Country': country
            })

        return data, None  # Return the data and no error message
    except Exception as e:
        return None, str(e)  # Return no data and the error message

# Parse all XML files in the data_lake folder
data_lake_folder = 'data_lake'
parsed_folder = os.path.join(data_lake_folder, 'parsed')
output_file = 'rss_feed.xlsx'

# Ensure the parsed folder exists
os.makedirs(parsed_folder, exist_ok=True)

# Collect all data
all_data = []

# Loop through all XML files in the data_lake folder
for xml_file in os.listdir(data_lake_folder):
    if xml_file.endswith('.xml'):
        file_path = os.path.join(data_lake_folder, xml_file)
        data, error = parse_rss_feed(file_path)
        if data:
            all_data.extend(data)
            # Move the file to the parsed folder if there were no errors
            shutil.move(file_path, os.path.join(parsed_folder, xml_file))
        else:
            print(f"Failed to parse {xml_file}: {error}")

# Check if the output file exists
if os.path.exists(output_file):
    # Read the existing data
    existing_df = pd.read_excel(output_file)
    # Append the new data
    df = pd.DataFrame(all_data)
    combined_df = pd.concat([existing_df, df], ignore_index=True)
else:
    # If the file does not exist, create a new DataFrame
    combined_df = pd.DataFrame(all_data)

# Output to a single spreadsheet
combined_df.to_excel(output_file, index=False)

print(f"All data has been written to {output_file}")