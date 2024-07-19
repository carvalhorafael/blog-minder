import os
import requests
import base64
import csv
import re
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
    

class FetchAndSavePostsContent(BaseTool):
    name: str = "Fetch and save posts content."
    description: str = (
        "Fetch content of two posts identified by 'winner_id' and 'loser_id' from the WordPress blog {blog_url} and save them."
    )

    def _run(self, blog_url: str, winner_id: int, loser_id: int, duplicate_hash: str) -> str:        
        
        ## Fetch the winner post
        winner_response = requests.get(f'{blog_url}/wp-json/wp/v2/posts/{winner_id}?context=edit', headers=wordpress_header)
        # Raise an error to other possible things
        if winner_response.status_code != 200:
            raise Exception(f'Error fetching posts: {winner_response.status_code} {winner_response.text}')
        data = winner_response.json()
        winner_post_content = data['content']['raw']
        winner_post_content = re.sub(r'<!--.*?-->', '', winner_post_content, flags=re.DOTALL)

        ## Fetch the loser post
        loser_response = requests.get(f'{blog_url}/wp-json/wp/v2/posts/{loser_id}?context=edit', headers=wordpress_header)
        # Raise an error to other possible things
        if loser_response.status_code != 200:
            raise Exception(f'Error fetching posts: {loser_response.status_code} {loser_response.text}')
        data = loser_response.json()
        loser_post_content = data['content']['raw']
        loser_post_content = re.sub(r'<!--.*?-->', '', loser_post_content, flags=re.DOTALL)

        with open(f'tmp/posts/{duplicate_hash}_winner_{winner_id}.html', 'w') as file:
            file.write(winner_post_content)
        with open(f'tmp/posts/{duplicate_hash}_loser_{loser_id}.html', 'w') as file:
            file.write(loser_post_content)

        return 'Posts were saved!'
    
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
    

class SavePostContent(BaseTool):
    name: str = "Save post content."
    description: str = (
        "Save post content and return a string with the file path."
    )

    def _run(self, post_content: str, duplicate_hash: str) -> str:
        
        filepath = f'tmp/posts/{duplicate_hash}_winner_new.html' 
        
        with open(filepath, 'w') as file:
            file.write(post_content)
    
        return filepath
    

class UpdatePostContent(BaseTool):
    name: str = "Update the content of a blog post."
    description: str = (
        "Update content of a Wordpress blog post hosted at {blog_url} and return a string with the reponse status code."
    )

    def _run(self, blog_url: str, post_id: int, file_path: str) -> str:        
        if not os.path.isfile(file_path):
            raise Exception(f'File {file_path} DO NOT exist.')
        
        with open(file_path, 'r', encoding='utf-8') as file:
            post_content = file.read()
        
        post_data = {
            'content': post_content
        }
        response = requests.put(f'{blog_url}/wp-json/wp/v2/posts/{post_id}', json=post_data, headers=wordpress_header)

        # Raise an error to other possible things
        if response.status_code != 200:
            raise Exception(f'Error fetching posts: {response.status_code} {response.text}')
        
        return response.status_code