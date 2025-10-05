import os
import argparse
import time

parser = argparse.ArgumentParser(description="Combine code files into a markdown document.")
parser.add_argument('--output', required=True, help='Output markdown file path')
parser.add_argument('--folders', required=True, help='Comma-separated list of folders to scan')
parser.add_argument('--extensions', required=True, help='Comma-separated list of file extensions to include')
parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
args = parser.parse_args()
args_verbose=True

folders = [f.strip() for f in args.folders.split(',')]
extensions = [e.strip() for e in args.extensions.split(',')]
output_file = args.output

if args_verbose:
    print(f"Directory: {os.getcwd()}")

output_dir = os.path.dirname(output_file)
if output_dir and not os.path.exists(output_dir):
    try:
        os.makedirs(output_dir)
        if args_verbose:
            print(f"Created output directory: {output_dir}")
    except Exception as e:
        print(f"Failed to create output directory '{output_dir}': {e}")
        exit(1)

if os.path.exists(output_file):
    try:
        timestamp = time.strftime("%Y%m%d%H%M%S")
        dirname, filename = os.path.split(output_file)
        new_name = f"sourcefold_{timestamp}_{filename}"
        new_path = os.path.join(dirname, new_name)
        os.rename(output_file, new_path)
        if args_verbose:
            print(f"Renamed existing output file to: {new_path}")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        exit(1)

def find_files(folders, extensions):
    matched_files = []
    for folder in folders:
        print('┌'+folder+'/')
        for root, _, files in os.walk(folder):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, file)
                    matched_files.append(full_path)
                    if args_verbose:
                        print_file=full_path.replace(folder+'/','├'+('─' * (len(folder)-1)))
                        print(f"{print_file}")
        print('└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────── ')
    return matched_files

files = find_files(folders, extensions)
if not files:
    print(f"No files with extensions {extensions} found in folders {folders}.")
    exit(1)

def combine_files_to_markdown(file_paths, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as md:
            for path in file_paths:
                ext = os.path.splitext(path)[1][1:]
                md.write(f'## {path}\n\n')
                md.write(f'```{ext}\n')
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    md.write(content)
                md.write('\n```\n\n---\n\n')
                if args_verbose:
                    # print(f"Appended: {path}")
                    pass
    except FileNotFoundError as e:
        print(f"Error writing to output file: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

combine_files_to_markdown(files, output_file)

if args_verbose:
    print(f"\nCombined markdown file created: {output_file}")
