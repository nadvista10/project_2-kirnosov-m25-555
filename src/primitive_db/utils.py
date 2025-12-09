import json
import os


def load_metadata(filepath):
    if not os.path.exists(filepath):
        return {}
    
    with open(filepath, "r", encoding="utf-8") as f:
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


def save_metadata(filepath, data):
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)