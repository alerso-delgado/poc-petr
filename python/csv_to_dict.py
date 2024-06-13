# python/csv_to_dict.py
import csv

def csv_to_dict(file_path):
    """
    Convert a CSV file into a dictionary of rows.

    This function reads a CSV file and returns a list of dictionaries representing the rows,
    where each row is represented by a dictionary with the CSV file headers as keys.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries representing the rows of the CSV file.

    Raises:
        FileNotFoundError: If the specified CSV file is not found.
    """

    try:
        return [*csv.DictReader(open(file_path))]
    except FileNotFoundError:
        raise FileNotFoundError(f"The CSV file ' {file_path} ' was not found.")