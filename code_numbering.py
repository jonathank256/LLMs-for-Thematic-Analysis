import os 
import re

MODE = "novice" # options: "novice", "expert", "all"

def load_txt(filename): 
    with open(filename, "r", encoding="utf-8") as f: 
        return [line.strip() for line in f if line.strip()] # Load files and strip whitespace 

def clean_line(line):
    return re.sub(r"^Code\s*\d+:\s*", "", line) # Remove existing number labels using RegEx (e.g. "Code 5: ")

def number_codes(lines, prefix, include_prefix=True):
    numbered = []
    for i, line in enumerate(lines, start=1):
        clean = clean_line(line) # Remove previous labels 
        if include_prefix: # A prefix option if we ever need it 
            numbered.append(f"{prefix} Code {i}: {clean}") 
        else:
            numbered.append(f"Code {i}: {clean}") # Add new line with correct code # and the rest of the text
    return numbered

def combine_and_number(folder, prefix, output_file, pattern, include_prefix=True):
    all_lines = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".txt") and re.match(pattern, filename):
            filepath = os.path.join(folder, filename)
            lines = load_txt(filepath)
            all_lines.extend(lines) # Combining all the files 

    numbered = number_codes(all_lines, prefix, include_prefix)

    with open(output_file, "w", encoding="utf-8") as f: # Write to file 
        for line in numbered:
            f.write(line + "\n")

def concatenate_codes(novice, expert, output_file = "concatenated_codes.txt"):
    novice_lines = load_txt(novice)
    expert_lines = load_txt(expert)

    novice_numbered = number_codes(novice_lines, "Novice")
    expert_numbered = number_codes(expert_lines, "Expert")
    
    combined = novice_numbered + expert_numbered

    with open(output_file, "w", encoding="utf-8") as f: # Write to file 
        for line in combined:
            f.write(line + "\n")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    checks_dir = os.path.join(base_dir, "2-TA-checks") # ASSUMPTION: Files are to be retrieved from 2-TA-checks 

    novice_output = os.path.join(checks_dir, "novice_codes.txt")
    expert_output = os.path.join(checks_dir, "expert_codes.txt")
    combined_output = os.path.join(checks_dir, "concatenated_codes.txt")

    if MODE == "novice":    # RegEx patterns ensure all files of same expertise are combined 
        combine_and_number(checks_dir, "Novice", novice_output, r"novice_\d+\.txt", include_prefix=False)
    elif MODE == "expert":
        combine_and_number(checks_dir, "Expert", expert_output, r"expert_\d+\.txt", include_prefix=False)
    elif MODE == "all":
        combine_and_number(checks_dir, "Novice", novice_output, r"novice_\d+\.txt", include_prefix=False)
        combine_and_number(checks_dir, "Expert", expert_output, r"expert_\d+\.txt", include_prefix=False)
        concatenate_codes(novice_output, expert_output, combined_output)
    else:
        print("Invalid MODE. Choose 'novice', 'expert', or 'all'.")




