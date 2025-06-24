import requests
response = requests.get('https://aistudio.google.com')
print(response.status_code)