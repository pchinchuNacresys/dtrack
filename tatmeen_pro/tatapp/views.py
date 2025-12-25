# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from services.tatmeen_auth import get_tatmeen_token, load_token_data
# from django.conf import settings
# import requests

# def call_tatmeen_api(endpoint, xml_body):
#     access_token = get_tatmeen_token()
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "apikey": settings.TATMEEN_API_KEY,
#         "Content-Type": "application/xml"
#     }
#     response = requests.post(endpoint, headers=headers, data=xml_body)
#     return response

# @csrf_exempt
# def send_epcis_view(request):
#     if request.method == "POST":
#         response = call_tatmeen_api(
#             "https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS",
#             request.body
#         )
#         return JsonResponse({"status": response.status_code, "response": response.text})
#     return JsonResponse({"error": "POST only"}, status=405)

# @csrf_exempt
# def dispensation_view(request):
#     if request.method == "POST":
#         response = call_tatmeen_api(
#             "https://tatmeenapim.mohap.gov.ae/v1/Dispensation",
#             request.body
#         )
#         return JsonResponse({"status": response.status_code, "response": response.text})
#     return JsonResponse({"error": "POST only"}, status=405)

# @csrf_exempt
# def verify_product_view(request):
#     if request.method == "POST":
#         response = call_tatmeen_api(
#             "https://tatmeenapim.mohap.gov.ae/v1/VerifyProduct",
#             request.body
#         )
#         return JsonResponse({"status": response.status_code, "response": response.text})
#     return JsonResponse({"error": "POST only"}, status=405)

# @csrf_exempt
# def msg_status_query_view(request):
#     if request.method == "POST":
#         response = call_tatmeen_api(
#             "https://tatmeenapim.mohap.gov.ae/v1/MsgStatusQuery",
#             request.body
#         )
#         return JsonResponse({"status": response.status_code, "response": response.text})
#     return JsonResponse({"error": "POST only"}, status=405)

# def token_info_view(request):
#     token_data = load_token_data()
#     print(token_data)
#     if not token_data:
#         return JsonResponse({"error": "Token not found"}, status=404)
#     return JsonResponse(token_data)

##############################################  new steps ###############################################
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from django.utils.timezone import now
import pytz

import requests
from django.http import JsonResponse
from django.conf import settings

