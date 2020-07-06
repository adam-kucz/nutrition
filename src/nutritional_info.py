import csv
from pathlib import Path
from typing import Mapping, MutableMapping


def read_names(path: Path) -> Mapping[str, str]:
    names: MutableMapping[str, str] = {}
    lines = path.read_text().split('\n')
    for line in csv.reader(lines):
        if not line:
            continue
        key = line[0]
        names[key] = key
        for name in line[1:]:
            names[name] = key
    return names


NutrientInfo = Mapping[str, float]
