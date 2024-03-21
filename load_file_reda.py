import requests

url = "https://invoiceocrp3.azurewebsites.net/invoices"

headers = {
    "accept": "application/json"
}


response = requests.get(url, headers=headers)
data = response.json()
data = data.get('invoices')
lastDate = data[-1]['dt']
flag = False
count = 0
while flag == False : 
    urldata  = f"https://invoiceocrp3.azurewebsites.net/invoices?start_date={lastDate}"
    responseData = requests.get(urldata, headers=headers)
    if responseData.status_code == 200:
            adddata = responseData.json()
            if len(adddata) == 0:
                adddata = adddata.get('invoices')
                data.extend(adddata)
                lastDate = data[-1]['dt']
                print(lastDate,data[-1])
            else:
                flag = True
    else :
        print(f"Erreur: {response.status_code} - {response.reason}") 
        flag = True
