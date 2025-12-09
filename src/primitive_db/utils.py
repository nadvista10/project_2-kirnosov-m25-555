import json
import os

metadata_path = "data/metadata.json"

def load_metadata():
    if not os.path.exists(metadata_path):
        return {}
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                # Если в файле не словарь, возвращаем пустой
                return {}
        except json.JSONDecodeError:
            # Если файл есть, но JSON некорректен
            return {}


def save_metadata(data):
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)