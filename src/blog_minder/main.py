#!/usr/bin/env python
import sys
import os
import json
from blog_minder.blog_integrity_crew import BlogIntegrityCrew
from blog_minder.content_consolidation_crew import ContentConsolidationCrew


def run():
    duplicate_and_similar_posts_path = 'tmp/duplicate_and_similar_blog_posts.json'

    blog_integrity_crew_inputs = {
        'blog_url': 'https://rafaelcarvalho.tv',
        'blog_posts_file_path': 'tmp/blog_posts.csv',
        'result_of_analysis_path': duplicate_and_similar_posts_path
    }

    BlogIntegrityCrew().crew().kickoff(inputs=blog_integrity_crew_inputs)

    if os.path.isfile(duplicate_and_similar_posts_path):    
        with open(duplicate_and_similar_posts_path, 'r') as json_file:
            duplicate_and_similar_posts = json.load(json_file)

        blog_url = 'https://rafaelcarvalho.tv'
        for dataset in duplicate_and_similar_posts['duplicates']:
            dataset['blog_url'] = blog_url
        ContentConsolidationCrew().crew().kickoff_for_each(inputs=duplicate_and_similar_posts['duplicates'])



def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs"}
    try:
        BlogIntegrityCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
