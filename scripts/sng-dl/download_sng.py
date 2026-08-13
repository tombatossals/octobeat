#!/usr/bin/env python3
"""Descarga masiva de archivos .sng de enchor.us (Chorus Encore).

Uso:
    python3 download_sng.py                      # descarga todo el catálogo filtrado
    python3 download_sng.py --output ./songs    # directorio de salida
    python3 download_sng.py --workers 4         # descargas en paralelo
    python3 download_sng.py --catalog-only      # solo guarda el catálogo (json)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

API_URL = "https://api.enchor.us"
FILES_URL = "https://files.enchor.us"
PAGE_SIZE = 10

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

DEFAULT_QUERY = {
    "instrument": "guitar",
    "difficulty": "expert",
    "drumType": None,
    "drumsReviewed": False,
    "sort": None,
    "source": "website",
    "name": {"value": "", "exact": False, "exclude": False},
    "artist": {"value": "", "exact": False, "exclude": False},
    "album": {"value": "", "exact": False, "exclude": False},
    "genre": {"value": "", "exact": False, "exclude": False},
    "year": {"value": "", "exact": False, "exclude": False},
    "charter": {"value": "Harmonix", "exact": False, "exclude": False},
    "minLength": None,
    "maxLength": None,
    "minIntensity": None,
    "maxIntensity": None,
    "minAverageNPS": None,
    "maxAverageNPS": None,
    "minMaxNPS": None,
    "maxMaxNPS": None,
    "minYear": None,
    "maxYear": None,
    "modifiedAfter": "",
    "hash": "",
    "trackHash": "",
    "hasSoloSections": None,
    "hasForcedNotes": None,
    "hasOpenNotes": None,
    "hasTapNotes": None,
    "hasLyrics": None,
    "hasVocals": None,
    "hasRollLanes": None,
    "has2xKick": None,
    "hasIssues": None,
    "hasVideoBackground": None,
    "modchart": None,
}


@dataclass
class Item:
    md5: str
    artist: str
    name: str
    charter: str
    chartId: int = 0
    songId: int = 0
    filename: str = ""

    @classmethod
    def from_row(cls, row: dict) -> "Item":
        return cls(
            md5=row["md5"],
            artist=row.get("artist") or "Unknown Artist",
            name=row.get("name") or "Unknown Name",
            charter=row.get("charter") or "Unknown Charter",
            chartId=row.get("chartId") or 0,
            songId=row.get("songId") or 0,
        )

    @property
    def url(self) -> str:
        return f"{FILES_URL}/{self.md5}.sng"

    def compute_filename(self, max_len: int = 100) -> str:
        raw = f"{self.artist} - {self.name} ({self.charter})"
        raw = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", raw)
        raw = raw.strip().strip(".")
        if len(raw) > max_len:
            raw = raw[: max_len - 4].rstrip() + "...."
        self.filename = f"{raw}.sng"
        return self.filename


def http_json(url: str, payload: dict, retries: int = 8) -> dict:
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After")
                try:
                    wait = min(int(retry_after), 60) if retry_after else 2 ** attempt
                except (TypeError, ValueError):
                    wait = 2 ** attempt
            elif exc.code in (500, 502, 503, 504):
                wait = 2 ** attempt
            else:
                raise
        except Exception as exc:
            last = exc
            wait = 2 ** attempt
        wait = min(wait, 60)
        print(f"  reintento API (página {payload.get('page')}): {last} en {wait}s",
              file=sys.stderr, flush=True)
        time.sleep(wait)
    raise last


CATALOG_FILE = "catalog.json"


def load_catalog_state() -> dict:
    try:
        with open(CATALOG_FILE) as fh:
            state = json.load(fh)
        if isinstance(state, dict) and "pages" in state:
            return state
    except (OSError, ValueError):
        pass
    return {"total": None, "pages": {}}


def save_catalog_state(state: dict) -> None:
    with open(CATALOG_FILE, "w") as fh:
        json.dump(state, fh)


def fetch_catalog(query: dict) -> list[dict]:
    state = load_catalog_state()
    if state.get("total") is None:
        first = http_json(f"{API_URL}/search/advanced", {**query, "page": 1})
        state["total"] = first.get("found", 0)
        state["pages"]["1"] = first.get("data") or []
        save_catalog_state(state)
    total = state["total"]
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"catálogo: {total} resultados, {pages} páginas, "
          f"{len(state['pages'])} ya guardadas", file=sys.stderr, flush=True)

    missing = [p for p in range(1, pages + 1) if str(p) not in state["pages"]]
    for p in missing:
        data = http_json(f"{API_URL}/search/advanced", {**query, "page": p})
        state["pages"][str(p)] = data.get("data") or []
        save_catalog_state(state)
        got = sum(len(v) for v in state["pages"].values())
        print(f"catálogo: {got}/{total} filas (página {p}/{pages})",
              file=sys.stderr, flush=True)
        time.sleep(0.1)

    return [r for p in range(1, pages + 1) for r in state["pages"].get(str(p), [])]


def build_items(rows: list[dict]) -> list[Item]:
    seen: set[str] = set()
    items: list[Item] = []
    for row in rows:
        md5 = row.get("md5")
        if not md5 or md5 in seen:
            continue
        seen.add(md5)
        items.append(Item.from_row(row))
    return items


def assign_filenames(items: list[Item]) -> None:
    used: dict[str, int] = {}
    for it in items:
        base = it.compute_filename()
        count = used.get(base, 0)
        used[base] = count + 1
        if count:
            it.filename = f"{base[:-4]} ({count}).sng"


def file_complete(path: str, expected: int | None) -> bool:
    return os.path.isfile(path) and (expected is None or os.path.getsize(path) == expected)


def probe_size(item: Item, timeout: int = 30) -> int | None:
    req = urllib.request.Request(
        item.url,
        method="GET",
        headers={"Range": "bytes=0-0", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        cr = resp.headers.get("Content-Range", "0/0")
        return int(cr.split("/")[-1])


def download(item: Item, dest: str, retries: int = 3, timeout: int = 120) -> tuple[str, str]:
    path = os.path.join(dest, item.filename)
    expected = probe_size(item)
    if file_complete(path, expected):
        return item.filename, "skip"

    tmp = f"{path}.part"
    if os.path.exists(tmp) and expected and os.path.getsize(tmp) > expected:
        os.remove(tmp)

    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "identity",
    }
    partial = os.path.exists(tmp) and os.path.getsize(tmp) > 0
    if partial:
        headers["Range"] = f"bytes={os.path.getsize(tmp)}-"

    for attempt in range(retries):
        try:
            req = urllib.request.Request(item.url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resumed = resp.status == 206 and partial
                mode = "ab" if resumed else "wb"
                with open(tmp, mode) as fh:
                    while True:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        fh.write(chunk)
            if expected and os.path.getsize(tmp) != expected:
                raise OSError(
                    f"tamaño inesperado: {os.path.getsize(tmp)} != {expected}"
                )
            os.replace(tmp, path)
            return item.filename, "ok"
        except Exception as exc:
            code = getattr(exc, "code", None)
            offset = os.path.getsize(tmp) if os.path.exists(tmp) else 0
            if code == 416 and offset and expected and offset >= expected:
                os.replace(tmp, path)
                return item.filename, "ok"
            last = exc
            if attempt < retries - 1:
                wait = 2 * (attempt + 1)
                print(f"  reintento {item.filename}: {exc} (en {wait}s)", file=sys.stderr)
                time.sleep(wait)
            elif os.path.exists(tmp) and expected and os.path.getsize(tmp) == expected:
                os.replace(tmp, path)
                return item.filename, "ok"
            else:
                return item.filename, f"error: {last}"


def main() -> None:
    ap = argparse.ArgumentParser(description="Descarga masiva de .sng de enchor.us")
    ap.add_argument("--output", "-o", default=os.path.join(os.getcwd(), "downloads"))
    ap.add_argument("--workers", "-w", type=int, default=3)
    ap.add_argument("--catalog-only", action="store_true")
    ap.add_argument("--catalog", default=None, help="ruta a catálogo JSON ya generado")
    args = ap.parse_args()

    if args.catalog:
        with open(args.catalog) as fh:
            state = json.load(fh)
        if "pages" in state:
            pages = (state["total"] + PAGE_SIZE - 1) // PAGE_SIZE
            rows = [r for p in range(1, pages + 1) for r in state["pages"].get(str(p), [])]
        else:
            rows = state
    else:
        rows = fetch_catalog(DEFAULT_QUERY)

    items = build_items(rows)
    assign_filenames(items)

    print(f"archivos únicos a descargar: {len(items)}")

    if args.catalog_only:
        json.dump(
            [
                {"md5": it.md5, "artist": it.artist, "name": it.name,
                 "charter": it.charter, "filename": it.filename, "url": it.url}
                for it in items
            ],
            open("catalog_dedupe.json", "w"),
            indent=2,
        )
        return

    os.makedirs(args.output, exist_ok=True)
    print(f"destino: {args.output}")

    stats = {"ok": 0, "skip": 0, "error": 0}
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(download, it, args.output): it for it in items}
        for fut in as_completed(futs):
            it = futs[fut]
            try:
                fname, status = fut.result()
            except Exception as exc:
                fname, status = it.filename, f"error: {exc}"
            if status == "ok":
                stats["ok"] += 1
            elif status == "skip":
                stats["skip"] += 1
            else:
                stats["error"] += 1
            done += 1
            if done % 25 == 0 or done == len(items):
                elapsed = time.time() - t0
                print(
                    f"progreso: {done}/{len(items)}  "
                    f"(ok={stats['ok']}, skip={stats['skip']}, err={stats['error']}) "
                    f"[{elapsed:.0f}s]",
                    file=sys.stderr,
                    flush=True,
                )

    print(f"resumen: ok={stats['ok']} skip={stats['skip']} errores={stats['error']}")


if __name__ == "__main__":
    main()
