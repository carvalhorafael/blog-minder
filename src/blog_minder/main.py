#!/usr/bin/env python
import sys
import os
import yaml
from blog_minder.content_integrity_crew import ContentIntegrityCrew
from blog_minder.content_consolidation_crew import ContentConsolidationCrew


def run():
    blog_posts_csv_file_path = os.environ["BLOG_POSTS_CSV_FILE_PATH"]
    duplicate_and_similar_posts_path = os.environ["LIST_OF_DUPLICATE_POSTS_PATH"]
    blog_url = os.environ["BLOG_URL"]

    # Put Content Integrity Crew to work
    ContentIntegrityCrew().crew().kickoff(inputs={
        'blog_url': blog_url,
        'blog_posts_file_path': blog_posts_csv_file_path,
        'result_of_analysis_path': duplicate_and_similar_posts_path
    })

    # If there is a list of duplicate post files, a crew may have work
    if os.path.isfile(duplicate_and_similar_posts_path):    
        with open(duplicate_and_similar_posts_path, 'r') as yaml_file:
            duplicate_and_similar_posts = yaml.safe_load(yaml_file)

        # Put Content Consolidation Crew to work for each duplicate content
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
