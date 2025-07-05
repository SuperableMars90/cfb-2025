import json
import requests
APIKEY = json.load(open("../.secret"))['cfbd_apikey']
def request_json(url,APIKEY=APIKEY):
    r = requests.get(url,headers={'accept': 'application/json',
          'Authorization': f'Bearer {APIKEY}'})
    print(r)
    if (r.status_code>=200) and (r.status_code<300):
        data = json.loads(r.content.decode())
        return data
