from bs4 import BeautifulSoup

def parse_and_write(html_content, output_file='elements.txt'):
    soup = BeautifulSoup(html_content, 'html.parser')
    interactive_tags = ['a', 'button', 'input', 'select', 'textarea']
    elements = []

    for tag in interactive_tags:
        for element in soup.find_all(tag):
            element_info = {}
            element_info['tag'] = tag
            element_info['id'] = element.get('id', '')
            element_info['class'] = ' '.join(element.get('class', []))
            element_info['name'] = element.get('name', '')
            element_info['type'] = element.get('type', '') if tag == 'input' else ''
            element_info['text'] = element.get_text(strip=True) if tag in ['a', 'button'] else ''

            elements.append(element_info)

    with open(output_file, 'w', encoding='utf-8') as f:
        for elem in elements:
            f.write(f"Tag: {elem['tag']}\n")
            if elem['id']:
                f.write(f"  ID: {elem['id']}\n")
            if elem['class']:
                f.write(f"  Class: {elem['class']}\n")
            if elem['name']:
                f.write(f"  Name: {elem['name']}\n")
            if elem['type']:
                f.write(f"  Type: {elem['type']}\n")
            if elem['text']:
                f.write(f"  Text: {elem['text']}\n")
            f.write("\n")