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

    if (x1 <= x_max and x2 >= x_min and
        y1 <= y_max and y2 >= y_min):
        return True

    return False

position = { 
    'id': [143, 30],
    'date': [159, 59],
    'client': [86, 89],
    'adresse1': [79, 125],
    'adresse2': [79, 141],
    'labels':[48, 193,48, 1037],
    'quantites':[517, 193,517, 1037],
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
    if len(chaine) > 7: return 'walou'
    
    regex = r'^(\d+)\s+\d+'
    match = re.match(regex, chaine)
    if match:
        return match.group(1)
    else:
        return 'walou'


    
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
                    
                    q=quantite.split("x")[0].strip()
                    if q.isdigit(): invoice_data['quantites'].append(q)
                    
                    prix=quantite.split("x")[-1].replace(" euro", "").replace(" ", "").replace(':', '')
                    if isfloat(prix): invoice_data['prix'].append(prix)
                elif not( "x" in quantite):
                    q=premier_nombre_avant_espace(quantite)
                    if q.isdigit(): invoice_data['quantites'].append(q)
                else:
                    q=item["text"].replace(" x", "").replace(" ", "")
                    if q.isdigit(): invoice_data['quantites'].append(q)
            elif inTheSegment(position['prix'], item["bounding_box"]):#---------------Prix-----------------------------------

                prix=item["text"].replace(" Euro", "").replace(" ", "").replace(':', '')
                if isfloat(prix): invoice_data['prix'].append(prix)
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
    
    print(json.dumps(invoice_data, indent=4))    
    return invoice_data    


if __name__ == "__main__":
    # Load JSON data from file
    json_data = load_json_file("json\FAC_2023_0166-1870080.json")
    invoice = json.dumps(decodeFactures(json_data), indent=4)
    
    
    engine = connectBd()
    session = createsession(engine)
    add_invoice(json.loads(invoice), session)
    
    surveillanceAllInOne('fonction', 'resultat', 'erreur')
