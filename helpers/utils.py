import random
import requests
from django.core.cache import cache
import urllib.parse
import pytz
from datetime import datetime
from django.conf import settings


# AUTH_SERVICE_MOBILE_URL =  settings.AUTH_SERVER_URL + "/member-details/",

def get_member_details_by_mobile(mobile_number):
    try:
        response = requests.get(settings.AUTH_SERVER_URL + "/member-details/", params={"mobile_number": mobile_number})
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"Error contacting auth service: {e}")
        return None
    
    


# AUTH_SERVICE_CARD_URL = settings.AUTH_SERVER_URL + "/cardno/member-details/",  

def get_member_details_by_card(card_number):
    try:
        response = requests.get(settings.AUTH_SERVER_URL + "/cardno/member-details/", params={"card_number": card_number})
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"Error contacting auth service: {e}")
        return None
    
    
    
    
    
# AUTH_SERVICE_BUSINESS_URL = settings.AUTH_SERVER_URL + "/business/details/",

def get_business_details_by_id(business_id):
    try:
        response = requests.get(settings.AUTH_SERVER_URL + "/business/details/", params={"business_id": business_id})
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"Error contacting auth service: {e}")
        return None


