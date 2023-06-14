import enum
import re
import tkinter as tk
import cv2
import numpy as np
from tkinter import messagebox, ttk
from PIL import ImageGrab, Image
from PIL import ImageTk
from pytesseract import pytesseract
from io import BytesIO
import json

class OS(enum.Enum):
    Windows = 1

class Language(enum.Enum):
    ENG = 'eng'


class ItemAttributes:
    def __init__(self, item_type, item_power, armor, attributes, item_weight):
        self.item_type = item_type
        self.item_power = item_power
        self.armor = armor
        self.attributes = attributes
        self.item_weight = item_weight

    def __str__(self):
        attr_str = '\n'.join(self.attributes)
        return f"Item: {self.item_type}\nItem Power: {self.item_power}\nArmor: {self.armor}\nAttributes:\n{attr_str}\nItem Weight: {self.item_weight}"

class Item:
    def __init__(self, tipo, weights):
        self.tipo = tipo
        self.atributos = {}
        self.weights = weights

    def adicionar_atributo(self, nome, valor):
        self.atributos[nome] = valor

    def calcular_peso(self):
        peso_total = 0
        if self.tipo in self.weights:
            atributos_item = self.atributos.keys()
            for atributo in atributos_item:
                if atributo in self.weights[self.tipo]:
                    peso_total += self.weights[self.tipo][atributo]

        return peso_total
    
    @staticmethod
    def from_attributes(attributes: ItemAttributes):
        item = Item(attributes.item_type, attributes.item_weight)
        item.atributos = attributes.attributes
        return item

class ItemCollection:
    def __init__(self):
        self.itens = {}

    def adicionar_item(self, tipo, item):
        self.itens[tipo] = item

    def calcular_peso_total(self):
        return sum(item.calcular_peso() for item in self.itens.values())
    
    def compare_items(self, itemNovo: Item, itemEquipado: Item):
        weight_total_novo = 0
        weight_total_equipado = 0

        # Calcula o peso total do item novo
        if itemNovo.tipo in itemNovo.weights:
            for attribute in itemNovo.atributos.keys():
                if attribute in itemNovo.weights[itemNovo.tipo]:
                    weight_total_novo += itemNovo.weights[itemNovo.tipo][attribute]

        # Calcula o peso total do item equipado
        if itemEquipado.tipo in itemEquipado.weights:
            for attribute in itemEquipado.atributos.keys():
                if attribute in itemEquipado.weights[itemEquipado.tipo]:
                    weight_total_equipado += itemEquipado.weights[itemEquipado.tipo][attribute]

        # Compara o peso total e os valores dos atributos
        if weight_total_novo > weight_total_equipado:
            tk.Label(attribute_frame_status, text=f"O item novo tem maior peso total.").pack()
        elif weight_total_novo < weight_total_equipado:
            tk.Label(attribute_frame_status, text=f"O item equipado tem maior peso total.").pack()
        else:
            tk.Label(attribute_frame_status, text=f"Os itens têm o mesmo peso total.").pack()

        for attr, value in itemNovo.atributos.items():
            if attr in itemEquipado.atributos:
                if value > itemEquipado.atributos[attr]:
                    tk.Label(attribute_frame_status, text=f"O item novo tem maior valor para o atributo {attr}.").pack()
                    print(f"O item novo tem maior valor para o atributo {attr}.")
                elif value < itemEquipado.atributos[attr]:
                    tk.Label(attribute_frame_status, text=f"O item equipado tem maior valor para o atributo {attr}.").pack()
                    print(f"O item equipado tem maior valor para o atributo {attr}.")
                else:
                    print(f"Os itens têm o mesmo valor para o atributo {attr}.")

        return weight_total_novo, weight_total_equipado
    
class ImageReader:
    def __init__(self, os: OS):
        if os == os.Windows:
            windows_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pytesseract.tesseract_cmd = windows_path

    def preprocess_image(self, image_io):
        image = Image.open(image_io)
        img_np = np.array(image)

        # Convert image to grayscale if it has more than one channel
        if len(img_np.shape) > 2 and img_np.shape[2] > 1:
            gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_np

        # Manually set threshold and apply global binarization
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

        # Save the preprocessed image for OCR
        cv2.imwrite('images/preprocessed_image.png', thresh)
        return 'images/preprocessed_image.png'

    def extract_text(self, image: Image.Image, lang: str) -> str:
        preprocessed_image = self.preprocess_image(image)
        preprocessed_image = self.preprocess_image(preprocessed_image)
        img = Image.open(preprocessed_image)
        extracted_text = pytesseract.image_to_string(img, lang=lang)
        return extracted_text

item_collection = ItemCollection()

def load_items(filepath, item_collection):
    with open(filepath) as f:
        data = json.load(f)
    weights = data['weights']
    items_data = data['my_items']  # This is a list of items
    for item_data in items_data:  # Iterate over each item
        tipo = item_data['type']
        item = Item(tipo, weights)
        for nome, valor in item_data['attributes'].items():
            item.adicionar_atributo(nome, valor)
        item_collection.adicionar_item(tipo, item)
    return weights

weights = load_items('wheights.json', item_collection)