def get_tatmeen_token(request):
    url = "https://tatmeenapim.mohap.gov.ae/v1/auth"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": settings.TATMEEN_API_KEY
    }

    data = {
        "username": settings.TATMEEN_USERNAME,
        "password": settings.TATMEEN_PASSWORD,
        "grant_type": settings.TATMEEN_GRANT_TYPE
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({
                "error": "Failed to get token",
                "status_code": response.status_code,
                "response": response.text
            }, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#####################################################################################################

from django.http import JsonResponse
from services.tatmeen_auth import get_valid_token

def token_info_view(request):
    try:
        token_data = get_valid_token()
        return JsonResponse(token_data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#Use It in the Views / API Requests
# from .tatmeen_auth import get_valid_token

# token_data = get_valid_token()
# access_token = token_data["access_token"]


def call_send_epcis(request):
    token_data = get_valid_token()
    access_token = token_data["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8",
    }

    body = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
            <soap:Header/>
            <soap:Body>
                <epcis:EPCISDocument schemaVersion="1.2" creationDate="2021-12-12T07:21:26Z" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                    <EPCISHeader>
                        <sbdh:StandardBusinessDocumentHeader>
                            <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                            <sbdh:Sender>
                                <sbdh:Identifier Authority="GS1">6297001118115</sbdh:Identifier>
                            </sbdh:Sender>
                            <sbdh:Receiver>
                                <sbdh:Identifier Authority="GS1">6297001273036</sbdh:Identifier>
                            </sbdh:Receiver>
                            <sbdh:DocumentIdentification>
                                <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                <!--Mandatory. Instance Identifier upto 50 char (min 32) alphanumeric UUID, example: 2f1bdabdfaee464c87e1aeb7e586e6ab-->
                                <sbdh:InstanceIdentifier>e999f82e7828a9633d977c64016a8f81</sbdh:InstanceIdentifier>
                                <sbdh:Type>Events</sbdh:Type>
                                <sbdh:CreationDateAndTime>2021-12-12T12:02:05.000Z</sbdh:CreationDateAndTime>
                            </sbdh:DocumentIdentification>
                        </sbdh:StandardBusinessDocumentHeader>
                    </EPCISHeader>
                    <EPCISBody>
                        <EventList>
                            <ObjectEvent>
                                <eventTime>2022-03-28T18:59:11.000Z</eventTime>
                                <eventTimeZoneOffset>+05:30</eventTimeZoneOffset>
                                <epcList>
                                    <epc>urn:epc:id:sscc:xxxxxxxx.123456789</epc>
                                </epcList>
                                <action>OBSERVE</action>
                                <bizStep>urn:epcglobal:cbv:bizstep:receiving</bizStep>
                                <disposition>urn:epcglobal:cbv:disp:returned</disposition>
                                <readPoint>
                                    <id>urn:epc:id:sgln:xxxxxxxx.2244.0</id>
                                </readPoint>
                                <bizLocation>
                                    <id>urn:epc:id:sgln:xxxxxxxx.2244.0</id>
                                </bizLocation>
                                <bizTransactionList>
                                    <bizTransaction type="urn:epcglobal:cbv:btt:desadv">urn:epcglobal:cbv:bt:xxxxxxxx00000:TSTOBD001</bizTransaction>
                                </bizTransactionList>
                            </ObjectEvent>
                        </EventList>
                    </EPCISBody>
                </epcis:EPCISDocument>
            </soap:Body>
        </soap:Envelope>"""

#6297001273036
    response = requests.post(
        "https://apim.tatmeen.ae/v1/epcisMsgAsync",
        headers=headers,
        data=body
    )

    return JsonResponse({"message": "EPCIS called successfully","status_code": response.status_code,"response_text": response.text})
    # return response.text, response.status_code


def verify_product(request):
    token_data = get_valid_token()
    access_token = token_data["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8",
    }

    body = """<?xml version="1.0" encoding="utf-8"?>
        <env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
            <env:Header/>
            <env:Body>
                <ProductVerificationRequest>
                    <GeoLatitude></GeoLatitude>
                    <GeoLongitude></GeoLongitude>
                    <Language>E</Language>
                    <ProductID>urn:epc:id:sscc:6297001118.0000040</ProductID>
                </ProductVerificationRequest>
            </env:Body>
        </env:Envelope>"""

    response = requests.post(
        "https://tatmeenapim.mohap.gov.ae/v1/VerifyProduct",
        headers=headers,
        data=body
    )

    return JsonResponse({
        "status_code": response.status_code,
        "response_text": response.text
    })
    
    
    
def msg_status_query(request):
    token_data = get_valid_token()
    access_token = token_data["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8",
    }

    body = """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
            <soap:Header/>
            <soap:Body>
                <tatmeenMsgStatusQuery xsi:noNamespaceSchemaLocation="schema.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <language>E</language>
                    <instanceIdentifier>e999f82e7828a9633d977c64016a8f81</instanceIdentifier>
                </tatmeenMsgStatusQuery>
            </soap:Body>
        </soap:Envelope>"""

    response = requests.post(
        "https://apim.tatmeen.ae/v1/MsgStatusQuery",
        headers=headers,
        data=body
    )

    return JsonResponse({
        "status_code": response.status_code,
        "response_text": response.text
    })
    
# <instanceIdentifier>af1145e8118d4edfb4c6ad50137e8ea6</instanceIdentifier> bindu nair


################# Event Time Test View #######################

class EventTimeTestView(APIView):
    def post(self, request):
        try:
            # Get input time from request (assume format: "2025-05-02T14:30")
            input_str = request.data.get("event_time")
            if not input_str:
                return Response({"error": "event_time is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Define timezones
            ist_tz = pytz.timezone("Asia/Kolkata")
            uae_tz = pytz.timezone("Asia/Dubai")

            # Parse and localize to IST
            input_dt = datetime.strptime(input_str, "%Y-%m-%dT%H:%M")
            event_time_ist = ist_tz.localize(input_dt)

            # Convert to UAE timezone
            event_time_uae = event_time_ist.astimezone(uae_tz)

            # Get current UAE time
            current_uae_time = now().astimezone(uae_tz)

            # Ensure event_time is not in the future
            final_event_time = min(event_time_uae, current_uae_time)

            # Format to ISO 8601
            formatted_time = final_event_time.strftime("%Y-%m-%dT%H:%M:%S")

            return Response({
                "original_input": input_str,
                "current_uae_time": current_uae_time,
                "converted_uae_time": formatted_time,
                "note": "Final event_time will not exceed current UAE time."
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


########################    barcode generation    #####################

import io
import random
import treepoem
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from admin_management.models import SSCCBarcode  # Update with your actual app path

def calculate_check_digit(number: str) -> str:
    total = 0
    reverse_digits = number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        total += n * 3 if i % 2 == 0 else n
    return str((10 - (total % 10)) % 10)

class GenerateSSCCBarcode(APIView):
    def post(self, request):
        extension_digit = request.data.get("extension_digit")
        company_prefix = request.data.get("company_prefix")

        if not (extension_digit and extension_digit.isdigit() and len(extension_digit) == 1):
            return Response({"error": "Invalid extension digit"}, status=status.HTTP_400_BAD_REQUEST)
        if not (company_prefix and company_prefix.isdigit()):
            return Response({"error": "Invalid company prefix"}, status=status.HTTP_400_BAD_REQUEST)

        max_base_length = 17
        fixed_part_length = len(extension_digit) + len(company_prefix)
        serial_length = max_base_length - fixed_part_length

        if serial_length <= 0:
            return Response({"error": "Company prefix too long"}, status=status.HTTP_400_BAD_REQUEST)

        serial_reference = ''.join(random.choices('0123456789', k=serial_length))
        base_sscc = extension_digit + company_prefix + serial_reference
        check_digit = calculate_check_digit(base_sscc)
        full_sscc = base_sscc + check_digit

        # Proper GS1-128 format with (00) Application Identifier
        gs1_data = f"[00]{full_sscc}"  # treepoem uses [] to represent AI

        # Generate barcode using GS1-128
        barcode_image = treepoem.generate_barcode(
            barcode_type="gs1-128",
            data=gs1_data
        )

        buffer = io.BytesIO()
        barcode_image.convert("1").save(buffer, format="PNG")
        buffer.seek(0)

        filename = f"sscc_{full_sscc}.png"
        content_file = ContentFile(buffer.read(), name=filename)

        barcode_record, created = SSCCBarcode.objects.get_or_create(
            full_sscc=full_sscc,
            defaults={
                'extension_digit': extension_digit,
                'company_prefix': company_prefix,
                'serial_reference': serial_reference,
                'check_digit': check_digit,
                'barcode_image': content_file,
            }
        )

        if not created and not barcode_record.barcode_image:
            barcode_record.barcode_image.save(filename, content_file, save=True)

        image_url = barcode_record.barcode_image.url

        return Response({
            "sscc": full_sscc,
            "image_url": image_url
        }, status=status.HTTP_201_CREATED)


########## OCR Reading ############


from .utils.pdf_reader import extract_invoice_data

# class InvoiceUploadAPIView(APIView):
#     def post(self, request):
#         uploaded_file = request.FILES.get('file')

#         if not uploaded_file:
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#         if not uploaded_file.name.lower().endswith(".pdf"):
#             return Response({"error": "File must be a PDF"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             data = extract_invoice_data(uploaded_file)
#             return Response(data, status=status.HTTP_200_OK)
#         except ValueError as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvoiceUploadAPIView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        if not uploaded_file.name.lower().endswith(".pdf"):
            return Response({"error": "File must be a PDF"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = extract_invoice_data(uploaded_file)
            return Response({
                "uploaded_image_url": f"/media/uploads/{uploaded_file.name}",
                "extracted_data": data
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# for django

import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
# from utils.pdf_reader import extract_invoice_data

@csrf_exempt  # You might keep this for testing, but better to handle CSRF properly later
def upload_invoice(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    uploaded_file = request.FILES.get('file')

    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    if not uploaded_file.name.lower().endswith(".pdf"):
        return JsonResponse({"error": "File must be a PDF"}, status=400)

    # Save file to media/uploads
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)

    with open(file_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    try:
        data = extract_invoice_data(file_path)
        return JsonResponse({
            "uploaded_file_url": f"/media/uploads/{uploaded_file.name}",
            "extracted_data": data
        }, status=200)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=500)




############################################################################


from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from .utils.pdf_reader import extracting_invoice_data

class InvoiceUploadingAPIView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        if not uploaded_file.name.lower().endswith(".pdf"):
            return Response({"error": "File must be a PDF"}, status=status.HTTP_400_BAD_REQUEST)

        # Save file to media folder
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read()))
        full_file_path = os.path.join(default_storage.location, file_path)

        try:
            extracted_data = extracting_invoice_data(full_file_path)
            return Response({
                "uploaded_file_url": default_storage.url(file_path),
                "extracted_data": extracted_data
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)