from docx import Document
from htmldocx import HtmlToDocx
def Html2Word(html_string, output_file):
    
    document = Document()
    new_parser = HtmlToDocx()
    # do stuff to document

    html = html_string
    new_parser.add_html_to_document(html, document)

    # do more stuff to document
    document.save(output_file)
