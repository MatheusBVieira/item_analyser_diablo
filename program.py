import tkinter as tk
import json

from tkinter import messagebox, ttk
from PIL import ImageGrab, ImageTk
from io import BytesIO

from image_reader import ImageReader, OS
from item import ItemAttributes, Item, ItemCollection
from constants import weights, equipped_items

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

        photo_image = ImageTk.PhotoImage(image)
        image_label.configure(image=photo_image)
        image_label.image = photo_image 

        tipo_item = item_type_var.get()
        new_item_attributes = ItemAttributes.from_text(text, tipo_item)

        print(new_item_attributes)
        
        tk.Label(attribute_frame_print, text=f"Item Type: {new_item_attributes.item_type}").pack()
        tk.Label(attribute_frame_print, text=f"Item power: {new_item_attributes.item_power}").pack()
        tk.Label(attribute_frame_print, text=f"Item armor: {new_item_attributes.armor}").pack()
        tk.Label(attribute_frame_print, text=f"Atributos: ").pack()
        for atributo in new_item_attributes.attributes:
            tk.Label(attribute_frame_print, text=f"- {atributo}").pack()

        new_item_parsed = Item.from_attributes(new_item_attributes)
        itemEquipado_dict = equipped_items[tipo_item] #atributos item equipado
        itemEquipado = Item.from_dict(tipo_item, itemEquipado_dict)

        messages = ItemCollection.compare_items(new_item_parsed, itemEquipado)

        for message in messages:
            tk.Label(attribute_frame_status, text=message).pack()
    else:
        messagebox.showerror("Erro", "Nenhuma imagem válida encontrada no clipboard.")

def on_item_type_changed(event):
    # Clear the current attributes
    for widget in attribute_frame.winfo_children():
        widget.destroy()

    # Load items from file
    item_type = item_type_var.get()
    item_datas = equipped_items  # This is a list, not a single item
    item_data = item_datas.get(item_type, None)  # Find the desired item

    tk.Label(attribute_frame, text="My Item:").pack()
    # tk.Label(attribute_frame, text=f"Total weight: {item_collection.calcular_peso_total()}").pack()

    if item_data:  # If the desired item is found
        for name, value in item_data.items():
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
