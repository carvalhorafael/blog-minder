from collections import defaultdict
from crewai_tools import tool

@tool
def keyword_analyzer(posts: str) -> str:
    """
    Analyzes the posts to identify duplicate keywords.
    
    Args:
    posts (str): The content of all posts.
    
    Returns:
    str: A report of posts with duplicate keywords and their frequency.
    """
    # Example implementation, replace with actual keyword analysis
    keywords = defaultdict(int)
    for post in posts.split("\n\n"):
        for word in post.split():
            keywords[word.lower()] += 1
    
    duplicates = {k: v for k, v in keywords.items() if v > 1}
    return str(duplicates)
