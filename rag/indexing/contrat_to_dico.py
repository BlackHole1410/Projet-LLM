from bs4 import BeautifulSoup
import os

def get_contrat(directory):
    """
    Extracts and structures text from HTML files in the specified directory.

    Args:
        directory (str): The directory containing the HTML files.

    Returns:
        dict: A dictionary where keys are document names and values are structured content.
    """
    documents = {}

    for html_file in os.listdir(directory):
        if html_file.endswith('.html'):
            file_path = os.path.join(directory, html_file)
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                
                # Get the title of the HTML file
                title = soup.title.string if soup.title else os.path.splitext(html_file)[0]
                
                # Initialize the document structure
                document_content = {
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
                
                # Add the structured content to the documents dictionary
                documents[title] = document_content
    
    return documents

# # Example usage
# import os 
# print(os.getcwd())
# path='tests'
# get_contrat(path)
