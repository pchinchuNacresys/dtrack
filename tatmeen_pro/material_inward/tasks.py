import requests
import dramatiq
from django.conf import settings


@dramatiq.actor(max_retries=3, min_backoff=900)  # Retry up to 3 times, wait 10 mins between retries
def send_epcis_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen API error: {response.status_code}, response: {response.text}")




@dramatiq.actor(max_retries=3, min_backoff=900)  # Retry up to 3 times with 10 min delay
def send_shipper_cases_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen API error: {response.status_code}, response: {response.text}")



@dramatiq.actor(max_retries=3, min_backoff=900)
def send_sscc_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen SSCC API failed: {response.status_code}, response: {response.text}")



@dramatiq.actor(max_retries=3, min_backoff=600)
def send_receive_sscc_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen SCP receive failed: {response.status_code}, response: {response.text}")



@dramatiq.actor(max_retries=3, min_backoff=600)
def send_decommission_sscc_to_tatmeen(xml_body, access_token):
    import requests
    from django.conf import settings

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen SCP decommission failed: {response.status_code}, response: {response.text}")


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_shipping_sscc_to_tatmeen(xml_body, access_token):
    import requests
    from django.conf import settings

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Tatmeen shipping failed: {response.status_code}, response: {response.text}"
        )


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_packing_sscc_to_tatmeen(xml_body, access_token):
    import requests
    from django.conf import settings

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Tatmeen packing failed: {response.status_code}, response: {response.text}"
        )



@dramatiq.actor(max_retries=3, min_backoff=60)
def send_disaggregation_to_tatmeen(xml_body, access_token):
    import requests
    from django.conf import settings

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Disaggregation failed: {response.status_code}, response: {response.text}"
        )


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_disaggregationBE_to_tatmeen(xml_body, access_token):
    import requests
    from django.conf import settings

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Disaggregation failed: {response.status_code}, response: {response.text}"
        )



@dramatiq.actor(max_retries=3, min_backoff=60)
def send_disaggregationEA_to_tatmeen(xml_body, access_token):
    import requests
    from django.conf import settings

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Disaggregation failed: {response.status_code}, response: {response.text}"
        )



@dramatiq.actor(max_retries=3, min_backoff=60)
def send_aggregationEACHES_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        "https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS",
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen aggregation failed: {response.status_code}, response: {response.text}")


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_case_into_pallet_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        "https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS",
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Aggregation Case into Pallet failed. Status: {response.status_code}, Response: {response.text}")



@dramatiq.actor(max_retries=3, min_backoff=60)
def send_stolen_sscc_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Stolen SSCC failed. Status: {response.status_code}, Response: {response.text}")


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_exported_sscc_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Exported SSCC failed. Status: {response.status_code}, Response: {response.text}"
        )


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_lost_sscc_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Lost SSCC failed. Status: {response.status_code}, Response: {response.text}"
        )



@dramatiq.actor(max_retries=3, min_backoff=60)
def send_sample_sscc_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Sample SSCC failed. Status: {response.status_code}, Response: {response.text}"
        )



@dramatiq.actor(max_retries=3, min_backoff=60)
def send_return_receiving_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Return Receiving failed. Status: {response.status_code}, Response: {response.text}"
        )


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_dispensed_sscc_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/Dispensation',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"Dispense failed. Status: {response.status_code}, Response: {response.text}"
        )



@dramatiq.actor(max_retries=3, min_backoff=60)
def send_dispensed_sgtin_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/Dispensation',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(
            f"SGTIN Dispensation failed. Status: {response.status_code}, Response: {response.text}"
        )



@dramatiq.actor(max_retries=3, min_backoff=60)
def send_return_shipping_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen return shipping failed. Status: {response.status_code}, Response: {response.text}")


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_returnshippingcancellation_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen return shipping cancellation failed. Status: {response.status_code}, Response: {response.text}")


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_returnreceiving_cancellation_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen receiving cancellation failed. Status: {response.status_code}, Response: {response.text}")


@dramatiq.actor(max_retries=3, min_backoff=60)
def send_shippingcancellation_to_tatmeen(xml_body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
        data=xml_body,
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Tatmeen cancellation failed. Status: {response.status_code}, Response: {response.text}")



# @dramatiq.actor(max_retries=3, min_backoff=900)  # Retry up to 3 times, wait 10 mins between retries
# def shipper_cases_api(xml_body, access_token):
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "apikey": settings.TATMEEN_API_KEY,
#         "Content-Type": "application/soap+xml; charset=utf-8"
#     }

#     response = requests.post(
#         'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
#         data=xml_body,
#         headers=headers
#     )               
#     if response.status_code != 200:
#         raise Exception(f"Tatmeen API error: {response.status_code}, response: {response.text}")    





