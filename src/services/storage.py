from pathlib import Path
import json

class Storage:
    def __init__(self, storage_path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_annotations(self, filename, annotations):
        file_path = self.storage_path / filename
        with open(file_path, 'w') as f:
            json.dump(annotations, f)

    def load_annotations(self, filename):
        file_path = self.storage_path / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None

    def list_annotations(self):
        return [file.name for file in self.storage_path.glob('*.json')]