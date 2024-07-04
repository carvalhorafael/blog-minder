from crewai_tools import BaseTool


class ReadCsv(BaseTool):
    name: str = "Read CSV file"
    description: str = (
        "Reads a CSV file and returns its contents as a DataFrame."
    )

    def _run(self, file_path: str) -> dict:
        df = pd.read_csv(file_path)
        return df.to_dict(orient='records')