import os
import requests
import base64
import csv
from crewai_tools import tool

@tool
def fetch_posts(url: str) -> str:
    """
    Fetches all posts from a WordPress blog and store in a CSV file.
    
    Args:
    url (str): The base URL of the blog.
    
    Returns:
    str: A string containing the CVS file path.
    """

    if os.path.isfile(os.environ["POSTS_CSV_FILE_PATH"]):
        return os.environ["POSTS_CSV_FILE_PATH"]

    credentials = os.environ["WORDPRESS_USER"] + ':' + os.environ["WORDPRESS_APP_PASSWORD"]
    token = base64.b64encode(credentials.encode())
    headers = {
        'Authorization': 'Basic ' + token.decode('utf-8'),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
        'Accept': 'application/json'
    }
    page = 1
    per_page = 100

    with open(os.environ["POSTS_CSV_FILE_PATH"], 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'title', 'link', 'keyword']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            response = requests.get(f'{os.environ["BLOG_URL"]}/wp-json/wp/v2/posts', headers=headers, params={'per_page': per_page, 'page': page})
            data = response.json()

            # Break when finish all pages and receive an error
            if ((response.status_code == 400) and (data['code'] == 'rest_post_invalid_page_number')):
                # return os.environ["POSTS_CSV_FILE_PATH"]
                break
            
            # Raise an error to other possible things
            if response.status_code != 200:
                raise Exception(f'Error fetching posts: {response.status_code} {response.text}')

            # Insert post information into the CSV file
            for post in data:
                writer.writerow({
                    'id': post['id'], 
                    'title': post['title']['rendered'], 
                    'link': post['link'],
                    'keyword': post['slug'].replace('-', ' ')
                    })

            # posts.extend(data)
            page += 1
        
    return os.environ["POSTS_CSV_FILE_PATH"]