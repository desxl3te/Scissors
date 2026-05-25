import json
from pathlib import Path
from typing import Any

# утилиты для работы с JSON файлами
# чтение JSON
def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

# запись JSON атоматически создаст папку "data", если её нет
def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
