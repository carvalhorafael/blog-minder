#!/usr/bin/env python
import sys
from blog_minder.crew import BlogMinderCrew


def run():
    inputs = {
        'blog_url': 'https://rafaelcarvalho.tv',
        'blog_posts_file_path': 'tmp/blog_posts.csv',
        'result_of_analysis_path': 'tmp/duplicate_and_silimar_blog_posts.json'
    }
    BlogMinderCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs"}
    try:
        BlogMinderCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
