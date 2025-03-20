import os
import html2text

# Function to convert HTML file to Markdown
def convert_html_to_markdown(html_file_path, markdown_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()
    
    markdown_content = html2text.html2text(html_content)
    
    with open(markdown_file_path, 'w', encoding='utf-8') as markdown_file:
        markdown_file.write(markdown_content)

# Directory containing the HTML files
html_directory = 'path/to/html/files'
# Directory to save the converted Markdown files
markdown_directory = 'path/to/markdown/files'

# Ensure the markdown directory exists
os.makedirs(markdown_directory, exist_ok=True)

# Convert each HTML file in the directory to Markdown
for html_file_name in os.listdir(html_directory):
    if html_file_name.endswith('.html'):
        html_file_path = os.path.join(html_directory, html_file_name)
        markdown_file_name = os.path.splitext(html_file_name)[0] + '.md'
        markdown_file_path = os.path.join(markdown_directory, markdown_file_name)
        
        convert_html_to_markdown(html_file_path, markdown_file_path)
        print(f'Converted {html_file_name} to {markdown_file_name}')
