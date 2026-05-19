import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TermiiService:
    """
    Service for interacting with Termii API to send SMS and OTPs.
    Documentation: https://developer.termii.com/

    url = "https://BASE_URL/api/sms/send"
    payload = {
            "to": "2347880234567",
            "from": "talert",
            "sms": "Hi there, testing Termii ",
            "type": "plain",
            "channel": "generic",
            "api_key": "Your API Key",
        }
    headers = {
    'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.text)
    """
    
    BASE_URL = getattr(settings, 'TERMI_BASE_URL', 'https://api.ng.termii.com/api')
    API_KEY = getattr(settings, 'TERMI_API_KEY', None)
    SENDER_ID = getattr(settings, 'TERMI_SENDER_ID', 'Sendit')

    @classmethod
    def send_sms(cls, to: str, message: str, channel="generic", sender_id: str = None):
        """
        Send a standard SMS. 
        message channel either generic or dnd
        """
        if not cls.API_KEY:
            logger.error("TERMI_API_KEY is not set in settings.")
            return None

        url = f"{cls.BASE_URL}/api/sms/send"
        # url = "https://api.termii.com/api/sms/send"
        payload = {
            "to": to,
            "from": sender_id or cls.SENDER_ID,
            "sms": message,
            "type": "plain",
            "channel":channel,
            "api_key": cls.API_KEY
        }
        headers = {
            'Content-Type': 'application/json',
        }
        try:
            print("payload", payload)
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending Termii SMS: {str(e)}")
            return None

    @classmethod
    def send_generic(cls, to: str, message: str, sender_id: str = None):
        """
        Send an OTP using Termii's SMS endpoint.
        Note: Termii also has a dedicated /sms/otp/send endpoint, 
        but many developers prefer using the standard SMS endpoint with their own generated OTP.
        """
        return cls.send_sms(to, message,channel="generic", sender_id=sender_id)

    @classmethod
    def send_dnd(cls, to: str, message: str):
        """
        Send high priority notification using the 'dnd' or 'whatsapp' channel if needed.
        For now, we use the standard generic channel as requested for reusability.
        """
        return cls.send_sms(to, message, channel="dnd")
