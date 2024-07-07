import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def download_file(url, root_dir):
    """Download a file from a URL into the specified directory structure if it matches allowed domains."""
    allowed_domains = ['files.slack.com', 'avatars.slack-edge.com', 'secure.gravatar.com']
    parsed_url = urlparse(url)
    
    # Check if the URL's domain is in the list of allowed domains
    if parsed_url.netloc not in allowed_domains:
        return url  # Return the original URL if it's not from an allowed domain
    
    # Create a path based on the URL structure
    file_path = os.path.join(root_dir, parsed_url.netloc, parsed_url.path.strip("/"))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Download and save the file
    response = requests.get(url)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path

def update_html_file(html_file_path, root_dir):
    """Update HTML file to download and reference local copies of external resources."""
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Find all img tags and any other tags that might reference external resources
    for img_tag in soup.find_all('img'):
        original_url = img_tag['src']
        # Download the file and get the new path if it's from an allowed domain
        new_path = download_file(original_url, root_dir)
        # Update the src attribute to point to the local file or keep it unchanged
        img_tag['src'] = new_path
    
    # Write the updated HTML back to a file
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

# Example usage
html_file_path = '/path/to/html_output/channel/announcements/index.html'
root_dir = '/path/to/html_output/attachments'
update_html_file(html_file_path, root_dir)