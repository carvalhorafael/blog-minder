import os
import requests
import base64
import csv
import re
import sqlite3
from datetime import datetime
from typing import List
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
                response = requests.get(f'{blog_url}/wp-json/wp/v2/posts', headers=wordpress_header, params={'per_page': per_page, 'page': page, 'status': 'publish'})
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
    

class FetchPostsSaveToDatabase(BaseTool):
    name: str = "Fetch posts and save to a Database."
    description: str = (
        "Fetches all posts from the WordPress blog {blog_url} and store in a database at {database_path} in the table {table_name}."
    )

    def data_exists(self, cur, table_name, id):
        query = f'SELECT 1 FROM {table_name} WHERE id = ?'
        cur.execute(query, (id,))
        return cur.fetchone() is not None
    
    def create_table_if_necessary(self, database_path: str, table_name: str) -> None:
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        # create the table to store posts if not exists
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER,
                link TEXT,
                title TEXT,
                keyword TEXT,            
                original_content TEXT,
                new_content TEXT,
                clicks INTEGER,
                impressions INTEGER,
                ctr REAL,
                position REAL,
                updated_at TEXT,
                inserted_at TEXT,
                is_human_writer INTEGER DEFAULT 0,
                to_improve INTEGER DEFAULT 0
            )
        ''')
        conn.close()
    
    # check if a post was written by humans and should not be improved by the crew
    def is_human_writer(self, tags: List[int]) -> int:
        if int(os.environ["TAG_ID_HUMAN_WRITER_POSTS"]) in tags:
            return 1
        else:
            return 0


    def _run(self, blog_url: str, database_path: str, table_name: str) -> str:        
        # configure pagination and posts per page to wordpress request
        page = 1
        per_page = 100

        # creates the table to store posts if necessary
        self.create_table_if_necessary(database_path, table_name)
        
        # starts the coneection with database
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()

        while True:
            response = requests.get(f'{blog_url}/wp-json/wp/v2/posts', headers=wordpress_header, params={'per_page': per_page, 'page': page, 'status': 'publish'})
            data = response.json()

            # Break when finish all pages and receive an error
            if ((response.status_code == 400) and (data['code'] == 'rest_post_invalid_page_number')):
                break
            
            # Raise an error to other possible things
            if response.status_code != 200:
                raise Exception(f'Error fetching posts: {response.status_code} {response.text}')
            
            # Insert posts from a page into the Database
            for post in data:
                # insert only if not exists in database
                if not self.data_exists(cur, table_name, post['id']):
                    cur.execute(f'''
                        INSERT INTO {table_name} (id, link, title, keyword, original_content, updated_at, inserted_at, is_human_writer)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        post['id'], 
                        post['link'], 
                        post['title']['rendered'], 
                        post['slug'].replace('-', ' '),                    
                        post['content']['rendered'],
                        post['modified'],
                        datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                        self.is_human_writer(post['tags'])
                        ))
                    conn.commit()
                else:
                    print(f'''Post already added ID: {post['id']}. Updating is_human_writer...''')
                    cur.execute(f'''
                        UPDATE {table_name}
                        SET is_human_writer = ?
                        WHERE id = ?
                    ''', (
                        self.is_human_writer(post['tags']),
                        post['id']
                        ))
                    conn.commit()

            page += 1
            
        conn.close()
        return "Posts were saved."