import json
import os

data_path = "data"
metadata_file_name = "metadata"


def load_metadata():
    return load_data_from_json(metadata_file_name)


def save_metadata(data):
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    save_data_to_json(metadata_file_name, data)


def load_table_data(table_name):
    return load_data_from_json(table_name)


def save_table_data(table_name, data):
    save_data_to_json(table_name, data)


def delete_table_data(table_name):
    file_path = os.path.join(data_path, f"{table_name}.json")
    if os.path.exists(file_path):
        os.remove(file_path)


def save_data_to_json(file_name, data):
    os.makedirs(data_path, exist_ok=True)
    file_path = os.path.join(data_path, f"{file_name}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_data_from_json(file_name):
    file_path = os.path.join(data_path, f"{file_name}.json")

    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                return {}
        except json.JSONDecodeError:
            return {}