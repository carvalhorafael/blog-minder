import sqlite3
from datetime import datetime, timedelta
from crewai_tools import BaseTool

class MarkPostsForImprovement(BaseTool):
    name: str = "Mark posts to be improved."
    description: str = (
        "Analyzes posts stored in a database at {database_path} and table {table_name} and marks which ones need improvement."
    )

    def _run(self, database_path: str, table_name: str) -> str:        
        
        # Calculating the date 30 days ago
        today = datetime.today()
        date_30_days_ago = today - timedelta(days=30)
        date_30_days_ago_str = date_30_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
                        
        # Connecting to the database
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()

        # Criteria for choosing posts that will have improved content
        # - cannot have been updated less than 30 days ago
        # - must have potential to climb positions (position > 10)
        # - must be being printed (more than 1000 impressions)
        # - cannot have been written by humans
        # - cannot have been already improved
        cur.execute(f'''
            UPDATE {table_name}
            SET to_improve = ?
            WHERE updated_at <= ?
            AND position > ?
            AND impressions > ?
            AND is_human_writer = ?
            AND was_improved = ?
        ''', (1, date_30_days_ago_str, 10, 1000, 0, 0))
        
        conn.commit()
        conn.close()

        return "Posts were tagged for improvement."
    
class MarkPostWasImproved(BaseTool):
    name: str = "Mark post was improved."
    description: str = (
        "Mark tha a post was improved."
    )

    def _run(self, post_id: int, database_path: str, table_name: str) -> str:
        # Connecting to the database
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()

        cur.execute(f'''
            UPDATE {table_name}
            SET was_improved = 1, to_improve = 0
            WHERE id = {post_id}
        ''')
        conn.commit()
        conn.close()

        return "Post was marked as improved."
