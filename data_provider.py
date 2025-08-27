# data_provider.py

import json
import os
from typing import Any, List, Dict
from collections.abc import Mapping


# This module is a general rendering engine responsible for transforming 
# external wedding data (from env or file) into an AI-friendly context string.

def _load_blocks() -> List[Dict[str, Any]]:
    """
    Loading list of wedding info blocks:
    1) Check the env var WEDDING_CONTEXT_JSON (JSON string).
    2) Otherwise read the file pointed to by WEDDING_CONTEXT_PATH (default: instance/wedding_data.json).
    Expected shape: list[ { "section_title": str, "details": dict } ]
    """
    # 1) Try JSON from environment (string)
    raw = os.getenv("WEDDING_CONTEXT_JSON")
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data
            else:
                print("WEDDING_CONTEXT_JSON 類型非 list，將嘗試改用檔案來源。")
        except Exception as e:
            print(f"WEDDING_CONTEXT_JSON 解析失敗: {e}，將嘗試改用檔案來源。")

    # 2) Fallback to file path
    path = os.getenv("WEDDING_CONTEXT_PATH", "instance/wedding_data.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print(f"檔案內容類型非 list：{path}。將回傳空列表。")
                return []
    except FileNotFoundError:
        print(f"找不到婚禮資料檔: {path} (可使用 WEDDING_CONTEXT_JSON 或調整 WEDDING_CONTEXT_PATH)")
        return []
    except Exception as e:
        print(f"讀取婚禮資料發生錯誤: {e}")
        return []
    
def get_wedding_context_string() -> str:
    """
    Transform the wedding data into an AI-readable, multi-section text string.
    """

    blocks = _load_blocks()
    if not blocks:
        return "(尚未提供婚禮資料)"
    
    parts: List[str] = []
    for section in blocks:
        title = section.get("section_title", "# 未知區塊")
        details = section.get("details", {})

        parts.append(title)

        if not details:
            parts.append("- (無資訊)")
        else:
            if isinstance(details, Mapping):
                for label, value in details.items():
                    parts.append(f"- {label}: {value}")
            else:
                # Unexpected shape; try best-effort rendering.
                parts.append(f"- (非預期格式) {details}")

        # Prettier format, add a blank line after block.
        parts.append("")

    return "\n".join(parts).strip()

# This block is for local testing of the module behavior.
if __name__ == "__main__":
    print(get_wedding_context_string())