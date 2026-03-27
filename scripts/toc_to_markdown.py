from __future__ import annotations

import argparse
import re
from pathlib import Path


HEADING_LEVELS = {
    "chapter": 0,
    "section": 1,
    "subsection": 2,
    "subsubsection": 3,
}


def parse_contentsline(line: str) -> tuple[str, str] | None:
    pattern = r"^\\contentsline\s*\{([^}]*)\}\{(.*)\}\{([^}]*)\}\{([^}]*)\}%?\s*$"
    match = re.match(pattern, line.strip())
    if not match:
        return None
    heading_type = match.group(1).strip()
    title_raw = match.group(2).strip()
    return heading_type, title_raw


def extract_braced(s: str, open_brace_index: int) -> tuple[str, int] | None:
    if open_brace_index >= len(s) or s[open_brace_index] != "{":
        return None
    depth = 0
    content_start = open_brace_index + 1
    for i in range(open_brace_index, len(s)):
        ch = s[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return s[content_start:i], i
    return None


def normalize_tex_text(text: str) -> str:
    cleaned = text
    cleaned = re.sub(r"\\hspace\s*\{[^}]*\}", " ", cleaned)
    cleaned = re.sub(r"\\ignorespaces\b", "", cleaned)
    cleaned = re.sub(r"\\relax\b", "", cleaned)
    cleaned = re.sub(r"\\textrm\s*\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\{|\}", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def clean_title(raw: str) -> tuple[str, str]:
    number = ""
    numberline_match = re.search(r"\\numberline\b", raw)
    if numberline_match:
        brace_start = raw.find("{", numberline_match.end())
        parsed = extract_braced(raw, brace_start)
        if parsed:
            number, brace_end = parsed
            number = normalize_tex_text(number)
            raw = raw[: numberline_match.start()] + raw[brace_end + 1 :]

    title = normalize_tex_text(raw)
    return number, title


def extract_headings(toc_path: Path) -> list[tuple[int, str]]:
    lines = toc_path.read_text(encoding="utf-8").splitlines()
    parsed: list[tuple[int, str, str]] = []

    for line in lines:
        item = parse_contentsline(line)
        if not item:
            continue
        heading_type, title_raw = item
        if heading_type not in HEADING_LEVELS:
            continue
        number, title = clean_title(title_raw)
        if not title:
            continue
        level = HEADING_LEVELS[heading_type]
        full_title = f"{number} {title}".strip()
        parsed.append((level, title, full_title))

    def filter_items(
        items: list[tuple[int, str, str]], require_abbrev: bool
    ) -> list[tuple[int, str]]:
        result: list[tuple[int, str]] = []
        started = not require_abbrev
        for level, title, full_title in items:
            if "参考文献" in title:
                break
            if "附录" in full_title:
                break
            if not started:
                if "缩略语" in title:
                    started = True
                continue
            result.append((level, full_title))
        return result

    filtered = filter_items(parsed, require_abbrev=True)
    if filtered:
        return filtered
    return filter_items(parsed, require_abbrev=False)


def headings_to_markdown(headings: list[tuple[int, str]], source: Path) -> str:
    output_lines = [
        "# 论文正文标题",
        "",
    ]
    for level, text in headings:
        indent = "  " * level
        output_lines.append(f"{indent}- {text}")
    output_lines.append("")
    return "\n".join(output_lines)


def build_parser() -> argparse.ArgumentParser:
    default_input = Path(__file__).resolve().parent.parent / "build" / "main.toc"
    parser = argparse.ArgumentParser(
        description="从 LaTeX .toc 中提取论文正文章节标题并输出 Markdown。"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=default_input,
        help=f"输入 .toc 文件路径（默认：{default_input}）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="输出 Markdown 文件路径（可选）",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_to_console",
        help="同时将结果打印到控制台",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    toc_path: Path = args.input.resolve()
    if not toc_path.exists():
        raise FileNotFoundError(f"找不到输入文件: {toc_path}")

    headings = extract_headings(toc_path)
    markdown = headings_to_markdown(headings, toc_path)

    should_print = args.print_to_console or args.output is None
    if should_print:
        print(markdown, end="")

    if args.output is not None:
        output_path: Path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        if not should_print:
            print(f"Markdown 已写入: {output_path.resolve()}")


if __name__ == "__main__":
    main()
