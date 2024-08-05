class MarkPostsForImprovement(BaseTool):
    name: str = "Mark posts to be improved."
    description: str = (
        "Analyzes posts stored in a database at {database_path} and table {table_name} and marks which ones need improvement."
    )

    def _run(self, database_path: str, table_name: str) -> str:
        # connect to database or create one
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()


# Como escolher posts para melhorar conteúdo?
# - não podem ter sido atualizados tão recentemente
# - precisam ter potencial para subir posições
# - não podem já estar em posição muito alta
# - não podem ser "mega posts"