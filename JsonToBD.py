import json
import os
from ORM import add_invoice, connectBd, createsession
from decodage import decodeFactures, load_json_file
from surveillance import surveillanceAllInOne



def exportJson(filename='json\FAC_2019_0002-521208.json'):
    # Connect to the database
    engine = connectBd()
    session = createsession(engine)

    if  filename.startswith("FAC_") and filename.endswith(".json"):
        # Load JSON data from file
        print(f'---------------------------------------------------------------------------')
        print(f'---------------Export du fichier : {filename}------------------------------')
        print(f'---------------------------------------------------------------------------')
        json_data = load_json_file(os.path.join(json_dir, filename))
        invoice = json.dumps(decodeFactures(json_data), indent=4)
        print(invoice)

        # Add the invoice to the database
        add_invoice(json.loads(invoice), session)

    # Close the session after processing all invoices
    session.close()

def exportAll(json_dir = "json"):
    # Connect to the database
    engine = connectBd()
    session = createsession(engine)
    
    # Iterate over each file in the directory
    for filename in os.listdir(json_dir):
        if  filename.startswith("FAC_") and filename.endswith(".json"):
            # Load JSON data from file
            print(f'---------------------------------------------------------------------------')
            print(f'---------------Export du fichier : {filename}------------------------------')
            print(f'---------------------------------------------------------------------------')
            json_data = load_json_file(os.path.join(json_dir, filename))
            invoice = json.dumps(decodeFactures(json_data), indent=4)
            print(invoice)

            # Add the invoice to the database
            add_invoice(json.loads(invoice), session)

    # Close the session after processing all invoices
    session.close()

if __name__ == "__main__":
    # exportJson()
    exportAll()
