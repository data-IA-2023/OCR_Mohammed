import json

from ORM import add_invoice, createsession


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

def decodeFactures(json_data):
    invoice_data = {}

    for item in json_data:
        if 'bounding_box' in item:
            if inThePoint(position['id'], item["bounding_box"]):
                invoice_data['id'] = item["text"].replace("INVOICE ", "")
            elif inThePoint(position['date'], item["bounding_box"]):
                invoice_data['date'] = item["text"].replace("issue date ", "")
            elif inThePoint(position['client'], item["bounding_box"]):
                invoice_data['client'] = item["text"].replace("Bill to ", "")
            elif inThePoint(position['adresse1'], item["bounding_box"]):
                invoice_data['adresse1'] = item["text"]
            elif inThePoint(position['adresse2'], item["bounding_box"]):
                invoice_data['adresse2'] = item["text"]
            elif inTheSegment(position['labels'], item["bounding_box"]):
                if 'labels' not in invoice_data:
                    invoice_data['labels'] = []
                invoice_data['labels'].append(item["text"])
            elif inTheSegment(position['quantites'], item["bounding_box"]):
                if 'quantites' not in invoice_data:
                    invoice_data['quantites'] = []
                
                quantite = item["text"].lower()
                #pour les cas ou il recupere les deux 
                if "euro" in quantite :
                    
                    invoice_data['quantites'].append(quantite.split("x")[0].strip())
                    if 'prix' not in invoice_data:
                        invoice_data['prix'] = []
                    prix=quantite.split("x")[-1].replace(" euro", "").replace(" ", "")
                    invoice_data['prix'].append(prix)
                    
                else:    
                    invoice_data['quantites'].append(item["text"].replace(" x", "").replace(" ", ""))
            elif inTheSegment(position['prix'], item["bounding_box"]):
                if 'prix' not in invoice_data:
                    invoice_data['prix'] = []
                invoice_data['prix'].append(item["text"].replace(" Euro", "").replace(" ", ""))
            else:
                if 'inconnu' not in invoice_data:
                    invoice_data['inconnu'] = []
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
        
    return invoice_data    


if __name__ == "__main__":
    # Load JSON data from file
    json_data = load_json_file("json\FAC_2019_0007-2747871.json")
    invoice = json.dumps(decodeFactures(json_data), indent=4)
    print(invoice)
    
    
    add_invoice(json.loads(invoice), createsession())
