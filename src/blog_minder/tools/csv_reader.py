import pandas as pd
from crewai_tools import BaseTool


class ReadCsv(BaseTool):
    name: str = "Read CSV file"
    description: str = (
        "Reads the CSV file at {blog_posts_file_path} and returns its contents as a Dictionary."
    )

    def _run(self, blog_posts_file_path: str) -> dict:
        df = pd.read_csv(blog_posts_file_path)
        return df.to_dict(orient='records')