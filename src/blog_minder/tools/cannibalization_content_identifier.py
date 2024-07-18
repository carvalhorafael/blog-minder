import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from crewai_tools import BaseTool
import yaml
import hashlib
import secrets

def generate_hash(length=9):
        random_string = secrets.token_hex(16)
        hash_object = hashlib.sha256(random_string.encode())
        hex_dig = hash_object.hexdigest()
        return hex_dig[:length]

class FindDuplicatesAndSimilarities(BaseTool):
    name: str = "Fetch duplicate and similarities on blog posts"
    description: str = (
        "Reads a CSV file at {blog_posts_file_path}, finds duplicate and similar posts then save a YAML file at {result_of_analysis_path} as result of analysis."
    )

    def _run(self, blog_posts_file_path: str, result_of_analysis_path: str) -> str:
        if not os.path.isfile(blog_posts_file_path):
            raise Exception(f'File {blog_posts_file_path} DO NOT exist.')
        
        if os.path.isfile(result_of_analysis_path):
            return result_of_analysis_path
        
        df = pd.read_csv(blog_posts_file_path)
        
        links = df['link'].tolist()
        seo_keywords = df['seo_keyword'].tolist()
        
        # Combine links and keywords for similarity check
        combined_texts = [f"{link} {seo_keyword}" for link, seo_keyword in zip(links, seo_keywords)]
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer().fit_transform(combined_texts)
        vectors = vectorizer.toarray()
        
        # Compute cosine similarity
        cosine_matrix = cosine_similarity(vectors)
        
        duplicates = []
        similarities = []
        
        for i in range(len(links)):
            for j in range(i + 1, len(links)):
                if cosine_matrix[i][j] > 0.9:  # Duplicate threshold
                    duplicate = {}
                    post01 = df.iloc[i].to_dict()
                    post02 = df.iloc[j].to_dict()
                    duplicate['duplicate_hash'] = generate_hash()
                    duplicate['post01_id'] = post01['id']
                    duplicate['post01_title'] = post01['title']
                    duplicate['post01_link'] = post01['link']
                    duplicate['post01_keyword'] = post01['seo_keyword']
                    duplicate['post02_id'] = post02['id']
                    duplicate['post02_title'] = post02['title']
                    duplicate['post02_link'] = post02['link']
                    duplicate['post02_keyword'] = post02['seo_keyword']
                    duplicates.append(duplicate)
                elif 0.7 < cosine_matrix[i][j] <= 0.9:  # Similarity threshold
                    similarity = {}
                    post01 = df.iloc[i].to_dict()
                    post02 = df.iloc[j].to_dict()
                    similarity['duplicate_hash'] = generate_hash()
                    similarity['post01_id'] = post01['id']
                    similarity['post01_title'] = post01['title']
                    similarity['post01_link'] = post01['link']
                    similarity['post01_keyword'] = post01['seo_keyword']
                    similarity['post02_id'] = post02['id']
                    similarity['post02_title'] = post02['title']
                    similarity['post02_link'] = post02['link']
                    similarity['post02_keyword'] = post02['seo_keyword']
                    similarities.append(similarity)
        
        result = {
            "duplicates": duplicates,
            "similarities": similarities
        }

        with open(result_of_analysis_path, 'w', encoding='utf-8') as f:
            yaml.dump(result, f, default_flow_style=False)
        
        return result_of_analysis_path