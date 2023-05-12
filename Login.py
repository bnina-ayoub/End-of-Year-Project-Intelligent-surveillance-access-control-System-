import requests
from bs4 import BeautifulSoup

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Set login credentials
payload = {
    'user': 'your_username_here',
    'mdp': 'your_password_here',
    ''
}

# Set headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

# Set URL
url = 'https://www.attt.com.tn/autoecole.php?code_menu=74&code_p=4'

# Create session
session = requests.session()

# Send login request
response = session.post(url, data=payload, headers=headers, verify=False)

# Check login status
if 'Compte bloqué ou inexistant' in response.text:
    print('Login Failed!')
else:
    print('Login Not sure.')
