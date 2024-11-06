import os
import re
from bs4 import BeautifulSoup

input_dir = "scripts/"  
output_dir = "cleaned_scripts/"  

os.makedirs(output_dir, exist_ok=True)

def clean_script(file_path, output_path):
    with open(file_path, "r", encoding="iso-8859-1") as file:
        soup = BeautifulSoup(file, "html.parser")

        cleaned_content = []

        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            cleaned_content.append(f"Title: {title_text}")

        pre_tags = soup.find_all("pre")
        for pre in pre_tags:
            text = pre.get_text(separator=" ", strip=True)
            text = re.sub(r'\s+', ' ', text)  
            text = re.sub(r'[^\x00-\x7F]+', '', text)  
            cleaned_content.append(text)

        cleaned_text = "\n\n".join(cleaned_content)

        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(cleaned_text)
        print(f"Cleaned script saved to: {output_path}")

for filename in os.listdir(input_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.txt")
        clean_script(file_path, output_path)
