from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import hanja


HANJA_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+")
XML_FILES = [Path("hg_001.xml"), Path("hg_002.xml")]


def annotate_hanja(text: str | None) -> str:
    if not text:
        return ""

    def replace(match: re.Match[str]) -> str:
        source = match.group(0)
        reading = hanja.translate(source, "substitution")
        return f"{source}({reading})"

    return HANJA_RE.sub(replace, text)


def clean_xml(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(line for line in lines if not line.lstrip().startswith("<!DOCTYPE"))


def text_content(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


def render_children(element: ET.Element, notes: list[dict]) -> str:
    parts: list[str] = []

    if element.text:
        parts.append(html.escape(annotate_hanja(element.text)))

    for child in element:
        parts.append(render_element(child, notes))
        if child.tail:
            parts.append(html.escape(annotate_hanja(child.tail)))

    return "".join(parts)


def render_element(element: ET.Element, notes: list[dict]) -> str:
    tag = element.tag

    if tag == "annotation":
        note_id = f"n{len(notes) + 1}"
        note_type = element.attrib.get("type", "주석")
        note_content = element.find("noteContent")
        notes.append(
            {
                "id": note_id,
                "type": annotate_hanja(note_type),
                "html": render_children(note_content, notes) if note_content is not None else "",
            }
        )
        return f'<sup class="note-ref" data-note-id="{note_id}">{len(notes)}</sup>'

    if tag == "br":
        return "<br>"

    if tag == "ul":
        list_type = html.escape(element.attrib.get("type", ""))
        class_attr = f' class="list-{list_type}"' if list_type else ""
        return f"<ul{class_attr}>{render_children(element, notes)}</ul>"

    if tag == "li":
        return f"<li>{render_children(element, notes)}</li>"

    if tag == "illustration":
        return f'<span class="image-group">{render_children(element, notes)}</span>'

    if tag == "image":
        src = html.escape(element.attrib.get("src", ""))
        return f'<span class="image-ref" title="원문 이미지 참조">{src}</span>'

    if tag == "noteContent":
        return render_children(element, notes)

    attrs = " ".join(f'{html.escape(k)}="{html.escape(v)}"' for k, v in element.attrib.items())
    open_tag = f"<{tag} {attrs}>" if attrs else f"<{tag}>"
    return f"{open_tag}{render_children(element, notes)}</{tag}>"


def parse_file(path: Path) -> dict:
    root = ET.fromstring(clean_xml(path))
    level1 = root.find(".//level1") if root.tag == "item" else root
    if level1 is None:
        level1 = root

    title = text_content(level1.find("./front/biblioData/title/mainTitle"))
    series = text_content(level1.find("./front/biblioData/title/seriesTitle"))
    coverage = text_content(level1.find("./front/description/coveragePeriod"))
    chapters = []

    for level2 in level1.findall("./level2"):
        notes: list[dict] = []
        paragraphs = []
        for paragraph in level2.findall(".//text/content/paragraph"):
            paragraphs.append(
                {
                    "align": paragraph.attrib.get("align", "left"),
                    "html": render_children(paragraph, notes).strip(),
                }
            )

        raw_title = text_content(level2.find("./front/biblioData/title/mainTitle"))
        chapters.append(
            {
                "id": level2.attrib.get("id", ""),
                "title": annotate_hanja(raw_title),
                "rawTitle": raw_title,
                "paragraphs": paragraphs,
                "notes": notes,
                "stats": {
                    "paragraphs": len(paragraphs),
                    "notes": len(notes),
                    "images": len(level2.findall(".//image")),
                },
            }
        )

    return {
        "id": level1.attrib.get("id", path.stem),
        "file": path.name,
        "title": annotate_hanja(title),
        "series": annotate_hanja(series),
        "coverage": annotate_hanja(coverage),
        "chapters": chapters,
    }


def main() -> None:
    volumes = [parse_file(path) for path in XML_FILES]
    payload = {
        "source": {
            "title": "海東高僧傳(해동고승전)",
            "organization": "국사편찬위원회",
            "files": [path.name for path in XML_FILES],
        },
        "stats": {
            "volumes": len(volumes),
            "chapters": sum(len(volume["chapters"]) for volume in volumes),
            "paragraphs": sum(
                chapter["stats"]["paragraphs"] for volume in volumes for chapter in volume["chapters"]
            ),
            "notes": sum(chapter["stats"]["notes"] for volume in volumes for chapter in volume["chapters"]),
            "images": sum(chapter["stats"]["images"] for volume in volumes for chapter in volume["chapters"]),
        },
        "volumes": volumes,
    }

    js = "window.HAEDONG_DATA = "
    js += json.dumps(payload, ensure_ascii=False, indent=2)
    js += ";\n"
    Path("data.js").write_text(js, encoding="utf-8")


if __name__ == "__main__":
    main()
