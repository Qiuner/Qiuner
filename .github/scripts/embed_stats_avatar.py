import base64
import mimetypes
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SVG_PATH = ROOT / "profile-summary-card-output" / "github" / "3-stats.svg"
AVATAR_URL = "https://github.com/Qiuner.png?size=160"
CLIP_ID = "qiuner-avatar-clip"


def fetch_avatar() -> tuple[str, str]:
    request = urllib.request.Request(AVATAR_URL, headers={"User-Agent": "Qiuner-profile-readme"})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read()
        content_type = response.headers.get_content_type()

    if content_type == "application/octet-stream":
        content_type = mimetypes.guess_type(AVATAR_URL)[0] or "image/jpeg"

    return content_type, base64.b64encode(data).decode("ascii")


def avatar_block(content_type: str, data: str) -> str:
    return (
        f'<defs><clipPath id="{CLIP_ID}">'
        '<circle cx="268" cy="68" r="48"></circle>'
        '</clipPath></defs>'
        '<circle cx="268" cy="68" r="48" fill="#f6f8fa"></circle>'
        f'<image href="data:{content_type};base64,{data}" '
        'x="220" y="20" width="96" height="96" '
        f'clip-path="url(#{CLIP_ID})" preserveAspectRatio="xMidYMid slice"></image>'
    )


def replace_avatar(svg: str, replacement: str) -> str:
    existing_start = svg.find(f'<defs><clipPath id="{CLIP_ID}">')
    if existing_start >= 0:
        existing_end = svg.find("</image>", existing_start)
        if existing_end < 0:
            raise RuntimeError("Existing avatar block is incomplete.")
        return svg[:existing_start] + replacement + svg[existing_end + len("</image>"):]

    start_marker = '<g transform="translate(220,20)">'
    start = svg.find(start_marker)
    if start < 0:
        raise RuntimeError("Stats card GitHub mark group was not found.")

    end_marker = "</path></g></g>"
    end = svg.find(end_marker, start)
    if end < 0:
        raise RuntimeError("Stats card GitHub mark group end was not found.")

    return svg[:start] + replacement + svg[end + len(end_marker):]


def main() -> None:
    svg = SVG_PATH.read_text(encoding="utf-8-sig")
    content_type, data = fetch_avatar()
    updated = replace_avatar(svg, avatar_block(content_type, data))
    ET.fromstring(updated)
    SVG_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
