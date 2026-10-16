"""Export Obsidian `.excalidraw.md` drawings to plain `.excalidraw` JSON files.

Obsidian's Excalidraw plugin stores scenes as LZ-string compressed JSON inside
a markdown wrapper. mkdocs-excalidraw renders plain `.excalidraw` JSON files
client-side, so this script decompresses each drawing next to its source:

    assets/excalidraw/Simple Agent flow.excalidraw.md
      -> assets/excalidraw/Simple Agent flow.excalidraw

Run from the `blogs/` directory after editing/adding drawings in Obsidian:

    python scripts/sync_excalidraw.py

Requires: pip install lzstring
"""
import glob
import json
import os
import re
import sys

try:
    from lzstring import LZString
except ImportError:
    sys.exit("Missing dependency: pip install lzstring")


def export_one(src_path: str) -> str:
    text = open(src_path, encoding="utf-8").read()
    match = re.search(r"```compressed-json\n(.*?)```", text, re.S)
    if not match:
        raise ValueError(f"No compressed-json block in {src_path}")
    blob = re.sub(r"\s+", "", match.group(1))
    scene = LZString().decompressFromBase64(blob)
    if not scene:
        raise ValueError(f"Could not decompress {src_path}")
    data = json.loads(scene)  # validate
    dst_path = src_path[: -len(".md")]  # strip trailing .md only
    with open(dst_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)
    return dst_path


def main() -> None:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "assets", "excalidraw")
    sources = sorted(glob.glob(os.path.join(base, "*.excalidraw.md")))
    if not sources:
        sys.exit(f"No drawings found in {base}")
    for src in sources:
        dst = export_one(src)
        print(f"{os.path.basename(src)} -> {os.path.basename(dst)}")


if __name__ == "__main__":
    main()
