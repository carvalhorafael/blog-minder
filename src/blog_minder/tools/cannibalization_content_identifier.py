import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from crewai_tools import BaseTool


class FindDuplicatesAndSimilarities(BaseTool):
    name: str = "Fetch duplicate and similarities on blog posts"
    description: str = (
        "Reads the CSV file at {blog_posts_file_path} and finds duplicate and similar posts. Returns a report indicating duplicates and similarities."
    )

    def _run(self, blog_posts_file_path: str) -> str:
        df = pd.read_csv(blog_posts_file_path)
        df = df.to_dict(orient='records')
        df = pd.DataFrame(df)
        
        # print(df)
        # return df.to_dict(orient='records')
        # df = pd.DataFrame(data)
        titles = df['title'].tolist()
        
        keywords = df['Keyword'].tolist() # erro aqui 

        print("\n\n ENTREI NA FUNÇÃO \n\n")

        # print("\n\n ENTREI NA FUNÇÃO \n\n")
        
        # Combine titles and keywords for similarity check
        combined_texts = [f"{title} {keyword}" for title, keyword in zip(titles, keywords)]
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer().fit_transform(combined_texts)
        vectors = vectorizer.toarray()
        
        # Compute cosine similarity
        cosine_matrix = cosine_similarity(vectors)
        
        duplicates = []
        similarities = []
        
        for i in range(len(titles)):
            for j in range(i + 1, len(titles)):
                if cosine_matrix[i][j] > 0.9:  # Duplicate threshold
                    duplicates.append((df.iloc[i]['ID'], df.iloc[j]['ID']))
                elif 0.7 < cosine_matrix[i][j] <= 0.9:  # Similarity threshold
                    similarities.append((df.iloc[i]['ID'], df.iloc[j]['ID']))
        
        # Generate report
        report = "Duplicate Posts:\n"
        for dup in duplicates:
            report += f"Post {dup[0]} and Post {dup[1]} are duplicates.\n"
        
        report += "\nSimilar Posts:\n"
        for sim in similarities:
            report += f"Post {sim[0]} and Post {sim[1]} are similar.\n"
        
        return report
