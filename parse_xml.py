import os
import shutil
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd

def parse_rss_feed(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        namespace = {'content': 'http://purl.org/rss/1.0/modules/content/'}
        items = root.findall('.//item')

        def extract_field(description, field):
            start_tag = f"{field}</b>:"
            if start_tag in description:
                start_idx = description.find(start_tag) + len(start_tag)
                end_idx = description.find('<br', start_idx)
                return description[start_idx:end_idx].strip()
            return ""

        data = []
        for item in items:
            title = item.find('title').text
            link = item.find('link').text
            description_html = item.find('description').text
            content_html = item.find('content:encoded', namespace).text if item.find('content:encoded', namespace) is not None else ''
            pubDate = item.find('pubDate').text
            guid = item.find('guid').text
            soup = BeautifulSoup(description_html, 'html.parser')
            description_text = soup.get_text(separator='\n')
            hourly_range = extract_field(description_html, "Hourly Range")
            budget = extract_field(description_html, "Budget")
            posted_on = extract_field(description_html, "Posted On")
            category = extract_field(description_html, "Category")
            skills = extract_field(description_html, "Skills")
            country = extract_field(description_html, "Country")

            data.append({
                'run_id': os.path.splitext(os.path.basename(file_path))[0],
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

        return data, None
    except Exception as e:
        return None, str(e)

data_lake_folder = 'data_lake'
parsed_folder = os.path.join(data_lake_folder, 'parsed')
output_file = 'rss_feed.xlsx'
os.makedirs(parsed_folder, exist_ok=True)
all_data = []

for xml_file in os.listdir(data_lake_folder):
    if xml_file.endswith('.xml'):
        file_path = os.path.join(data_lake_folder, xml_file)
        print(f"Parsing file: {file_path}")
        data, error = parse_rss_feed(file_path)
        if data:
            all_data.extend(data)
            target_path = os.path.join(parsed_folder, xml_file)
            print(f"Moving {file_path} to {target_path}")
            shutil.move(file_path, target_path)
            print(f"Moved {file_path} to {target_path}")
        else:
            print(f"Failed to parse {xml_file}: {error}")

if os.path.exists(output_file):
    existing_df = pd.read_excel(output_file)
    df = pd.DataFrame(all_data)
    combined_df = pd.concat([existing_df, df], ignore_index=True)
else:
    combined_df = pd.DataFrame(all_data)

combined_df.to_excel(output_file, index=False)
print(f"All data has been written to {output_file}")