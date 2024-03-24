import pdfkit

def convert_html_to_pdf(html_string, pdf_path):
    pdfkit.from_string(html_string, pdf_path)
    return True  # Assuming the function succeeds without raising an exception
