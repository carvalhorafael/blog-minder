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

    print(f"Starting fetch wordpress posts from: {url}")

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
    }

    response = requests.get(f"{url}/wp-json/wp/v2/posts?per_page=10", headers=headers)
    # response = requests.get(f"{url}/wp-json/wp/v2/posts", params={"per_page": 100})
    if response.status_code != 200:
        return f"Failed to fetch posts: {response.status_code}"
    

    # response = requests.get(url, headers=headers)
    # print(f"Posts HERE: {response.content}")

    posts = response.json()
    post_texts = []
    for post in posts:
        post_texts.append(post['title']['rendered'] + "\n" + post['content']['rendered'])
    
    return "\n\n".join(post_texts)