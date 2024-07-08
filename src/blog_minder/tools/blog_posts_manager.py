import os
import requests
import base64
import csv
from crewai_tools import BaseTool


wordpress_credentials = os.environ["WORDPRESS_USER"] + ':' + os.environ["WORDPRESS_APP_PASSWORD"]
wordpress_token = base64.b64encode(wordpress_credentials.encode())
wordpress_header = {
    'Authorization': 'Basic ' + wordpress_token.decode('utf-8'),
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
    'Accept': 'application/json'
}

class FetchPosts(BaseTool):
    name: str = "Fetch posts"
    description: str = (
        "Fetches all posts from the WordPress blog {blog_url} and store in a CSV file at {blog_posts_file_path}."
    )

    def _run(self, blog_url: str, blog_posts_file_path: str) -> str:
        if os.path.isfile(blog_posts_file_path):
            return blog_posts_file_path

        page = 1
        per_page = 100

        with open(blog_posts_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'title', 'link', 'seo_keyword']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            while True:
                response = requests.get(f'{blog_url}/wp-json/wp/v2/posts', headers=wordpress_header, params={'per_page': per_page, 'page': page})
                data = response.json()

                # Break when finish all pages and receive an error
                if ((response.status_code == 400) and (data['code'] == 'rest_post_invalid_page_number')):
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
                        'seo_keyword': post['slug'].replace('-', ' ')
                        })

                # posts.extend(data)
                page += 1
            
        return blog_posts_file_path
    

class FetchPostContent(BaseTool):
    name: str = "Fetch post content."
    description: str = (
        "Fetch a post identified by {post_id} from the WordPress blog {blog_url} and return its content."
    )

    def _run(self, blog_url: str, post_id: int) -> str:        
        response = requests.get(f'{blog_url}/wp-json/wp/v2/posts/{post_id}', headers=wordpress_header)
        
        # Raise an error to other possible things
        if response.status_code != 200:
            raise Exception(f'Error fetching posts: {response.status_code} {response.text}')
        
        data = response.json()
        post_content = data['content']['rendered']

        return post_content
    
class UpdatePostStatus(BaseTool):
    name: str = "Update status of a blog post."
    description: str = (
        "Update status of a Wordpress blog post hosted at {blog_url} and return a string with the reponse status code."
    )

    def _run(self, blog_url: str, post_id: int, post_status: str) -> str:
        # Other possible status: 'draft', 'pending', 'private', etc.
        new_post_status = {
            'status': post_status  
        }
        response = requests.put(f'{blog_url}/wp-json/wp/v2/posts/{post_id}', json=new_post_status, headers=wordpress_header)

        # Raise an error to other possible things
        if response.status_code != 200:
            raise Exception(f'Error fetching posts: {response.status_code} {response.text}')
        
        return response.status_code