import os
import re
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

def extract_front_matter(content):
    match = re.match(r"^\s*---\s*$(.*?)^---\s*$(.*)", content, re.DOTALL | re.MULTILINE)
    if match:
        yaml_str = match.group(1).strip()
        markdown_content = match.group(2).strip()
        try:
            front_matter = yaml.safe_load(yaml_str)
            if front_matter is None:
                return {}, markdown_content
            return (
                front_matter if isinstance(front_matter, dict) else {}
            ), markdown_content
        except yaml.YAMLError as e:
            print(f"  [Error] YAML Parsing Failed: {e}")
            return None, content
    else:
        return {}, content

def process_markdown_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    front_matter, markdown_content = extract_front_matter(content)
    if front_matter is None:
        print(f"[Error] Failed to parse frontmatter in {filepath}")
        return

    # 提取正文中的第一个大标题
    match = re.match(r"^\s*#\s+(.+?)\s*$", markdown_content, re.MULTILINE)
    if match:
        heading = match.group(1).strip()
        # 如果 frontmatter 中有 title 且等于正文大标题，则移除正文大标题
        if "title" in front_matter and front_matter["title"] == heading:
            markdown_content = re.sub(r"^\s*#\s+.+?\s*$\n?", "", markdown_content, 1, re.MULTILINE)
        # 如果 frontmatter 中没有 title，则将正文大标题添加到 frontmatter 中
        elif "title" not in front_matter:
            front_matter["title"] = heading
            markdown_content = re.sub(r"^\s*#\s+.+?\s*$\n?", "", markdown_content, 1, re.MULTILINE)

    # 重新生成文件内容
    try:
        new_yaml_str = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_yaml_str}---\n\n{markdown_content}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[Processed] {filepath}")
    except Exception as e:
        print(f"[Error] Failed to write updated content for {filepath}: {e}")

def process_docs_directory(docs_dir):
    for root, _, files in os.walk(docs_dir):
        for filename in files:
            if filename.lower().endswith(".md"):
                filepath = os.path.join(root, filename)
                process_markdown_file(filepath)

if __name__ == "__main__":
    if os.path.exists(DOCS_DIR):
        process_docs_directory(DOCS_DIR)
    else:
        print(f"[Error] Docs directory not found: {DOCS_DIR}")
