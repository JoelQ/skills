#!/usr/bin/env python3
"""
Diff Explainer build tool.

Two subcommands:

  show
    Read a unified diff from stdin and print numbered diff panels per file.
    Use this during authoring to discover the data-n line numbers your
    commentary will reference.

      git diff | python3 scripts/build.py show

  render <commentary.json> [-o report.html]
    Read a diff from stdin, combine with the commentary JSON, and write the
    finished HTML report. The script handles all HTML assembly — escaping,
    tags, headings, panel rendering, and template substitution.

      git diff | python3 scripts/build.py render commentary.json -o report.html

commentary.json schema:

    {
      "title": "...",
      "summary_what": "...",
      "summary_why": "...",
      "files": [
        {
          "path": "src/Auth.cs",
          "tag": "new",                              // new | mod | infra
          "cards": [
            {
              "type": "concept",                     // observation | concept | warn | surprise
              "title": "Dependency injection",
              "label": "Concept",                    // optional override of the prefix
              "body": "Plain text or inline HTML.",
              "lines": "1-5"                         // data-n ranges; "3,7-12" also valid
            }
          ]
        }
      ]
    }

Files that appear in the diff but not in commentary.json are rendered with no
commentary, so you can ship a partial report on a large diff.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

DEFAULT_LABEL = {
    "observation": "Observation",
    "concept": "Concept",
    "warn": "Potential Issue",
    "surprise": "Surprise",
}

CARD_CLASS = {
    "observation": "",
    "concept": " concept",
    "warn": " warn",
    "surprise": " surprise",
}

TAG_TEXT = {"new": "new", "mod": "modified", "infra": "infra"}


def parse_diff(text):
    files = []
    current = None
    line_num = 0

    skip_prefixes = (
        "diff --git", "index ",
        "new file mode", "deleted file mode",
        "old mode", "new mode",
        "similarity index", "dissimilarity index",
        "rename from", "rename to",
        "copy from", "copy to",
        "--- ", "+++ ",
    )

    for raw in text.splitlines():
        m = re.match(r"^diff --git a/(.+) b/(.+)$", raw)
        if m:
            if current is not None:
                files.append(current)
            current = {"path": m.group(2), "type": "modified", "spans": []}
            line_num = 0
            continue

        if current is None:
            continue

        if raw.startswith("new file mode"):
            current["type"] = "new"
        elif raw.startswith("deleted file mode"):
            current["type"] = "deleted"
        elif raw.startswith("rename from") or raw.startswith("rename to"):
            current["type"] = "renamed"
        elif raw.startswith("Binary files"):
            current["type"] = "binary"

        if raw.startswith(skip_prefixes):
            continue

        if raw.startswith("@@"):
            cls = "diff-hunk"
        elif raw.startswith("+"):
            cls = "diff-add"
        elif raw.startswith("-"):
            cls = "diff-remove"
        elif raw == "" or raw.startswith(" ") or raw.startswith("\\"):
            cls = "diff-context"
        else:
            continue

        line_num += 1
        escaped = html.escape(raw, quote=False)
        current["spans"].append(
            f'<span class="diff-line {cls}" data-n="{line_num}">{escaped}</span>'
        )

    if current is not None:
        files.append(current)
    return files


def render_panel(diff_file):
    path_esc = html.escape(diff_file["path"], quote=True)
    spans = "\n".join(diff_file["spans"]) if diff_file["spans"] else ""
    return (
        f'<div class="diff-panel">\n'
        f'    <div class="diff-file-header">{path_esc}</div>\n'
        f'    <div class="diff-content"><pre>\n'
        f'{spans}\n'
        f'</pre></div>\n'
        f'  </div>'
    )


def render_card(card):
    card_type = card.get("type", "observation")
    css_extra = CARD_CLASS.get(card_type, "")
    label = card.get("label") or DEFAULT_LABEL.get(card_type, "Note")
    title = card.get("title", "").strip()
    body = card.get("body", "").strip()
    lines = card.get("lines", "").strip() if isinstance(card.get("lines", ""), str) else str(card.get("lines"))

    label_text = f"{label}: {title}" if title else label
    label_html = html.escape(label_text, quote=False)

    data_attr = f' data-lines="{html.escape(lines, quote=True)}"' if lines else ""

    # If body isn't HTML, wrap it in <p> so the note's existing padding works.
    if body and not body.lstrip().startswith("<"):
        body_html = f"<p>{body}</p>"
    else:
        body_html = body

    return (
        f'    <div class="note{css_extra}"{data_attr}>\n'
        f'      <div class="note-label">{label_html}</div>\n'
        f'      {body_html}\n'
        f'    </div>'
    )


def render_row(idx, fmeta, diff_file):
    path = fmeta.get("path") or (diff_file["path"] if diff_file else "")
    tag = fmeta.get("tag", "mod")
    cards = fmeta.get("cards", [])

    filename = Path(path).name
    tag_text = TAG_TEXT.get(tag, tag)
    heading = (
        f'{idx}. {html.escape(filename, quote=False)} '
        f'<span class="tag tag-{html.escape(tag, quote=False)}">{html.escape(tag_text, quote=False)}</span>'
    )

    cards_html = "\n".join(render_card(c) for c in cards) if cards else ""

    if diff_file is not None:
        panel_html = render_panel(diff_file)
    else:
        panel_html = (
            f'<div class="diff-panel">\n'
            f'    <div class="diff-file-header">{html.escape(path, quote=True)} (not found in diff)</div>\n'
            f'  </div>'
        )

    return (
        f'<div class="row">\n'
        f'  <div class="commentary">\n'
        f'    <h2>{heading}</h2>\n'
        f'{cards_html}\n'
        f'  </div>\n'
        f'\n'
        f'  {panel_html}\n'
        f'</div>'
    )


def cmd_show(_args):
    files = parse_diff(sys.stdin.read())
    for f in files:
        print(f"FILE {f['path']}")
        print(f"TYPE {f['type']}")
        print("PANEL")
        print(render_panel(f))
        print("END")
        print()


def cmd_render(args):
    commentary = json.loads(Path(args.commentary).read_text())
    diff_files = {f["path"]: f for f in parse_diff(sys.stdin.read())}

    rows = []
    idx = 1
    commented = set()
    for fmeta in commentary.get("files", []):
        path = fmeta.get("path", "")
        commented.add(path)
        rows.append(render_row(idx, fmeta, diff_files.get(path)))
        idx += 1

    for path, diff_file in diff_files.items():
        if path not in commented:
            rows.append(render_row(idx, {"path": path, "tag": "mod"}, diff_file))
            idx += 1

    template_path = Path(__file__).parent.parent / "assets" / "template.html"
    template = template_path.read_text()

    rendered = (
        template
        .replace("{{TITLE}}", html.escape(commentary.get("title", "Diff Report"), quote=False))
        .replace("{{SUMMARY_WHAT}}", commentary.get("summary_what", ""))
        .replace("{{SUMMARY_WHY}}", commentary.get("summary_why", ""))
        .replace("{{ROWS}}", "\n\n".join(rows))
    )

    output_path = Path(args.output)
    output_path.write_text(rendered)
    print(f"Wrote {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Diff explainer build tool")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("show", help="Print numbered diff panels from stdin")

    render_p = sub.add_parser("render", help="Build HTML report from commentary.json + stdin diff")
    render_p.add_argument("commentary", help="Path to commentary.json")
    render_p.add_argument("-o", "--output", default="diff-report.html", help="Output HTML path")

    args = parser.parse_args()
    {"show": cmd_show, "render": cmd_render}[args.cmd](args)


if __name__ == "__main__":
    main()
