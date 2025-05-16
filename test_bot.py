import requests
from bs4 import BeautifulSoup

# First, get the CSRF token
session = requests.Session()
response = session.get('https://tetralto.com/contact/')
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

# Form data
form_data = {
    'csrfmiddlewaretoken': csrf_token,
    'name': 'Test Bot',
    'phone': '1234567890',
    'email': 'bot@test.com',
    'address': '123 Bot Street',
    'description': 'This is a test submission from a bot',
    'g_recaptcha_response': ''  # Empty token to simulate bot
}

# Submit the form
response = session.post('https://tetralto.com/contact/', data=form_data)

# Print the response
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text[:500]}")  # Print first 500 chars of response 