def on_paste(event):
    image = ImageGrab.grabclipboard()

    for widget in attribute_frame_print.winfo_children():
        widget.destroy()

    for widget in attribute_frame_status.winfo_children():
        widget.destroy()

    if image is not None:
        image = image.convert("RGB")
        image_io = BytesIO()
        image.save(image_io, format="PNG")
        image_io.seek(0)
        text = ir.extract_text(image_io, lang='eng')
        print(text)
        photo_image = ImageTk.PhotoImage(image)  # create PhotoImage
        image_label.configure(image=photo_image)  # assign PhotoImage to label
        image_label.image = photo_image  # keep a reference to the image

        tipo_item = item_type_var.get()
        item_attributes = extract_information(text, item_collection.itens[tipo_item], tipo_item)

        print(item_attributes)
        
        tk.Label(attribute_frame_print, text=f"Item Type: {item_attributes.item_type}").pack()
        tk.Label(attribute_frame_print, text=f"Item power: {item_attributes.item_power}").pack()
        tk.Label(attribute_frame_print, text=f"Item armor: {item_attributes.armor}").pack()
        tk.Label(attribute_frame_print, text=f"Atributos: ").pack()
        for atributo in item_attributes.attributes:
            tk.Label(attribute_frame_print, text=f"- {atributo}").pack()

        new_item_parsed = Item.from_attributes(item_attributes)

        item_collection.compare_items(new_item_parsed, item_collection.itens[tipo_item])
    else:
        messagebox.showerror("Erro", "Nenhuma imagem válida encontrada no clipboard.")

def criar_item(weights):
    tipo_item = item_type_var.get()
    item = Item(tipo_item, weights)
    return item

def extract_information(text, item, tipo_item):
    item_power_pattern = r'\d{1,3}\sItem Power'
    item_power = re.search(item_power_pattern, text)
    if item_power:
        item.adicionar_atributo("Item Power", int(item_power.group().split()[0]))
    
    armadura_pattern = r'\d{1,3}\sArmor'
    armadura_match = re.search(armadura_pattern, text)
    if armadura_match:
        item.adicionar_atributo("Armor", int(armadura_match.group().split()[0]))

    atributos = extract_attributes(text, item)

    return ItemAttributes(
        tipo_item,
        item_power.group() if item_power else 'N/A',
        armadura_match.group() if armadura_match else 'N/A',
        atributos,
        weights
    )

def extract_attributes(item_text, item_type):
    # Início e fim da região de atributos
    start_keywords = ["Item Power"]
    end_keywords = ["Requires Level"]

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
    attributes = {}
    previous_line = ""
    for line in lines:
        if line.strip() == "":
            continue
        # Juntar linhas de apenas números com a linha anterior
        if re.match(r'^\d+(\.\d+)?$', line.strip()):
            continue
        else:
            # Remover caracteres indesejados
            line = line.replace("—", "-")
            line = re.sub(r'[\[\]+-]', '', line)
            # Aplicar a regra para deixar apenas "float str str..."
            attribute = ' '.join([x for x in line.split() if not re.match(r'^[\d.-]+|\||\[|\]$', x)])
            # Encontrar o valor do atributo (float no início da linha)
            value = re.search(r'^[\d.-]+', line)
            if attribute and value:
                attributes[attribute] = float(value.group())

    return attributes

def on_item_type_changed(event):
    # Clear the current attributes
    for widget in attribute_frame.winfo_children():
        widget.destroy()

    # Load items from file
    with open('wheights.json') as f:
        data = json.load(f)

    item_type = item_type_var.get()
    item_datas = data['my_items']  # This is a list, not a single item
    item_data = next((item for item in item_datas if item['type'] == item_type), None)  # Find the desired item

    tk.Label(attribute_frame, text="Meu item:").pack()
    tk.Label(attribute_frame, text=f"Peso total: {item_collection.calcular_peso_total()}").pack()

    if item_data:  # If the desired item is found
        for name, value in item_data['attributes'].items():
            tk.Label(attribute_frame, text=f"{value} {name}").pack()
    else:
        tk.Label(attribute_frame, text="No attributes for this item type.").pack()

    item_type_dropdown.bind('<<ComboboxSelected>>', on_item_type_changed)

root = tk.Tk()
root.geometry("800x1000")
root.title("Equip Compare")
root.bind('<Control-v>', on_paste)

ir = ImageReader(OS.Windows)

attribute_frame = tk.Frame(root)
attribute_frame.grid(column=1, row=1)

attribute_frame_status = tk.Frame(root)
attribute_frame_status.grid(column=1, row=2)

attribute_frame_print = tk.Frame(root)
attribute_frame_print.grid(column=0, row=2)

item_type_var = tk.StringVar()
item_type_var.set('Amulet')  # set initial value
item_type_dropdown = ttk.Combobox(root, textvariable=item_type_var)
item_type_dropdown['values'] = ('Amulet', 'Ring', 'Belt', 'Boots', 'Chest', 'Gloves', 'Helmet', 'Pants', 'Shoulder', 'Weapon 1H', 'Weapon 2H')
item_type_dropdown.grid(column=0, row=0)

image_label = tk.Label(root)
image_label.grid(column=0, row=1)

on_item_type_changed(None)

root.mainloop()
