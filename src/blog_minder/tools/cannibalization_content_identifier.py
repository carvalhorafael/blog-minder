import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from crewai_tools import BaseTool
import json


class FindDuplicatesAndSimilarities(BaseTool):
    name: str = "Fetch duplicate and similarities on blog posts"
    description: str = (
        "Reads a CSV file at {blog_posts_file_path}, finds duplicate and similar posts then save a JSON file at {result_of_analysis_path} as result of analysis."
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
                    duplicate = []
                    duplicate.append(df.iloc[i].to_dict())
                    duplicate.append(df.iloc[j].to_dict())
                    duplicates.append(duplicate)
                elif 0.7 < cosine_matrix[i][j] <= 0.9:  # Similarity threshold
                    similarity = []
                    similarity.append(df.iloc[i].to_dict())
                    similarity.append(df.iloc[j].to_dict())
                    similarities.append(similarity)
        
        result = {
            "duplicates": duplicates,
            "similarities": similarities
        }

        with open(result_of_analysis_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        return result_of_analysis_path