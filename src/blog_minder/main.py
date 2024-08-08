#!/usr/bin/env python
import sys
import os
import yaml
import sqlite3
from blog_minder.content_integrity_crew import ContentIntegrityCrew
from blog_minder.content_consolidation_crew import ContentConsolidationCrew
from blog_minder.content_performance_analyzer_crew import ContentPerformanceAnalyzerCrew
from blog_minder.content_enhancement_crew import ContentEnhancementCrew



# Check if a file exists
def find_files(partial_file_name, folder_path):
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            if partial_file_name in file_name:
                return True
    return False


def run():
    blog_posts_csv_file_path = os.environ["BLOG_POSTS_CSV_FILE_PATH"]
    duplicate_and_similar_posts_path = os.environ["LIST_OF_DUPLICATE_POSTS_PATH"]
    blog_url = os.environ["BLOG_URL"]
    posts_to_improve_database_path = os.environ["BLOG_POSTS_TO_IMPROVE_DB_PATH"]
    posts_to_improve_table_name = 'posts_to_improve'

    print('\n\nStarting Blog Minder...')


    # #
    # # Check if is necessary put Content Integrity Crew to work
    # #
    # print('\n\nChecking if is necessary to analyze the integrity of posts...')
    # if not find_files('duplicate_and_similar', 'tmp'):
    #     print('Yes. Its necessary. Putting Content Integrity Crew to work.')
    #     ContentIntegrityCrew().crew().kickoff(inputs={
    #         'blog_url': blog_url,
    #         'blog_posts_file_path': blog_posts_csv_file_path,
    #         'result_of_analysis_path': duplicate_and_similar_posts_path
    #     })
    # else:
    #     print('It is not necessary to check the integrity of posts.')


    # #
    # # Check if is necessary start Content Consolidation Crew avaliation
    # #
    # print('\n\nChecking if is possible to consolidate posts...')
    # if os.path.isfile(duplicate_and_similar_posts_path):    
    #     with open(duplicate_and_similar_posts_path, 'r') as yaml_file:
    #         duplicate_and_similar_posts = yaml.safe_load(yaml_file)

    #     print('\nChecking DUPLICATE posts to consolidate...')
    #     for duplicate_and_similar_post in duplicate_and_similar_posts['duplicates']:
            
    #         # Check is is necessary put Content Consolidation Crew to work
    #         duplicate_hash = duplicate_and_similar_post['duplicate_hash']
    #         if not find_files(f'{duplicate_hash}_winner_new', 'tmp/posts'):
    #             print(f'\nPutting Content Consolidation Crew to work on: {duplicate_hash}\n\n')
    #             duplicate_and_similar_post['blog_url'] = blog_url
    #             content_consolidation_crew = ContentConsolidationCrew(inputs=duplicate_and_similar_post)
    #             content_consolidation_crew.crew().kickoff(inputs=duplicate_and_similar_post)
    #         else:
    #             print(f'Duplicate {duplicate_hash} has already been consolidated.')
    # else:
    #     print('\nIt is not possible to consolidate posts.')

    
    # #
    # #  Download, analyze and mark posts to be improved
    # # 
    # print('\n\nAnalyzing and marking posts for improvement...')
    # ContentPerformanceAnalyzerCrew().crew().kickoff(inputs={
    #     'blog_url': blog_url,
    #     'database_path': posts_to_improve_database_path,
    #     'table_name': posts_to_improve_table_name
    # })

    
    #
    #  Starts Content Enhancement Crew for each post that needs to be improved
    # 
    conn = sqlite3.connect(posts_to_improve_database_path)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    cur = conn.cursor()
    cur.execute(f'''
        SELECT * FROM {posts_to_improve_table_name}
        WHERE to_improve = 1
    ''')
    posts = cur.fetchall()
    conn.close()
    for post in posts:
        inputs = {
            'blog_url': blog_url,
            'database_path': posts_to_improve_database_path,
            'table_name': posts_to_improve_table_name,
            'post_id': post['id'],
            'post_link': post['link'],
            'keyword': post['keyword']
        }    
        content_enhancement_crew = ContentEnhancementCrew(inputs=inputs)
        content_enhancement_crew.crew().kickoff(inputs=inputs)
        

# pode deletar o que está comentado daqui para baixo        
        # ContentEnhancementCrew().crew().kickoff(inputs={
        #     'blog_url': blog_url,
        #     'post_id': post['id'],
        #     'link': post['link'],
        #     'keyword': post['keyword']
        # })


    # conn = sqlite3.connect(posts_to_improve_database_path)
    # cur = conn.cursor()
    # cur.execute(f'''
    #     ALTER TABLE {posts_to_improve_table_name}
    #     ADD COLUMN was_improved INTEGER DEFAULT 0
    # ''')


    # inputs = {
    #     'blog_url': blog_url,
    #     'database_path': posts_to_improve_database_path,
    #     'table_name': posts_to_improve_table_name,
    #     'post_id': 6470,
    #     'post_link': 'https://rafaelcarvalho.tv/profissoes-do-futuro-o-que-esperar-para-2030/',
    #     'keyword': 'profissoes do futuro o que esperar para 2030'
    # }
    # content_enhancement_crew = ContentEnhancementCrew(inputs=inputs)
    # content_enhancement_crew.crew().kickoff(inputs=inputs)
    

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs"}
    try:
        BlogIntegrityCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
