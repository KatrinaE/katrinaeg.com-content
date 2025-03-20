import os

def split_line(line, max_length):
    words = line.split()
    new_lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_length:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            new_lines.append(current_line)
            current_line = word

    if current_line:
        new_lines.append(current_line)

    return new_lines

def adjust_file_lines(input_file, max_length=80):
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}-80charlines{ext}"

    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    new_lines = []
    for line in lines:
        new_lines.extend(split_line(line.strip(), max_length))

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("\n".join(new_lines) + "\n")

    print(f"Adjusted lines written to {output_file}")

# Example usage:
input_file = 'content/hs-reflections.md'
adjust_file_lines(input_file)
