import os
import csv
from crewai_tools import tool

@tool
def read_csv_file(file_path: str) -> list:
    """
    Reads data from a CSV file.
    
    Args:
    file_path (str): The path to the CSV file.
    
    Returns:
    list: A list of dictionaries containing the data from the CSV file.
    """
    data = []
    try:
        with open(os.environ["POSTS_CSV_FILE_PATH"], mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        return f"Failed to read CSV file: {e}"
