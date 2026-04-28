import os

# Ignore list to prevent the text file from becoming massive or crashing
IGNORE_LIST = {
    '__pycache__', '.git', '.venv', 'venv', '.ipynb_checkpoints', 
    'node_modules', '.vscode', 'serviceAccountKey.json', 'ffmpeg.exe',
    'project_dump.txt', 'full_dump.py'
}

# Only capture code and text files
INCLUDE_EXTENSIONS = {'.py', '.txt', '.json', '.html', '.css'}

def dump_entire_project(startpath, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"PROJECT STRUCTURE DUMP\nRoot: {startpath}\n{'='*50}\n\n")
        
        for root, dirs, files in os.walk(startpath):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_LIST]
            
            # Create a visual tree structure in the TXT
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f'{indent}📂 {os.path.basename(root)}/\n')
            
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                # Skip non-code files or ignored files
                if file in IGNORE_LIST or os.path.splitext(file)[1] not in INCLUDE_EXTENSIONS:
                    continue
                    
                file_path = os.path.join(root, file)
                f.write(f'{sub_indent}📄 {file}\n')
                
                # Write the actual content of the file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as code_file:
                        content = code_file.read()
                        f.write(f'\n{sub_indent}{"#"*10} START OF {file} {"#"*10}\n')
                        f.write(content)
                        f.write(f'\n{sub_indent}{"#"*10} END OF {file} {"#"*10}\n\n')
                except Exception as e:
                    f.write(f'{sub_indent}[Error reading {file}: {e}]\n')

if __name__ == "__main__":
    # This grabs the folder the script is currently sitting in
    current_folder = os.getcwd() 
    output_name = "full_project_dump.txt"
    
    print(f"Starting dump from: {current_folder}")
    dump_entire_project(current_folder, output_name)
    print(f"✅ SUCCESS! File created: {output_name}")