#!/usr/bin/env python
import sys
import os
import yaml
from blog_minder.blog_integrity_crew import BlogIntegrityCrew
from blog_minder.content_consolidation_crew import ContentConsolidationCrew


def run():
    duplicate_and_similar_posts_path = os.environ["LIST_OF_DUPLICATE_POSTS_PATH"]
    blog_url = os.environ["BLOG_URL"]

    # Crew to download, analyze and identify duplicate and similar posts
    # BlogIntegrityCrew().crew().kickoff(inputs={
    #     'blog_url': blog_url,
    #     'blog_posts_file_path': 'tmp/blog_posts.csv',
    #     'result_of_analysis_path': duplicate_and_similar_posts_path
    # })

    # Crew to consolidate duplicate posts and improve their content
    if os.path.isfile(duplicate_and_similar_posts_path):    
        with open(duplicate_and_similar_posts_path, 'r') as yaml_file:
            duplicate_and_similar_posts = yaml.safe_load(yaml_file)

        for duplicate_and_similar_post in duplicate_and_similar_posts['duplicates']:
            duplicate_and_similar_post['blog_url'] = blog_url
            ContentConsolidationCrew().crew().kickoff(inputs=duplicate_and_similar_post)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs"}
    try:
        BlogIntegrityCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
