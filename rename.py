import os
import yaml
import re
# import shutil  # Keep for potential future use, though os.rename is used now
import datetime  # To generate timestamps for archiving

# --- Configuration ---
SOURCE_DIR_NAME = "docs_new_archive_20250409_152626" # dev_plugin
TARGET_DIR_NAME = "docs"
ARCHIVE_PREFIX = "docs_new_archive_"  # Prefix for archived directories

# --- Mapping Configuration ---
# (Mappings remain the same as the previous version)
PRIMARY_TYPE_MAP = {
    'conceptual': 1, 'implementation': 2, 'operational': 3, 'reference': 4,
}
DEFAULT_W = 0
DETAIL_TYPE_MAPS = {
    'conceptual': {'introduction': 1, 'principles': 2, 'architecture': 3},
    'implementation': {'basic': 1, 'standard': 2, 'high': 3, 'advanced': 4},
    'operational': {'setup': 1, 'deployment': 2, 'maintenance': 3},
    'reference': {'core': 1, 'configuration': 2, 'examples': 3},
}
DEFAULT_X = 0
LEVEL_MAP = {
    'beginner': 1, 'intermediate': 2, 'advanced': 3,
}
DEFAULT_Y = 0
PRIORITY_NORMAL = 0
PRIORITY_HIGH = 9
PRIORITY_ADVANCED_LEVEL_KEY = 'advanced'
PRIORITY_IMPLEMENTATION_PRIMARY_KEY = 'implementation'
PRIORITY_IMPLEMENTATION_DETAIL_KEYS = {'high', 'advanced'}

# --- Configuration End ---

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, SOURCE_DIR_NAME)
TARGET_DIR = os.path.join(BASE_DIR, TARGET_DIR_NAME)

# --- Helper Functions ---
# (extract_front_matter remains the same)


def extract_front_matter(content):
    match = re.match(r'^\s*---\s*$(.*?)^---\s*$(.*)',
                     content, re.DOTALL | re.MULTILINE)
    if match:
        yaml_str = match.group(1).strip()
        markdown_content = match.group(2).strip()
        try:
            front_matter = yaml.safe_load(yaml_str)
            if front_matter is None:
                return {}, markdown_content
            return front_matter if isinstance(front_matter, dict) else {}, markdown_content
        except yaml.YAMLError as e:
            print(f"  [Error] YAML Parsing Failed: {e}")
            return None, content
    else:
        return {}, content

# (sanitize_filename_part remains mostly the same, ensures non-empty return)


def sanitize_filename_part(part):
    if not isinstance(part, str):
        part = str(part)
    part = part.lower()
    # Replace common problematic characters first
    part = part.replace('&', 'and').replace('@', 'at')
    part = re.sub(r'\s+', '-', part)  # Whitespace to hyphen
    # Keep letters, numbers, underscore, hyphen. Remove others.
    part = re.sub(r'[^\w\-]+', '', part)
    part = part.strip('.-_')  # Remove leading/trailing separators
    # Ensure it's not empty, provide a default if it becomes empty
    return part or "untitled"

# --- Main Processing Function ---


