import pandas as pd
from crewai_tools import tool

@tool
def read_csv(file_path: str) -> dict:
    """
    Reads a CSV file and returns its contents as a DataFrame.
    """
    df = pd.read_csv(file_path)
    return df.to_dict(orient='records')