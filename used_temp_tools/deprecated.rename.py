"""
写一个简单函数, 将 dev_plugin (和这个 main.py 同级的一个文件夹)的所有 md 里的 front (yaml) 进行操作:
1. 将含有相对路径的文件名写入新的 front (yaml) 中, 例如 `pervious_name: dev_plugin/schema-definition/model/model-designing-rules.md`
2. 将 md 重命名. yaml 例如:

```yaml
---
dimensions:
  type:
    primary: reference
    detail: core
  level: beginner
---
```

那么名字为 reference-core-beginner[].md / reference-core-beginner[model-designing-rules].md

然后, 将所有文件扁平化, 都放到 docs_new 里面. 挪动, 并跳过重复名字的
pip install PyYAML

"""

import os
import yaml
import re # 导入正则表达式模块

# --- 配置 ---
SOURCE_DIR_NAME = "dev_plugin"
TARGET_DIR_NAME = "docs_new"
# --- 配置结束 ---

# 获取当前脚本所在的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 拼接源目录和目标目录的绝对路径
SOURCE_DIR = os.path.join(BASE_DIR, SOURCE_DIR_NAME)
TARGET_DIR = os.path.join(BASE_DIR, TARGET_DIR_NAME)

def extract_front_matter(content):
    """
    从 Markdown 文件内容中提取 YAML front matter 和剩余内容。
    使用更健壮的正则表达式来处理不同的换行符和可选的空白。
    """
    # 匹配开头的 '---'，然后是非贪婪匹配任何字符 (.*?) 直到下一个 '---'
    # 使用 re.DOTALL 让 '.' 匹配换行符
    # 使用 re.MULTILINE 让 '^' 和 '$' 匹配行的开始和结束
    match = re.match(r'^\s*---\s*$(.*?)^---\s*$(.*)', content, re.DOTALL | re.MULTILINE)
    if match:
        yaml_str = match.group(1).strip()
        markdown_content = match.group(2).strip()
        try:
            # 解析 YAML
            front_matter = yaml.safe_load(yaml_str)
            # 确保返回的是字典，即使yaml为空也返回空字典
            return front_matter if isinstance(front_matter, dict) else {}, markdown_content
        except yaml.YAMLError as e:
            print(f"  [错误] YAML 解析失败: {e}")
            return None, content # YAML 解析失败，返回 None 和原始内容
    else:
        # 没有找到 front matter
        return {}, content # 返回空字典和原始内容

def sanitize_filename_part(part):
    """清理文件名部分，移除不允许的字符，并用连字符替换空格"""
    if not isinstance(part, str):
        part = str(part) # 转换为字符串以防万一
    part = part.lower() # 转为小写
    part = re.sub(r'\s+', '-', part) # 空格替换为连字符
    # 只保留字母、数字、连字符、下划线
    part = re.sub(r'[^\w\-]+', '', part)
    return part

def process_markdown_files(source_dir, target_dir):
    """
    处理源目录中的 Markdown 文件，提取 front matter，重命名并移动到目标目录。
    """
    print(f"开始处理源目录: {source_dir}")
    print(f"目标目录: {target_dir}")

    # 确保目标目录存在，如果不存在则创建
    os.makedirs(target_dir, exist_ok=True)
    print(f"确保目标目录 '{TARGET_DIR_NAME}' 已创建或已存在。")

    processed_count = 0
    skipped_count = 0
    error_count = 0

    # 遍历源目录及其所有子目录
    for root, _, files in os.walk(source_dir):
        for filename in files:
            # 检查是否是 markdown 文件
            if filename.lower().endswith(".md"):
                original_filepath = os.path.join(root, filename)
                # 计算相对于 source_dir 的路径，用于 previous_name
                relative_path = os.path.relpath(original_filepath, BASE_DIR).replace(os.sep, '/') # 使用 / 作为分隔符

                print(f"\n正在处理: {relative_path}")

                try:
                    # 读取文件内容
                    with open(original_filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取 front matter 和 markdown 内容
                    front_matter, markdown_content = extract_front_matter(content)

                    if front_matter is None: # YAML 解析错误
                         print(f"  [跳过] 文件 '{relative_path}' 的 YAML 解析失败。")
                         error_count += 1
                         continue

                    # --- 1. 添加 previous_name ---
                    front_matter['previous_name'] = relative_path

                    # --- 2. 构建新文件名 ---
                    try:
                        # 安全地获取 dimensions 值
                        dimensions = front_matter.get('dimensions', {})
                        type_info = dimensions.get('type', {})
                        primary = type_info.get('primary', 'unknown')
                        detail = type_info.get('detail', 'unknown')
                        level = dimensions.get('level', 'unknown')

                        # 清理文件名各部分
                        primary_clean = sanitize_filename_part(primary)
                        detail_clean = sanitize_filename_part(detail)
                        level_clean = sanitize_filename_part(level)

                        # 获取原始文件名（不含扩展名）
                        original_basename = os.path.splitext(filename)[0]
                        original_basename_clean = sanitize_filename_part(original_basename) # 也清理一下原始名字

                        # 构造新文件名
                        new_filename_base = f"{primary_clean}-{detail_clean}-{level_clean}"
                        if original_basename_clean: # 如果原始文件名清理后不为空
                            new_filename = f"{new_filename_base}[{original_basename_clean}].md"
                        else: # 如果原始文件名清理后为空（虽然不太可能）
                             new_filename = f"{new_filename_base}.md"

                        print(f"  提取维度: primary='{primary}', detail='{detail}', level='{level}'")
                        print(f"  生成新文件名: {new_filename}")

                    except Exception as e: # 捕捉构建文件名时可能出现的其他错误
                        print(f"  [错误] 构建新文件名失败: {e}")
                        print(f"  [跳过] 文件 '{relative_path}'")
                        error_count += 1
                        continue

                    # --- 3. 准备写入新文件 ---
                    target_filepath = os.path.join(target_dir, new_filename)

                    # 检查目标文件是否已存在
                    if os.path.exists(target_filepath):
                        print(f"  [跳过] 目标文件已存在: {new_filename}")
                        skipped_count += 1
                        continue

                    # 将更新后的 front matter 转回 YAML 字符串
                    new_yaml_str = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)

                    # 组合新的文件内容
                    new_content = f"---\n{new_yaml_str}---\n\n{markdown_content}"

                    # 写入新文件
                    with open(target_filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    print(f"  [成功] 文件已处理并保存到: {os.path.join(TARGET_DIR_NAME, new_filename)}")
                    processed_count += 1

                except FileNotFoundError:
                    print(f"  [错误] 文件未找到（可能在处理过程中被删除）: {original_filepath}")
                    error_count +=1
                except Exception as e:
                    # 捕获其他可能的错误，如读取权限等
                    print(f"  [错误] 处理文件 '{relative_path}' 时发生未知错误: {e}")
                    error_count += 1
            else:
                # print(f"  [跳过] 非 Markdown 文件: {filename}") # 如果需要可以取消注释
                pass

    print("\n--- 处理完成 ---")
    print(f"成功处理文件数: {processed_count}")
    print(f"因目标文件已存在而跳过数: {skipped_count}")
    print(f"处理过程中遇到错误数: {error_count}")

# --- 主程序入口 ---
if __name__ == "__main__":
    # 检查源目录是否存在
    if not os.path.isdir(SOURCE_DIR):
        print(f"错误：源目录 '{SOURCE_DIR_NAME}' 不存在于 {BASE_DIR}。请确保文件夹存在。")
    else:
        process_markdown_files(SOURCE_DIR, TARGET_DIR)
