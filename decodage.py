import json
import re

from ORM import add_invoice, connectBd, createsession
from surveillance import surveillanceAllInOne


def load_json_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def inThePoint(point, box):

    x, y = point
    x_coordinates = box[::2]  
    y_coordinates = box[1::2]  
    if min(x_coordinates) <= x <= max(x_coordinates) and min(y_coordinates) <= y <= max(y_coordinates):
        return True
    else:
        return False


def inTheSegment(segment, box):
    x1, y1, x2, y2 = segment
    x_min = min(box[::2])
    y_min = min(box[1::2])
    x_max = max(box[::2])
    y_max = max(box[1::2])

    # if (x1 <= x_max and x2 >= x_min and
    #     y1 <= y_max and y2 >= y_min):
    #     return True

    # Vérifie si un coin de la boîte se trouve sur le segment
    if (x1 <= x_max and x1 >= x_min and
        y1 <= y_max and y1 <= y_min):
        return True
    if (x2 <= x_max and x2 >= x_min and
        y2 >= y_max and y2 >= y_min):
        return True

    return False




position = { 
    'id': [143, 30],
    'date': [159, 59],
    'client': [86, 89],
    'adresse1': [79, 125],
    'adresse2': [79, 141],
    'labels':[86, 193,86, 1037],
    'quantites':[518, 193,518, 1037],
    'prix':[652, 193,652, 1037],
}

def isfloat(s):
    try:
        float(s.replace(",", "."))
        return True
    except ValueError:
        return False

def parse_line(line):

    # Motif regex pour capturer les différentes parties
    pattern = r"^(.+?)\.\s*(\d+)\s*x\s*([\d.]+)\s*Euro$"

    # Recherche des correspondances dans la chaîne
    matches = re.match(pattern, line)

    # Si une correspondance est trouvée
    if matches:
        description = matches.group(1)
        quantite = matches.group(2)
        prix_unitaire = matches.group(3)
        
        return description, quantite, prix_unitaire
    else:
        return None

def premier_nombre_avant_espace(chaine):
    # Vérifie si la longueur de la chaîne est supérieure à 7
    if len(chaine) > 7:
        return 'walou'
    
    # Expression régulière pour extraire le premier nombre avant un espace
    regex = r'^(\d+)\s'
    match = re.match(regex, chaine)
    
    if match:
        return match.group(1)
    else:
        return 'walou'

def premier_nombre(chaine):
    nombres = re.findall(r'\d+', chaine)
    if nombres:
        return int(nombres[0])
    else:
        return None
def dernier_nombre(chaine):
    nombres = re.findall(r'\d+(?:\.\d+)?', chaine)
    if nombres:
        return float(nombres[-1])
    else:
        return None

    
def decodeFactures(json_data):
    invoice_data = {}
    invoice_data['labels'] = []
    invoice_data['quantites'] =[]
    invoice_data['prix'] =[]
    invoice_data['inconnu'] =[]
    for item in json_data:
        if 'bounding_box' in item:
            if inThePoint(position['id'], item["bounding_box"]):#---------------------INVOICE------------------------------------
                invoice_data['id'] = item["text"].upper().replace("INVOICE ", "")
            elif inThePoint(position['date'], item["bounding_box"]):#-----------------date------------------------------------
                invoice_data['date'] = item["text"].lower().replace("issue date ", "")
            elif inThePoint(position['client'], item["bounding_box"]):#-------------client------------------------------------
                invoice_data['client'] = item["text"].lower().replace("bill to ", "").title()
            elif inThePoint(position['adresse1'], item["bounding_box"]):#---------adresse1------------------------------------
                invoice_data['adresse1'] = item["text"].lower().replace("address ", "").title()
            elif inThePoint(position['adresse2'], item["bounding_box"]):#---------adresse2------------------------------------
                invoice_data['adresse2'] = item["text"]
            elif inTheSegment(position['labels'], item["bounding_box"]):#---------LABELS------------------------------------
                label = item["text"]
                resultat= parse_line(label)
                if resultat :
                    l, q, p= resultat
                    invoice_data['labels'].append(l)
                    invoice_data['quantites'].append(q)
                    invoice_data['prix'].append(p)    
                else:
                    invoice_data['labels'].append(label)
                
            elif inTheSegment(position['quantites'], item["bounding_box"]):#---------quantites-----------------------------

                quantite = item["text"].lower()
                
                #pour les cas ou il recupere les deux 
                if "euro" in quantite :
                    
                    # q=quantite.split("x")[0].strip()
                    q=premier_nombre(quantite)
                    if q : invoice_data['quantites'].append(q)
                    prix=dernier_nombre(quantite)
                    # prix=quantite.split("x")[-1].replace("euro", "").replace(" ", "").replace(':', '')
                    if prix: invoice_data['prix'].append(prix)
                elif not( "x" in quantite):
                    if " " in quantite:# dans le cas ou x est ocrise come 2 ou . avec un espace
                        quantite.replace(" ", "")
                        if len(quantite) > 5: continue
                        q=premier_nombre(quantite)
                        if q: invoice_data['quantites'].append(q)   
                    else:
                        q=premier_nombre(quantite)
                        if q:
                            if q % 10 == 2: q = q // 10 # dans le cas ou x est ocrise come 2
                            invoice_data['quantites'].append(q)        
                else:
                    
                    q=premier_nombre(quantite)
                    if q: invoice_data['quantites'].append(q)
            elif inTheSegment(position['prix'], item["bounding_box"]):#---------------Prix-----------------------------------
                prix=item["text"].lower().replace("euro", "").replace(" ", "")
                prix=dernier_nombre(prix)
                if prix: invoice_data['prix'].append(prix)
            else:#--------------------------------------------------------------------inconnu---------------------------------
                invoice_data['inconnu'].append(item["text"])
        else:
            invoice_data['QRid'] = item["INVOICE"]
            invoice_data['QRdate'] = item["DATE"]
            invoice_data['QRclientId'] = item["CUST"]
            invoice_data['QRclientCAT'] = item["CAT"]

    # traite la derniere ligne total
    invoice_data['Total_label'] = invoice_data['labels'][-1]
    invoice_data['labels'].pop() 
    invoice_data['TotalValue'] = invoice_data['prix'][-1]
    invoice_data['prix'].pop()
    
    # Calcul du total
    if 'quantites' in invoice_data and 'prix' in invoice_data:
        total = sum(int(q) * float(p) for q, p in zip(invoice_data['quantites'], invoice_data['prix']))
        invoice_data['total_Calculated'] = total
        invoice_data['delta'] = total - float(invoice_data['TotalValue'])
    print(json.dumps(invoice_data, indent=4))    
    return invoice_data    


if __name__ == "__main__":
    # Load JSON data from file
    json_data = load_json_file("json\FAC_2019_0275-165798.json")
    invoice = json.dumps(decodeFactures(json_data), indent=4)
    
    
    engine = connectBd()
    session = createsession(engine)
    add_invoice(json.loads(invoice), session)
    
    surveillanceAllInOne('fonction', 'resultat', 'erreur')
