from __future__ import absolute_import, unicode_literals
from celery import shared_task
import requests
from django.conf import settings


@shared_task
def background_task():
   
    api_url = settings.FIXER_API_URL
    api_key = settings.FIXER_API_KEY
        
    params = {
        "access_key": api_key,
        "symbols": "EUR, USD, PLN, GBP"
        #base -> EUR
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status() 

        data = response.json()

        if "rates" in data:
            return data["rates"]
        else:
            #default setting in case of not working API
            return {"USD": 0.86, "PLN": 4.47, "EUR": 1, "GBP": 1.12}  

    except requests.exceptions.RequestException as e:
        #default setting in case of not working API
        return {"USD": 0.86, "PLN": 4.47, "EUR": 1, "GBP": 1.12} 
    

