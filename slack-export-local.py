#!/usr/bin/python

import sys
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def download_file(url, root_dir, html_file_path):
    """Download a file from a URL into the specified directory structure if it matches allowed domains."""
    allowed_domains = ['files.slack.com', 'avatars.slack-edge.com', 'secure.gravatar.com']
    parsed_url = urlparse(url)
    
    # Check if the URL's domain is in the list of allowed domains
    if parsed_url.netloc not in allowed_domains:
        return url  # Return the original URL if it's not from an allowed domain
    
    # Create a path based on the URL structure
    file_path = os.path.join(root_dir, parsed_url.netloc, parsed_url.path.strip("/"))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Creat the relative path to the html file
    file_path_relative = os.path.relpath(file_path, os.path.dirname(html_file_path))

    # Skip downloading if the file already exists
    if os.path.exists(file_path):
        return file_path_relative

    # Download and save the file
    response = requests.get(url)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    
    return file_path_relative

def update_html_file(html_file_path, root_dir):
    """Update HTML file to download and reference local copies of external resources."""
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Handle img tags with src attributes
    for img_tag in soup.find_all('img'):
        original_url = img_tag.get('src')
        if original_url:
            new_path = download_file(original_url, root_dir, html_file_path)
            img_tag['src'] = new_path
    
    # Handle tags with href attributes (e.g., a, link)
    for href_tag in soup.find_all(href=True):
        original_url = href_tag.get('href')
        if original_url:
            new_path = download_file(original_url, root_dir, html_file_path)
            href_tag['href'] = new_path
    
    # Write the updated HTML back to a file
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

def scan_and_update_html_files(channel_dir, root_dir):
    """Scan each folder in the channel directory and update the index.html file found within."""
    for subdir, dirs, files in os.walk(channel_dir):
        # Print message to indicate the current directory being processed
        print(f"Processing directory: {subdir}")
        for file in files:
            if file == 'index.html':
                html_file_path = os.path.join(subdir, file)
                update_html_file(html_file_path, root_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python slack-export-local.py <root_directory_path>")
        sys.exit(1)

    root_directory_path = sys.argv[1]
    channel_dir = os.path.join(root_directory_path, "channel")
    root_dir = os.path.join(root_directory_path, "attachments")

    scan_and_update_html_files(channel_dir, root_dir)