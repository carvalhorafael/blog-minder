import requests
from crewai_tools import tool

@tool
def fetch_wordpress_posts(url: str) -> str:
    """
    Fetches all posts from a WordPress blog.
    
    Args:
    url (str): The base URL of the WordPress blog.
    
    Returns:
    str: A string containing all the blog posts.
    """
    response = requests.get(f"{url}/wp-json/wp/v2/posts?per_page=100")
    if response.status_code != 200:
        return f"Failed to fetch posts: {response.status_code}"
    
    posts = response.json()
    post_texts = []
    for post in posts:
        post_texts.append(post['title']['rendered'] + "\n" + post['content']['rendered'])
    
    return "\n\n".join(post_texts)
