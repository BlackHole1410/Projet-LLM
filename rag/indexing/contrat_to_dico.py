import os
from bs4 import BeautifulSoup
def get_contrat_from_file(file_path):
    """
    Extracts and structures text from a specified HTML file.

    Args:
        file_path (str): The path to the HTML file.

    Returns:
        dict: A dictionary containing structured content of the HTML file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        
        # Get the title of the HTML file
        title = soup.title.string if soup.title else os.path.splitext(os.path.basename(file_path))[0]
        
        # Initialize the document structure
        document_content = {
            'title': title,
            'paragraphs': [],
            'headings': {}
        }
        
        # Extract paragraphs
        for p in soup.find_all('p'):
            document_content['paragraphs'].append(p.get_text())
        
        # Extract h2 and h3 headings
        for h2 in soup.find_all('h2'):
            h2_text = h2.get_text()
            h2_content = ""
            h2_sibling = h2.find_next_sibling()
            
            while h2_sibling and h2_sibling.name != 'h2':
                if h2_sibling.name == 'ul' or h2_sibling.name == 'ol':
                    h2_content += h2_sibling.get_text(separator="\n")
                elif h2_sibling.name == 'h3':
                    break
                h2_sibling = h2_sibling.find_next_sibling()
            
            document_content['headings'][h2_text] = {
                'content': h2_content.strip(),
                'subheadings': {}
            }
            
            for h3 in h2.find_all_next('h3'):
                if h3.find_previous('h2') == h2:
                    h3_text = h3.get_text()
                    h3_content = ""
                    h3_sibling = h3.find_next_sibling()
                    
                    while h3_sibling and h3_sibling.name not in ['h2', 'h3']:
                        if h3_sibling.name == 'ul' or h3_sibling.name == 'ol':
                            h3_content += h3_sibling.get_text(separator="\n")
                        h3_sibling = h3_sibling.find_next_sibling()
                    
                    document_content['headings'][h2_text]['subheadings'][h3_text] = h3_content.strip()
    
    return document_content
