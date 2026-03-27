import re
import os
import sys
import subprocess
import argparse
import time

# 全局变量，用于后续延迟加载库
ts = None
inflect = None
p_engine = None

# 翻译缓存
TRANSLATION_CACHE = {}

# --- Lua Filter 脚本内容 (核心修改) ---
# 功能1: 将 latex-code 代码块作为原生 LaTeX 插入 (不转义)
# 功能2: 将独立行公式 (DisplayMath) 转换为 equation 环境 (带编号)
LUA_FILTER_CONTENT = r"""
function CodeBlock(el)
  -- 如果代码块标记为 latex-code，直接作为原生 LaTeX 插入
  if el.classes:includes('latex') then
    return pandoc.RawBlock('tex', el.text)
  end
end

function Math(el)
  -- 如果是独立行公式 ($$...$$)，转换为 equation 环境
  if el.mathtype == 'DisplayMath' then
    return pandoc.RawInline('tex', '\\begin{equation}' .. el.text .. '\\end{equation}')
  end
end
"""


# --- 依赖库加载逻辑 (懒加载) ---
def load_trans_dependencies():
    """仅在需要翻译模式时加载第三方库"""
    global ts, inflect, p_engine

    missing = []
    try:
        import translators as _ts

        ts = _ts
    except ImportError:
        missing.append("translators")

    try:
        import inflect as _inflect

        inflect = _inflect
        p_engine = inflect.engine()
    except ImportError:
        missing.append("inflect")

    if missing:
        print("错误: 选择 'trans' 模式需要以下库，请先安装：", file=sys.stderr)
        print(f"pip install {' '.join(missing)}", file=sys.stderr)
        sys.exit(1)


# --- 配置：智能缩写表 (仅用于 trans 模式) ---
SPECIAL_MAPPING = {
    "algorithm": "algo",
    "configuration": "config",
    "initialization": "init",
    "database": "db",
    "information": "info",
    "technology": "tech",
    "administrator": "admin",
    "parameter": "param",
    "mathematics": "math",
    "statistics": "stat",
    "user": "usr",
    "server": "srv",
}


