#!/usr/bin/env python
import sys
from blog_minder.blog_integrity_crew import BlogIntegrityCrew
from blog_minder.content_consolidation_crew import ContentConsolidationCrew


def run():
    blog_integrity_crew_inputs = {
        'blog_url': 'https://rafaelcarvalho.tv',
        'blog_posts_file_path': 'tmp/blog_posts.csv',
        'result_of_analysis_path': 'tmp/duplicate_and_silimar_blog_posts.json'
    }
    content_consolidation_crew_inputs = {
        'blog_url': 'https://rafaelcarvalho.tv'
    }

    BlogIntegrityCrew().crew().kickoff(inputs=blog_integrity_crew_inputs)
    ContentConsolidationCrew().crew().kickoff(inputs=content_consolidation_crew_inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs"}
    try:
        BlogIntegrityCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
