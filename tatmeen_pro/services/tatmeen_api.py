import requests
from django.conf import settings
from services.tatmeen_auth import get_tatmeen_token

TATMEEN_ENDPOINTS = {
    "send_epcis": "https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS",
    "dispensation": "https://tatmeenapim.mohap.gov.ae/v1/Dispensation",
    "verify_product": "https://tatmeenapim.mohap.gov.ae/v1/VerifyProduct",
    "msg_status": "https://tatmeenapim.mohap.gov.ae/v1/MsgStatusQuery"
}

def call_tatmeen_endpoint(endpoint_key: str, xml_body: str) -> dict:
    if endpoint_key not in TATMEEN_ENDPOINTS:
        raise ValueError("Invalid endpoint key")

    url = TATMEEN_ENDPOINTS[endpoint_key]
    token = get_tatmeen_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/xml"
    }

    response = requests.post(url, headers=headers, data=xml_body)

    if response.status_code == 200:
        return {
            "status": "success",
            "data": response.text
        }
    else:
        return {
            "status": "error",
            "code": response.status_code,
            "message": response.text
        }
