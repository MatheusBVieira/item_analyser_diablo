import enum
import re

from PIL import Image
from pytesseract import pytesseract

class OS(enum.Enum):
    Windows = 1

class Language(enum.Enum):
    ENG = 'eng'

class ImageReader:

    def __init__(self, os: OS):
        if os == os.Windows:
            windows_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pytesseract.tesseract_cmd = windows_path

    def extract_text(self, image: str,  lang: str) -> str:
        img = Image.open(image)
        extracted_text = pytesseract.image_to_string(img, lang=lang)
        return extracted_text

if __name__ == '__main__':
    ir = ImageReader(OS.Windows)
    text = ir.extract_text('images/anel2.png', lang='eng')

    print(text)

    # Expressões regulares para extrair as informações desejadas
    padrao_nome_item = r"(?<=\n)[A-Z\s]+"
    padrao_item_power = r"\d+ Item Power"
    padrao_armadura = r"\d+ Armor"
    padrao_aspecto = r"\*.+?(?=\n\n)"
    item_type_pattern = r"(?<=Legendary |Unique )\w+"

    # Função para obter o tipo de item
    def get_item_type(item_text):
        match = re.search(item_type_pattern, item_text)
        if match:
            item_type = match.group().lower()
            if item_type in ["amulet", "ring"]:
                return "amulet/ring"
            elif item_type in ["sword", "dagger"]:
                return "sword/dagger"
            else:
                return "other"
        else:
            return "unknown"

    def extract_attributes(item_text, item_type):
        # Início e fim da região de atributos
        start_keywords = ["Item Power"]
        end_keywords = ["Aspect", "Requires Level"]

        # Encontrar os índices de início e fim da região de atributos
        start_index = end_index = None
        for keyword in start_keywords:
            start_index = item_text.find(keyword)
            if start_index != -1:
                start_index += len(keyword)
                break
        
        for keyword in end_keywords:
            end_index = item_text.find(keyword)
            if end_index != -1:
                break

        if start_index is not None and end_index is not None:
            attributes_text = item_text[start_index:end_index]
        else:
            attributes_text = item_text  # usar todo o texto se a região de atributos não puder ser determinada

        # Extrair os atributos
        lines = attributes_text.split('\n')
        attributes = []
        for line in lines:
            # Adicionar a linha aos atributos se ela contiver um número
            if re.search(r'\d', line):
                line = re.sub(r'^[^+\d]*', '', line)  # remover caracteres não desejados do início da linha
                attributes.append(line.strip())
            # Parar de adicionar linhas aos atributos se a linha começar com '*'
            elif line.startswith('*'):
                break
            # Ignorar a linha se contiver "a eee"
            elif "a eee" in line:
                continue
                    
        return attributes


    # Função para verificar o tipo de item
    def get_item_type(item_text):
        if "Amulet" in item_text or "Ring" in item_text:
            return "amulet/ring"
        elif "Sword" in item_text or "Dagger" in item_text:
            return "sword/dagger"
        else:
            return "other"

    # Extrair as informações usando as expressões regulares
    nome_item = re.search(padrao_nome_item, text).group()
    item_power = re.search(padrao_item_power, text).group().split()[0]
    armadura = ""
    item_type = get_item_type(text)
    atributos = extract_attributes(text, item_type)
    aspecto = re.findall(padrao_aspecto, text, re.DOTALL)
    item_type = get_item_type(text)

    # Verificar o tipo de item e ajustar a extração de atributos
    if item_type == "amulet/ring":
        armadura = "N/A"
    elif item_type == "sword/dagger":
        armadura = "Dano"
    else:
        armadura_match = re.search(padrao_armadura, text)
        if armadura_match:
            armadura = armadura_match.group().split()[0]
        else:
            armadura = "Armadura"

    # Exibir as informações extraídas
    print("Nome do item:", nome_item.strip())
    print("Item Power:", item_power)
    print("Armadura:", armadura)
    print("Atributos:", atributos)
    print("Aspecto:", aspecto)
