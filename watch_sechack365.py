#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
複数ページ（SecHack365 配下の 7 URL）をまとめて監視するスクリプト。
各ページごとに ETag／Last-Modified を比較し、変化があれば通知します。

■ 追加の主なポイント
  1) URL をリストで列挙してループ処理
  2) 直近シグネチャを JSON で {url: signature} 形式で保存
  3) URL 単位で更新判定し、変化があったページだけメッセージ出力
"""

from __future__ import annotations

import json
import pathlib
import time
from typing import Final

import requests

# ─── 設定値 ──────────────────────────────────────────
URLS: Final[list[str]] = [
    "https://sechack365.nict.go.jp/document/",
    "https://sechack365.nict.go.jp/course/",
    "https://sechack365.nict.go.jp/trainers/",
    "https://sechack365.nict.go.jp/achievement/",
    "https://sechack365.nict.go.jp/report/",
    "https://sechack365.nict.go.jp/alumni/",
    "https://sechack365.nict.go.jp/requirements/",
]
CHECK_DELAY: Final[int] = 5  # 秒
STATE_FILE: Final[pathlib.Path] = (
    pathlib.Path(__file__).with_name("page_signatures.json")
)
# ────────────────────────────────────────────────


def get_page_signature(url: str) -> str:
    """対象 URL へ HEAD リクエストを送り、ETag と Last-Modified を 1 行にまとめる"""
    r = requests.head(url, timeout=10)
    r.raise_for_status()
    etag = r.headers.get("ETag", "")
    lm = r.headers.get("Last-Modified", "")
    return f"{etag},{lm}"


def load_prev_signatures() -> dict[str, str]:
    """JSON で保存した前回値を読み込む（無ければ空 dict）"""
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        # 壊れたら初期化
        return {}


def save_signatures(sig_dict: dict[str, str]) -> None:
    STATE_FILE.write_text(json.dumps(sig_dict, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    prev = load_prev_signatures()

    while True:
        changed = False  # 少なくとも 1 ページ更新されたか
        for url in URLS:
            try:
                now_sig = get_page_signature(url)
            except Exception as exc:
                print(f"⚠️ 取得失敗: {url} -> {exc}")
                continue

            if now_sig and now_sig != prev.get(url, ""):
                print(f"✅ 更新あり: {url}")
                prev[url] = now_sig
                changed = True
            else:
                print(f"— 変更なし: {url}")

        if changed:
            save_signatures(prev)

        time.sleep(CHECK_DELAY)


if __name__ == "__main__":
    main()
