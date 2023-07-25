import requests

url = 'http://172.30.1.20:8000/size/'
params = {
    'height': 180,
    'weight': 70,
    'imageUrl': 'https://www.musinsa.com/app/goods/983339',
    'loosefit_condition': '오버핏'
}

response = requests.get(url, params=params)
data = response.json()

print(data)
