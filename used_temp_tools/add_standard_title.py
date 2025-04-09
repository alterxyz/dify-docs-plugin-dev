import os
import yaml
import re

# --- 配置 ---
TARGET_DIR_NAME = "dev_plugin"
# --- 配置结束 ---

# 获取当前脚本所在的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 拼接目标目录的绝对路径
TARGET_DIR = os.path.join(BASE_DIR, TARGET_DIR_NAME)

def extract_front_matter(content):
    """
    从 Markdown 文件内容中提取 YAML front matter 和剩余内容。
    使用正则表达式来处理不同的换行符和可选的空白。
    """
    # 匹配开头的 '---'，然后是非贪婪匹配任何字符 (.*?) 直到下一个 '---'
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

def generate_standard_title(filename):
    """
    从文件名生成标准标题
    """
    # 移除扩展名
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # 将连字符和下划线替换为空格
    title = re.sub(r'[-_]', ' ', base_name)
    
    # 将标题转为标题格式（首字母大写）
    title = title.title()
    
    return title

def add_standard_title_to_md_files(target_dir):
    """
    为目标目录中的所有 Markdown 文件添加 standard_title 到 front matter
    """
    print(f"开始处理目录: {target_dir}")
    
    processed_count = 0
    error_count = 0
    
    # 遍历目标目录及其所有子目录
    for root, _, files in os.walk(target_dir):
        for filename in files:
            # 检查是否是 markdown 文件
            if filename.lower().endswith(".md"):
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, BASE_DIR).replace(os.sep, '/')
                
                print(f"\n正在处理: {relative_path}")
                
                try:
                    # 读取文件内容
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取 front matter 和 markdown 内容
                    front_matter, markdown_content = extract_front_matter(content)
                    
                    if front_matter is None: # YAML 解析错误
                        print(f"  [跳过] 文件 '{relative_path}' 的 YAML 解析失败。")
                        error_count += 1
                        continue
                    
                    # 生成 standard_title
                    standard_title = generate_standard_title(filename)
                    
                    # 添加 standard_title 到 front matter
                    front_matter['standard_title'] = standard_title
                    
                    print(f"  添加 standard_title: '{standard_title}'")
                    
                    # 将更新后的 front matter 转回 YAML 字符串
                    new_yaml_str = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    
                    # 组合新的文件内容
                    new_content = f"---\n{new_yaml_str}---\n\n{markdown_content}"
                    
                    # 写入文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"  [成功] 已添加 standard_title 到文件: {relative_path}")
                    processed_count += 1
                    
                except Exception as e:
                    print(f"  [错误] 处理文件 '{relative_path}' 时发生错误: {e}")
                    error_count += 1
    
    print("\n--- 处理完成 ---")
    print(f"成功处理文件数: {processed_count}")
    print(f"处理过程中遇到错误数: {error_count}")

def add_language_to_md_files(target_dir):
    """
    为目标目录中的所有 Markdown 文件添加 language: zh 到 front matter
    """
    print(f"开始处理目录: {target_dir}")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    # 遍历目标目录及其所有子目录
    for root, _, files in os.walk(target_dir):
        for filename in files:
            # 检查是否是 markdown 文件
            if filename.lower().endswith(".md"):
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, BASE_DIR).replace(os.sep, '/')
                
                print(f"\n正在处理: {relative_path}")
                
                try:
                    # 读取文件内容
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取 front matter 和 markdown 内容
                    front_matter, markdown_content = extract_front_matter(content)
                    
                    if front_matter is None: # YAML 解析错误
                        print(f"  [跳过] 文件 '{relative_path}' 的 YAML 解析失败。")
                        error_count += 1
                        continue
                    
                    # 检查是否已有语言设置
                    if 'language' in front_matter:
                        print(f"  [跳过] 文件 '{relative_path}' 已设置语言: {front_matter['language']}")
                        skipped_count += 1
                        continue
                    
                    # 添加语言到 front matter
                    front_matter['language'] = 'zh'
                    
                    print("  添加 language: 'zh'")
                    
                    # 将更新后的 front matter 转回 YAML 字符串
                    new_yaml_str = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    
                    # 组合新的文件内容
                    new_content = f"---\n{new_yaml_str}---\n\n{markdown_content}"
                    
                    # 写入文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"  [成功] 已添加 language: zh 到文件: {relative_path}")
                    processed_count += 1
                    
                except Exception as e:
                    print(f"  [错误] 处理文件 '{relative_path}' 时发生错误: {e}")
                    error_count += 1
    
    print("\n--- 处理完成 ---")
    print(f"成功处理文件数: {processed_count}")
    print(f"已有语言设置而跳过的文件数: {skipped_count}")
    print(f"处理过程中遇到错误数: {error_count}")

# --- 主程序入口 ---
if __name__ == "__main__":
    # 检查目标目录是否存在
    if not os.path.isdir(TARGET_DIR):
        print(f"错误：目标目录 '{TARGET_DIR_NAME}' 不存在于 {BASE_DIR}。请确保文件夹存在。")
    else:
        # add_standard_title_to_md_files(TARGET_DIR)
        add_language_to_md_files(TARGET_DIR)