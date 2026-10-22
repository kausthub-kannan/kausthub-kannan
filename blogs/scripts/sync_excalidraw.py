"""Export Obsidian `.excalidraw.md` drawings to plain `.excalidraw` JSON files.

Obsidian's Excalidraw plugin stores scenes as LZ-string compressed JSON inside
a markdown wrapper. mkdocs-excalidraw renders plain `.excalidraw` JSON files
client-side, so this script decompresses each drawing next to its source:

    assets/excalidraw/Agentic AI/Simple Agent flow.excalidraw.md
      -> assets/excalidraw/Agentic AI/Simple Agent flow.excalidraw
    assets/excalidraw/System Design/Fundamentals/Networking/DNS.md
      -> assets/excalidraw/System Design/Fundamentals/Networking/DNS.excalidraw

Drawings are kept in subfolders mirroring the notes tree (Agentic AI/,
System Design/Fundamentals/Networking/, ...). Both naming styles the Obsidian
plugin produces are handled: `Name.excalidraw.md` and plain `Name.md`.
Files without a compressed-json block are skipped.

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

COMPRESSED_JSON_RE = re.compile(r"```compressed-json\n(.*?)```", re.S)


def export_one(src_path: str) -> str | None:
    text = open(src_path, encoding="utf-8").read()
    match = COMPRESSED_JSON_RE.search(text)
    if not match:
        return None  # not an excalidraw drawing
    blob = re.sub(r"\s+", "", match.group(1))
    scene = LZString().decompressFromBase64(blob)
    if not scene:
        raise ValueError(f"Could not decompress {src_path}")
    data = json.loads(scene)  # validate
    if src_path.endswith(".excalidraw.md"):
        dst_path = src_path[: -len(".md")]  # Name.excalidraw.md -> Name.excalidraw
    else:
        dst_path = src_path[: -len(".md")] + ".excalidraw"  # Name.md -> Name.excalidraw
    with open(dst_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)
    return dst_path


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(script_dir, "..", "assets", "excalidraw")
    sources = sorted(
        p for p in glob.glob(os.path.join(base, "*", "**", "*.md"), recursive=True)
        if not p.endswith(".md/.md")  # paranoia: never treat folders as files
    )
    if not sources:
        sys.exit(f"No drawings found in {base}")
    exported = skipped = 0
    for src in sources:
        dst = export_one(src)
        if dst is None:
            skipped += 1
            continue
        print(f"{src} -> {os.path.relpath(dst, base)}")
        exported += 1
    print(f"\n{exported} exported, {skipped} skipped (not excalidraw drawings)")


if __name__ == "__main__":
    main()
