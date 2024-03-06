import html2text

def convert_html_to_text(html, output_path):
    config = html2text.HTML2Text()
    config.ignore_links = True
    config.ignore_images = True
    config.ignore_tables = True
    config.body_width = 0
    text_content = config.handle(html)
    
    # Save the text content to the specified output path
    with open(output_path, 'w', encoding='utf-8') as text_file:
        text_file.write(text_content)