def process_markdown_files(source_dir, target_dir):
    """
    Processes markdown files, archives old target dir, uses PWXY-[title].lang.md format.
    """
    print("Starting processing...")
    print(f"Source Directory: {source_dir}")
    print(f"Target Directory: {target_dir}")

    # --- Archive Existing Target Directory ---
    if os.path.exists(target_dir):
        if os.path.isdir(target_dir):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir = os.path.join(
                BASE_DIR, f"{ARCHIVE_PREFIX}{timestamp}")
            try:
                os.rename(target_dir, archive_dir)
                print(f"Archived existing target directory to: {archive_dir}")
            except OSError as e:
                print(
                    f"[Error] Failed to archive existing target directory: {e}")
                print("Aborting to prevent data loss.")
                return  # Stop execution if archiving fails
        else:
            print(
                f"[Error] Target path '{target_dir}' exists but is not a directory. Please remove or rename it manually.")
            print("Aborting.")
            return

    # --- Create New Target Directory ---
    try:
        # Should not exist after archiving
        os.makedirs(target_dir, exist_ok=False)
        print(f"Created new target directory: {target_dir}")
    except OSError as e:
        print(f"[Error] Failed to create target directory '{target_dir}': {e}")
        print("Aborting.")
        return

    processed_count = 0
    skipped_count = 0
    error_count = 0
    warning_count = 0  # Counts files with at least one warning

    for root, _, files in os.walk(source_dir):
        for filename in files:
            if not filename.lower().endswith(".md"):
                continue

            original_filepath = os.path.join(root, filename)
            relative_path = os.path.relpath(
                original_filepath, BASE_DIR).replace(os.sep, '/')

            print(f"\nProcessing: {relative_path}")
            current_warnings = 0  # Reset warning flag for this file

            try:
                with open(original_filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                front_matter, markdown_content = extract_front_matter(content)

                if front_matter is None:
                    print("  [Skipping] YAML Error in file.")
                    error_count += 1
                    continue

                # --- Extract Metadata (including new fields) ---
                dimensions = front_matter.get('dimensions', {})
                type_info = dimensions.get('type', {})
                primary = type_info.get('primary')
                detail = type_info.get('detail')
                level = dimensions.get('level')
                standard_title = front_matter.get('standard_title')  # New
                language = front_matter.get('language')  # New

                # --- Determine P, W, X, Y (Logic remains the same) ---
                P = PRIORITY_NORMAL
                # (Priority logic based on level and implementation/detail)
                if level == PRIORITY_ADVANCED_LEVEL_KEY:
                    P = PRIORITY_HIGH
                if primary == PRIORITY_IMPLEMENTATION_PRIMARY_KEY and detail in PRIORITY_IMPLEMENTATION_DETAIL_KEYS:
                    P = PRIORITY_HIGH

                W = PRIMARY_TYPE_MAP.get(primary, DEFAULT_W)
                primary_detail_map = DETAIL_TYPE_MAPS.get(primary, {})
                X = primary_detail_map.get(detail, DEFAULT_X)
                Y = LEVEL_MAP.get(level, DEFAULT_Y)

                # --- Warnings for missing dimension data (same as before) ---
                if primary is None:
                    current_warnings += 1
                    print("  [Warning] Missing dimensions.type.primary")
                elif W == DEFAULT_W:
                    current_warnings += 1
                    print(
                        f"  [Warning] Unmapped primary type: '{primary}'. Using W={DEFAULT_W}")
                if detail is None:
                    current_warnings += 1
                    print("  [Warning] Missing dimensions.type.detail")
                elif X == DEFAULT_X and primary in DETAIL_TYPE_MAPS:
                    current_warnings += 1
                    print(
                        f"  [Warning] Unmapped detail type: '{detail}' for primary '{primary}'. Using X={DEFAULT_X}")
                elif primary not in DETAIL_TYPE_MAPS and primary is not None:
                    current_warnings += 1
                    print(
                        f"  [Warning] No detail map defined for primary type: '{primary}'. Using X={DEFAULT_X}")
                if level is None:
                    current_warnings += 1
                    print("  [Warning] Missing dimensions.level")
                elif Y == DEFAULT_Y:
                    current_warnings += 1
                    print(
                        f"  [Warning] Unmapped level: '{level}'. Using Y={DEFAULT_Y}")

                # --- Construct New Filename using standard_title and language ---
                prefix_str = f"{P}{W}{X}{Y}"
                try:
                    numeric_prefix = int(prefix_str)
                    padded_prefix = f"{numeric_prefix:04d}"
                except ValueError:
                    print(
                        f"  [Error] Could not form numeric prefix from P={P}, W={W}, X={X}, Y={Y}. Using '0000'.")
                    padded_prefix = "0000"
                    error_count += 1
                    continue  # Skip file

                # Determine title part (use standard_title or fallback)
                title_part_to_use = standard_title
                if not title_part_to_use:
                    print(
                        "  [Warning] Missing 'standard_title'. Using original filename base as fallback.")
                    current_warnings += 1
                    title_part_to_use = os.path.splitext(filename)[
                        0]  # Fallback

                sanitized_title = sanitize_filename_part(title_part_to_use)
                print(
                    f"  Using Title: '{title_part_to_use}' -> Sanitized: '{sanitized_title}'")

                # Determine language suffix
                lang_suffix = ""
                if language:
                    lang_code = str(language).strip().lower()
                    if lang_code:
                        lang_suffix = f".{lang_code}"
                        print(
                            f"  Using Language: '{language}' -> Suffix: '{lang_suffix}'")
                    else:
                        print(
                            "  [Warning] Empty 'language' field found. Omitting suffix.")
                        current_warnings += 1
                else:
                    print(
                        "  [Warning] Missing 'language' field. Omitting suffix.")
                    current_warnings += 1

                # Combine parts
                new_filename = f"{padded_prefix}-[{sanitized_title}]{lang_suffix}.md"
                print(
                    f"  Calculated PWXY: {padded_prefix} (P={P}, W={W}, X={X}, Y={Y})")
                print(f"  Generated Filename: {new_filename}")

                target_filepath = os.path.join(target_dir, new_filename)

                # --- Check for Collisions ---
                if os.path.exists(target_filepath):
                    print(
                        f"  [Skipping] Target file already exists: {new_filename}")
                    skipped_count += 1
                    continue

                # --- Prepare New Content ---
                try:
                    new_yaml_str = yaml.dump(
                        front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)
                except Exception as dump_error:
                    print(
                        f"  [Error] Failed to dump updated YAML: {dump_error}")
                    error_count += 1
                    continue

                new_content = f"---\n{new_yaml_str}---\n\n{markdown_content}"

                # --- Write New File ---
                with open(target_filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print("  [Success] File processed and saved.")
                processed_count += 1
                if current_warnings > 0:
                    warning_count += 1  # Increment file warning count if this file had warnings

            except FileNotFoundError:
                print(
                    f"  [Error] File not found during processing: {original_filepath}")
                error_count += 1
            except Exception as e:
                print(
                    f"  [Error] Unexpected error processing file '{relative_path}': {e}")
                import traceback
                traceback.print_exc()
                error_count += 1

    # --- Final Report ---
    print("\n--- Processing Complete ---")
    print(f"Successfully processed: {processed_count} files")
    print(f"Skipped (target exists): {skipped_count} files")
    print(f"Files with warnings (missing/unmapped data): {warning_count}")
    print(f"Errors encountered: {error_count} files")
    print("-" * 27)


# --- Script Entry Point ---
if __name__ == "__main__":
    if not os.path.isdir(SOURCE_DIR):
        print(
            f"Error: Source directory '{SOURCE_DIR_NAME}' not found in '{BASE_DIR}'.")
    else:
        process_markdown_files(SOURCE_DIR, TARGET_DIR)
