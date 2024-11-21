from typing import Any
import json

class CustomEncoder:
    def __call__(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {str(k): self(v) for k, v in obj.items()}
        return obj


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is None or (isinstance(obj, (list, dict)) and not obj):
            return None
        return super().default(obj)

def custom_json_dumps(data):
    def remove_empty(data):
        if isinstance(data, dict):
            return {k: remove_empty(v) for k, v in data.items() if v is not None and (not isinstance(v, (list, dict)) or v)}
        elif isinstance(data, list):
            return [remove_empty(v) for v in data if v is not None and (not isinstance(v, (list, dict)) or v)]
        else:
            return data

    cleaned_data = remove_empty(data)
    return json.dumps(cleaned_data, cls=CustomJSONEncoder, sort_keys=True, separators=(',', ':'))
