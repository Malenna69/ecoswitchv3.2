# -*- coding: utf-8 -*-
import json

def load_client(path_json: str):
    with open(path_json, "r", encoding="utf-8") as f:
        return json.load(f)