# --- 辅助函数：管理临时 Lua 文件 ---
def create_lua_filter(filename="temp_pandoc_filter.lua"):
    """创建临时的 Lua Filter 文件"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(LUA_FILTER_CONTENT)
        return filename
    except IOError as e:
        print(f"错误: 无法创建临时 Lua 文件: {e}", file=sys.stderr)
        sys.exit(1)


def remove_lua_filter(filename="temp_pandoc_filter.lua"):
    """清理临时的 Lua Filter 文件"""
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError:
            pass


def strip_heading_number(title):
    r"""去除标题的数字编号 (如 2.1, 第二章)"""
    title = title.strip()
    title = re.sub(r"^(\d+(\.\d+)*)[:：\.\s]*", "", title)
    title = re.sub(r"^(第[一二三四五六七八九十]+章)[:：\s]*", "", title)
    title = re.sub(r"^[\(（]\d+[\)）][:：\s]*", "", title)
    return title.strip()


def get_target_level(title):
    r"""计算 Markdown Heading 层级"""
    raw_title = title.strip()

    # 匹配 "第x章"
    if re.match(r"^第[0-9一二三四五六七八九十百零]+章", raw_title):
        return 1

    # 匹配 2.1.1, 2.1.3 等多级编号
    num_match = re.match(r"^(\d+(\.\d+)+)", raw_title)
    if num_match:
        return num_match.group(1).count(".") + 1

    # 匹配 2.1
    num_match_2 = re.match(r"^(\d+\.\d+)", raw_title)
    if num_match_2:
        return 2

    return None


def generate_raw_label(text, prefix="sec"):
    """中文直出 Label"""
    clean_text = re.sub(r"[^\w\-_]", "", text)
    if len(clean_text) > 30:
        clean_text = clean_text[:30]
    return f"{prefix}:{clean_text}"


def generate_trans_label(text, prefix="sec"):
    r"""翻译+缩写 Label"""

    def translate(text, retries=3):
        if re.match(r"^[a-zA-Z0-9\s\-_]+$", text):
            return text
        if text in TRANSLATION_CACHE:
            return TRANSLATION_CACHE[text]

        for attempt in range(retries):
            try:
                result = ts.translate_text(text, translator="bing", to_language="en")
                if isinstance(result, str):
                    TRANSLATION_CACHE[text] = result
                    return result
            except Exception:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
        return text

    def abbreviate(word):
        word = word.lower()
        if word in SPECIAL_MAPPING:
            return SPECIAL_MAPPING[word]
        singular = p_engine.singular_noun(word)
        if singular:
            word = singular
        if len(word) <= 4:
            return word
        vowels = set("aeiou")
        abbr = word[0] + "".join([c for c in word[1:] if c not in vowels])
        if len(abbr) > 5:
            abbr = abbr[:5]
        return abbr

    try:
        translated = translate(text)
        clean_text = re.sub(r"[^a-z0-9\s]", "", translated.lower())
        stop_words = {
            "a",
            "an",
            "the",
            "of",
            "for",
            "and",
            "or",
            "in",
            "on",
            "at",
            "to",
            "with",
            "by",
            "based",
            "using",
            "from",
            "via",
            "is",
            "are",
            "about",
            "chapter",
            "section",
            "part",
            "study",
            "research",
            "analysis",
            "approach",
            "method",
        }

        words = clean_text.split()
        keywords = [w for w in words if w not in stop_words]
        if not keywords:
            keywords = words

        abbr_words = [abbreviate(w) for w in keywords]
        final_slug = "-".join(abbr_words[:3])

        return f"{prefix}:{final_slug}"
    except Exception as e:
        print(f"Label 生成异常: {e}", file=sys.stderr)
        return f"{prefix}:" + re.sub(r"[^\w]", "", text)[:10]


# ================= 主逻辑 =================


def improve_labels(filepath, style="raw"):
    if not os.path.exists(filepath):
        return

    if style == "trans":
        load_trans_dependencies()

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    cmd_to_prefix = {
        "chapter": "chap",
        "section": "sec",
        "subsection": "subsec",
        "subsubsection": "subsubsec",
    }

    def replacer(match):
        cmd = match.group(1)
        title = match.group(2)
        old_label = match.group(3)

        prefix = cmd_to_prefix.get(cmd, "sec")
        clean_title = re.sub(r"\\[a-zA-Z]+\{.*?\}", "", title)

        if style == "trans":
            new_label = generate_trans_label(clean_title, prefix)
        else:
            new_label = generate_raw_label(clean_title, prefix)

        return f"\\{cmd}{{{title}}}\\label{{{new_label}}}"

    pattern = r"\\(chapter|section|subsection|subsubsection)\{(.*?)\}\\label\{(.*?)\}"
    new_content = re.sub(pattern, replacer, content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("[SAVE] Labels 优化完成。")


def process_file(filepath, base_dir, visited=None, strip_numbers=True, current_shift=0):
    """
    递归读取处理文件。
    """
    if visited is None:
        visited = set()
    norm_path = os.path.normpath(os.path.join(base_dir, filepath))
    abs_path = os.path.abspath(norm_path)
    current_dir = os.path.dirname(abs_path)

    if abs_path in visited:
        return ""
    visited.add(abs_path)

    if not os.path.exists(abs_path):
        print(f"警告: 文件不存在: {abs_path}", file=sys.stderr)
        return f"\n% Warning: File not found: {filepath}\n"

    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()

    # 1. 预扫描：确定当前文件的标题层级偏移
    local_shift = 0
    for line in lines:
        match = re.match(r"^(#+)\s*(.*)$", line)
        if match:
            hashes, title = match.groups()
            target_level = get_target_level(title)
            # 只有当标题里显式包含 "2.1" 这种层级信息时，才重置 shift
            if target_level is not None:
                local_shift = target_level - len(hashes)
            else:
                local_shift = current_shift
            break

    # 2. 逐行处理
    output = []
    for line in lines:
        # A. 检测子文件引用 [Link](./sub.md)
        link_match = re.search(r"\[.*?\]\((?P<path>\.\/.*?\.md)\)", line)
        if link_match:
            sub_rel_path = link_match.group("path")
            clean_sub_path = sub_rel_path.strip().replace("./", "")
            if sub_rel_path.startswith("./"):
                clean_sub_path = sub_rel_path[2:]

            print(f"    > 读取子文件: {clean_sub_path}")

            sub_content = process_file(
                clean_sub_path,
                current_dir,
                visited,
                strip_numbers,
                current_shift=local_shift,
            )
            output.append(sub_content)
            continue

        # B. 检测标题
        heading_match = re.match(r"^(#+)\s*(.*)$", line)
        if heading_match:
            hashes, title = heading_match.groups()

            # 计算最终层级
            new_level = max(1, len(hashes) + local_shift)

            final_title = strip_heading_number(title) if strip_numbers else title

            # --- Tree Print Logic ---
            indent_count = max(0, new_level - 1)
            tree_prefix = "│   " * indent_count + "├── "
            print(f"{tree_prefix}{final_title}")
            # ------------------------

            output.append(("#" * new_level) + " " + final_title)
        else:
            output.append(line)

    return "\n".join(output) + "\n"


def remove_tightlist(filepath, whole_line=True):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r"\\providecommand\{\\tightlist\}\{.*?\}", "", content)
    if whole_line:
        content = re.sub(r"^.*\\tightlist.*$\n?", "", content, flags=re.MULTILINE)
    else:
        content = content.replace("\\tightlist", "")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("[SAVE] 删除 \\tightlist")


def main():
    parser = argparse.ArgumentParser(description="Markdown 合并转 LaTeX 工具")
    parser.add_argument("-i", "--input", required=True, help="输入文件路径")
    parser.add_argument("-o", "--output", help="输出文件名基名")
    parser.add_argument("--no-strip", action="store_true", help="保留标题数字编号")
    parser.add_argument(
        "--keep-tightlist", action="store_true", help="保留 \\tightlist"
    )
    parser.add_argument("--skip-labels", action="store_true", help="跳过 Label 优化")
    parser.add_argument(
        "--label-style",
        choices=["raw", "trans"],
        default="raw",
        help="Label 风格: 'raw' (中文, 默认), 'trans' (翻译+缩写)",
    )
    parser.add_argument(
        "--remove-markdown",
        default=True,
        help="删除合并的Markdown文件",
    )

    args = parser.parse_args()

    entry_file = args.input
    strip_numbers = not args.no_strip

    if args.output:
        output_basename = args.output
    else:
        base_name = os.path.splitext(os.path.basename(entry_file))[0]
        output_basename = f"{base_name}_expand"

    output_md = output_basename + ".md"
    output_tex = output_basename + ".tex"
    base_dir = os.getcwd()

    print("--- 标题概览 ---")
    merged = process_file(entry_file, base_dir, strip_numbers=strip_numbers)
    print("-------------------")

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("<!-- Auto-generated -->\n")
        f.write(merged)
    print(f"[SAVE] 合并 Markdown 已保存: {output_md}")

    # --- 创建临时 Lua Filter ---
    lua_filter_file = create_lua_filter()

    print("[PROC] 正在执行 Pandoc 转换 (含公式编号与RawTex处理)...")
    try:
        cmd = [
            "pandoc",
            output_md,
            "-o",
            output_tex,
            "--top-level-division=chapter",
            "--wrap=none",
            f"--lua-filter={lua_filter_file}",  # 加载临时生成的 Lua 脚本
        ]
        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Pandoc 错误 (code {e.returncode})", file=sys.stderr)
    except Exception as e:
        print(f"执行错误: {e}", file=sys.stderr)
    else:
        print(f"[SAVE] LaTeX 文件已生成: {output_tex}")
    finally:
        # --- 清理临时 Lua Filter ---
        remove_lua_filter(lua_filter_file)

    # 3. 后处理
    if not args.keep_tightlist:
        remove_tightlist(output_tex, whole_line=True)

    if not args.skip_labels:
        improve_labels(output_tex, style=args.label_style)

    if args.remove_markdown:
        os.remove(output_md)
        print(f"[DEL] 删除临时 Markdown 文件: {output_md}")


if __name__ == "__main__":
    main()
