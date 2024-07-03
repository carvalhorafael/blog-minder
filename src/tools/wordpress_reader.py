import os
import requests
import base64
import csv
from crewai_tools import tool

@tool
def fetch_wordpress_posts(blog_url: str) -> str:
    """
    Fetches all posts from a WordPress blog and store in a CSV file.
    
    Args:
    blog_url (str): The base URL of the WordPress blog.
    
    Returns:
    str: A string containing the CVS file path.
    """

    if os.path.isfile(os.environ["POSTS_CSV_FILE_PATH"]):
        return os.environ["POSTS_CSV_FILE_PATH"]

    credentials = os.environ["WORDPRESS_USER"] + ':' + os.environ["WORDPRESS_APP_PASSWORD"]
    token = base64.b64encode(credentials.encode())
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Authorization': 'Basic ' + token.decode('utf-8')
    }
    page = 1
    per_page = 100

    
    # print('\n\n PASSEI POR AQUI \n\n')

    with open(os.environ["POSTS_CSV_FILE_PATH"], 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'title', 'keyword']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


        # print('\n\n PASSEI POR AQUI: ANTES \n\n')

        while True:
            # print('\n\n PASSEI POR AQUI: DEPOIS WHILE \n\n')


            # Tá com erro aqui, não executa essa request se estiver com URL como variável
            response = requests.get(f'{os.environ["BLOG_URL"]}/wp-json/wp/v2/posts', headers=headers, params={'per_page': per_page, 'page': page})
            data = response.json()

            # print('\n\n PASSEI POR AQUI: DEPOIS REQUEST \n\n')

            # Break when finish all pages and receive an error
            if ((response.status_code == 400) and (data['code'] == 'rest_post_invalid_page_number')):
                # return os.environ["POSTS_CSV_FILE_PATH"]
                break
            
            # Raise an error to other possible things
            if response.status_code != 200:
                raise Exception(f'Error fetching posts: {response.status_code} {response.text}')

            # Insert post information into the CSV file
            for post in data:
                keyword = post['slug'].replace('-', ' ')
                writer.writerow({'id': post['id'], 'title': post['title']['rendered'], 'keyword': keyword})

            # posts.extend(data)
            page += 1
        
    return os.environ["POSTS_CSV_FILE_PATH"]