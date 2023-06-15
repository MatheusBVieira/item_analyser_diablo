import re

from constants import weights

class ItemAttributes:
    def __init__(self, item_type, item_power, armor, attributes):
        self.item_type = item_type
        self.item_power = item_power
        self.armor = armor
        self.attributes = attributes

    @staticmethod
    def from_text(text, tipo_item):
        item_power_pattern = r'\d{1,3}\sItem Power'
        item_power = re.search(item_power_pattern, text)
        
        armadura_pattern = r'\d{1,3}\sArmor'
        armadura_match = re.search(armadura_pattern, text)

        atributos = ItemAttributes.extract_attributes(text)

        return ItemAttributes(
            tipo_item,
            item_power.group() if item_power else 'N/A',
            armadura_match.group() if armadura_match else 'N/A',
            atributos
        )

    @staticmethod
    def extract_attributes(item_text):
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
    
    def __str__(self):
        attr_str = '\n'.join(self.attributes)
        return f"Item: {self.item_type}\nItem Power: {self.item_power}\nArmor: {self.armor}\nAttributes:\n{attr_str}"

class Item:
    def __init__(self, tipo):
        self.tipo = tipo
        self.atributos = {}

    def adicionar_atributo(self, nome, valor):
        self.atributos[nome] = valor

    def calcular_peso(self):
        peso_total = 0
        if self.tipo in weights:
            atributos_item = self.atributos.keys()
            for atributo in atributos_item:
                if atributo in weights[self.tipo]:
                    peso_total += weights[self.tipo][atributo]

        return peso_total
    
    @staticmethod
    def from_attributes(attributes: ItemAttributes):
        item = Item(attributes.item_type)
        item.atributos = attributes.attributes
        return item
    
    @staticmethod
    def from_dict(item_type, item_dict):
        item = Item(item_type)
        item.atributos = item_dict
        return item

class ItemCollection:
    def __init__(self):
        self.itens = {}

    def adicionar_item(self, tipo, item):
        self.itens[tipo] = item

    def calcular_peso_total(self):
        return sum(item.calcular_peso() for item in self.itens.values())
    
    @staticmethod
    def compare_items(itemNovo: Item, itemEquipado: Item):
        messages = []

        weight_total_novo = 0
        weight_total_equipado = 0

        if itemNovo.tipo in weights:
            for attribute in itemNovo.atributos.keys():
                if attribute in weights[itemNovo.tipo]:
                    weight_total_novo += weights[itemNovo.tipo][attribute]

        if itemEquipado.tipo in weights:
            for attribute in itemEquipado.atributos.keys():
                if attribute in weights[itemEquipado.tipo]:
                    weight_total_equipado += weights[itemEquipado.tipo][attribute]

        # Compara o peso total e os valores dos atributos
        if weight_total_novo > weight_total_equipado:
            messages.append("O item novo tem maior peso total.")
        elif weight_total_novo < weight_total_equipado:
            messages.append("O item equipado tem maior peso total.")
        else:
            messages.append("Os itens têm o mesmo peso total.")

        for attr, value in itemNovo.atributos.items():
            if attr in itemEquipado.atributos:
                if value > itemEquipado.atributos[attr]:
                    messages.append(f"O item novo tem maior valor para o atributo {attr}.")
                    print(f"O item novo tem maior valor para o atributo {attr}.")
                elif value < itemEquipado.atributos[attr]:
                    messages.append(f"O item equipado tem maior valor para o atributo {attr}.")
                    print(f"O item equipado tem maior valor para o atributo {attr}.")
                else:
                    print(f"Os itens têm o mesmo valor para o atributo {attr}.")

        return weight_total_novo, weight_total_equipado, messages