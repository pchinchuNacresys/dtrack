#from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from material_inward.models import *
from admin_management.models import *
from tatmeen_pro.utils import generate_random_string_with_uuid_seed  # import your generator
from django.db import connection
import json
import uuid
from django.utils.timezone import now
from django.utils.timezone import localtime
import pytz
import requests
from datetime import datetime
import random
from services.tatmeen_auth import get_valid_token
from django.conf import settings
from tatmeen_pro.utils import get_next_serials
from django.db import transaction
import re
import xml.etree.ElementTree as ET
from django.utils import timezone
from material_inward.tasks import *



# UUID generator function
# class GenerateIdentifierView(APIView):
#     def post(self, request):
#         max_attempts = 10
#         for _ in range(max_attempts):
#             code = generate_random_string_with_uuid_seed()
#             if not UniqueIdentifier.objects.filter(code=code).exists():
#                 UniqueIdentifier.objects.create(code=code)
#                 return Response({"identifier": code}, status=status.HTTP_201_CREATED)

#         return Response(
#             {"error": "Could not generate a unique identifier. Please try again."},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


class GenerateIdentifierView(APIView):
    def post(self, request):
        max_attempts = 10
        for _ in range(max_attempts):
            code = generate_random_string_with_uuid_seed()
            if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                UniqueIdentifier.objects.using('default').create(code=code)
                return Response({"identifier": code}, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "Could not generate a unique identifier. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


#add vendor details
class AddVendorAPIView(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            ven_name = data['name']
            gln = data['gln']
            company_prefix = data['company_prefix']
            # sgln = data['sgln']
            shipmentpermit=data['shipmentpermit']
            ven_address = data['address']
            ven_city = data['city']
            ven_province = data['province']
            ven_country = data['country']
            contactno = data['contactno']
            vemail = data['vemail']

            # SGLN extraction from GLN using CompanyPrefix
            # if not gln.startswith(company_prefix):
            #     return Response({'error': 'GLN does not match the Company Prefix'}, status=status.HTTP_400_BAD_REQUEST)

            location_part = gln[len(company_prefix):-1]  # Remove last digit
            sgln = f"{company_prefix}.{location_part}"
            
            # ORM check if vendor already exists
            if vendor_master.objects.filter(vendor_name=ven_name, CompanyPrefix=company_prefix).exists():
                return Response({'error': 'Supplier already exists'}, status=status.HTTP_400_BAD_REQUEST)

            a = connection.cursor()
            a.execute("EXEC add_vendor'" + str(ven_name) + "','" + str(
                gln) + "','" + str(company_prefix) + "','" + str(sgln) + "','" + str(shipmentpermit) + "','" + str(ven_address) + "','" + str(ven_city) + "','" + str(
                ven_province) + "','" + str(ven_country) + "','" + str(contactno) + "','" + str(vemail) + "'")
            
            return Response({'data': 'Supplier data added successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        return Response({"error": "Invalid method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    
# venfor master details
class VendorListAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC get_vendor_details")
            columns = [col[0] for col in cursor.description]
            vendor_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'vendor_data': vendor_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteVendorListAPIView(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            ven_id = data['ven_id']
            
            # ORM check if vendor exists
            if not vendor_master.objects.filter(id=ven_id,status=1).exists():
                return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

            # Delete the vendor
            cursor = connection.cursor()
            cursor.execute("EXEC delete_vendor'" + str(ven_id) + "'")
            return Response({'message': 'Supplier removed successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateVendorListAPIView(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            ven_id=data['ven_id']
            ven_name = data['name']
            gln = data['gln']
            company_prefix = data['company_prefix']
            shipmentpermit=data['shipmentpermit']
            ven_address = data['address']
            ven_city = data['city']
            ven_province = data['province']
            ven_country = data['country']
            contactno = data['contactno']
            vemail = data['vemail']

            # ORM check if vendor exists
            if not vendor_master.objects.filter(GLN=gln,status=1).exists():
                return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

            location_part = gln[len(company_prefix):-1]  # Remove last digit
            sgln = f"{company_prefix}.{location_part}"

            cursor = connection.cursor()
            cursor.execute("EXEC update_vendor'" + str(ven_id) + "','" + str(ven_name) + "','" + str(
                gln) + "','" + str(company_prefix) + "','" + str(sgln) + "','" + str(shipmentpermit) + "','" + str(ven_address) + "','" + str(ven_city) + "','" + str(
                ven_province) + "','" + str(ven_country) + "','" + str(contactno) + "','" + str(vemail) + "'")
            
            return Response({'data': 'Supplier updated successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#manufacturer list
class ManufacturerListAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC manufacturer_list")
            columns = [col[0] for col in cursor.description]        
            manufacturer_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'manufacturer_data': manufacturer_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#supplier list
class SupplierListAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC supplier_list")
            columns = [col[0] for col in cursor.description]
            supplier_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'supplier_data': supplier_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#add product master data
class AddProductAPIView(APIView):
    def post(self, request):
        try:
            # data = json.loads(request.body.decode('utf-8'))
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            
            pr_name = data['name']
            gtin=data['gtin']
            dosage = data['dosage']
            manufacturer = data['manufacturer']
            country_origin = data['country_origin']
            product_form = data['product_form']
            uom = data['uom']
            # gln=data['gln']

            # Get company_prefix from vendor_master using manufacturer
            try:
                vendor = vendor_master.objects.get(GLN=manufacturer)
                company_prefix = vendor.CompanyPrefix
                print("---- company prefix -------",company_prefix)
            except vendor_master.DoesNotExist:
                return Response({'error': 'Manufacturer not found in vendor master'}, status=400)
            
            
            # Basic GTIN validation
            # if len(gtin) < 3 or not gtin.startswith('0'):
            #     return Response({'error': 'GTIN must start with 0 and be at least 3 digits long'}, status=400)

            # Remove indicator digit and check digit from GTIN
            gtin_core = gtin[1:-1]
            print("----gtin core ---------",gtin_core)

            if not gtin_core.startswith(company_prefix):
                return Response({'error': 'GTIN does not match the Company Prefix'}, status=400)

            # Extract item reference
            item_ref = gtin_core[len(company_prefix):]
            item_ref = item_ref.zfill(13 - len(company_prefix))  # GTIN is 13 digits excluding indicator and check

            # Generate serial number (12-digit chunk from UUID)
            # serial_number = str(uuid.uuid4().int)[:12]   .{serial_number}

            # Construct full SGTIN
            sgtin = f"{company_prefix}.{item_ref}"
            
            
            if ProductMaster.objects.filter(product_name=pr_name,dosage=dosage,manufacturer=manufacturer).exists():
                return Response({'error':"Data already exists"})
            
            cursor = connection.cursor()
            cursor.execute("EXEC prod_add'" + str(pr_name) + "','" + str(gtin) + "','" + str(sgtin) + "','" + str(dosage) + "','" + str(manufacturer) + "','" + str(country_origin) + "','" + str(product_form) + "','" + str(uom) + "'")
            return Response({'data': 'Product added successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        return Response({"error": "Invalid method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    
#fetch product master details   
class ProductListAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC get_product_details")
            columns = [col[0] for col in cursor.description]
            product_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'product_data': product_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateProductDataAPIView(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            product_id = data['product_id']
            pr_name = data['name']
            gtin = data['gtin']
            dosage = data['dosage']
            manufacturer = data['manufacturer']
            country_origin = data['country_origin']
            product_form = data['product_form']
            uom = data['uom']
            

            # Get company_prefix from vendor_master using manufacturer
            try:
                vendor = vendor_master.objects.get(GLN=manufacturer)
                company_prefix = vendor.CompanyPrefix
            except vendor_master.DoesNotExist:
                return Response({'error': 'Manufacturer not found in supplier master'}, status=400)

            # Basic GTIN validation
            if len(gtin) < 3 or not gtin.startswith('0'):
                return Response({'error': 'GTIN must start with 0 and be at least 3 digits long'}, status=400)

            # Remove indicator digit and check digit from GTIN
            gtin_core = gtin[1:-1]

            if not gtin_core.startswith(company_prefix):
                return Response({'error': 'GTIN does not match the Company Prefix'}, status=400)

            # Extract item reference
            item_ref = gtin_core[len(company_prefix):]
            item_ref = item_ref.zfill(13 - len(company_prefix))  # GTIN is 13 digits excluding indicator and check

            # Construct full SGTIN
            sgtin = f"{company_prefix}.{item_ref}"

            cursor = connection.cursor()
            cursor.execute("EXEC update_product_data'" + str(product_id) + "','" + str(pr_name) + "','" + str(gtin) + "','" + str(sgtin) + "','" + str(dosage) + "','" + str(manufacturer) + "','" + str(country_origin) + "','" + str(product_form) + "','" + str(uom) + "'")
            
            return Response({'data': 'Product updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DeleteProductDataAPIView(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            product_id = data['product_id']

            # Check if product exists
            if not ProductMaster.objects.filter(product_id=product_id,status=1).exists():
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            # Call stored procedure to delete product
            cursor = connection.cursor()
            cursor.execute("EXEC delete_product_data @product_id=%s", [product_id])

            return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
#company prefix dropdown for sender
class CompanyPrefixAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC get_company_prefix")
            columns = [col[0] for col in cursor.description]
            company_prefix_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'company_prefix_data': company_prefix_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        
        
#product gtin details
class GtinAPIView(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            # gln= data['gln']
            cursor = connection.cursor()
            # cursor.execute("EXEC get_gtin_details'" + str(gln) + "'")
            cursor.execute("EXEC get_gtin_details")
            
            columns = [col[0] for col in cursor.description]
            gtin_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'gtin_data': gtin_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#sender gln details for dropdown
class GlnAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC get_gln_details")
            columns = [col[0] for col in cursor.description]
            gln_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'gln_data': gln_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
#shipment permit details for dropdown
class ShipmentPermitAPIView(APIView):                   
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            gln = data['gln']
            cursor = connection.cursor()
            cursor.execute("EXEC get_shipment_permit'" + str(gln) + "'")
            columns = [col[0] for col in cursor.description]
            shipment_permit_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'shipment_permit_data': shipment_permit_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShipmentPermitDropdownAPIView(APIView):                   
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC get_shipment_permit_dropdown")
            columns = [col[0] for col in cursor.description]
            shipment_permit_data_drp = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'shipment_permit_data_drp': shipment_permit_data_drp}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#get instance id
class GetInstanceIdAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC get_instance_id")
            columns = [col[0] for col in cursor.description]
            instance_id_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'instance_id_data': instance_id_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

# add customer  data
class AddCustomerDataAPIView(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            customer_name = data['customer_name']
            customer_gln = data['customer_gln']
            company_prefix = data['company_prefix']
            shipmentpermit = data['shipmentpermit']
            customer_address = data['customer_address']
            customer_city = data['customer_city']
            customer_province = data['customer_province']
            customer_country = data['customer_country']
            contact_no = data['contact_no']
            email = data['email']

            # Check if already exists
            if customer_master.objects.filter(
                customer_name=customer_name,
                customerGLN=customer_gln,
                status=1
            ).exists():
                return Response({'error': 'Customer already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate GLN with company prefix
            if not customer_gln.startswith(company_prefix):
                return Response({'error': 'GLN does not match the Company Prefix'}, status=status.HTTP_400_BAD_REQUEST)

            # Derive SGLN
            location_part = customer_gln[len(company_prefix):-1]  # Exclude check digit
            sgln = f"{company_prefix}.{location_part}"

            # Call stored procedure securely
            with connection.cursor() as cursor:
                cursor.execute("""
                    EXEC add_customer_data 
                        @customer_name=%s,
                        @customer_gln=%s,
                        @cmpny_prefix=%s,
                        @sgln=%s,
                        @s_p=%s,
                        @customer_address=%s,
                        @customer_city=%s,
                        @customer_province=%s,
                        @customer_country=%s,
                        @contact_no=%s,
                        @email=%s
                """, [
                    customer_name,
                    customer_gln,
                    company_prefix,
                    sgln,
                    shipmentpermit,
                    customer_address,
                    customer_city,
                    customer_province,
                    customer_country,
                    contact_no,
                    email
                ])

            return Response({'data': 'Customer data added successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FetchCustomerDataAPIView(APIView):
    def post(self, request):
        try:
            # Fetch customer data using stored procedure
            cursor = connection.cursor()
            cursor.execute("EXEC get_customer_data")
            columns = [col[0] for col in cursor.description]
            customer_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'customer_data': customer_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateCustomerDataAPIView(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            customer_id = data['customer_id']
            customer_name = data['customer_name']
            customer_gln = data['customer_gln']
            company_prefix = data['company_prefix']
            shipmentpermit = data['shipmentpermit']
            customer_address = data['customer_address']
            customer_city = data['customer_city']
            customer_province = data['customer_province']
            customer_country = data['customer_country']
            contact_no = data['contact_no']
            email = data['email']

            # Validate GLN with company prefix
            if not customer_gln.startswith(company_prefix):
                return Response({'error': 'GLN does not match the Company Prefix'}, status=status.HTTP_400_BAD_REQUEST)

            # Derive SGLN
            location_part = customer_gln[len(company_prefix):-1]  # Exclude check digit
            sgln = f"{company_prefix}.{location_part}"

            # Call stored procedure securely
            with connection.cursor() as cursor:
                cursor.execute("""
                    EXEC update_customer_data 
                        @customer_id=%s,
                        @customer_name=%s,
                        @customer_gln=%s,
                        @cmpny_prefix=%s,
                        @sgln=%s,
                        @s_p=%s,
                        @customer_address=%s,
                        @customer_city=%s,
                        @customer_province=%s,
                        @customer_country=%s,
                        @contact_no=%s,
                        @email=%s
                """, [
                    customer_id,
                    customer_name,
                    customer_gln,
                    company_prefix,
                    sgln,
                    shipmentpermit,
                    customer_address,
                    customer_city,
                    customer_province,
                    customer_country,
                    contact_no,
                    email
                ])

            return Response({'data': 'Customer data updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteCustomerDataAPIView(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            customer_id = data['customer_id']

            # Check if customer exists
            if not customer_master.objects.filter(id=customer_id, status=1).exists():
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

            # Call stored procedure to delete customer
            with connection.cursor() as cursor:
                cursor.execute("EXEC delete_customer_data @customer_id=%s", [customer_id])

            return Response({'message': 'Customer deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FetchReasonCodesAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC fetch_reason_codes")
            columns = [col[0] for col in cursor.description]
            reason_codes_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'reason_codes_data': reason_codes_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ScanSGTINView(APIView):
    """
    API View to scan and parse raw GS1-128 encoded barcodes,
    extracting common Application Identifiers like GTIN, Expiration Date,
    Batch Number, and Serial Number, as well as AI 8015.
    """
    def post(self, request, *args, **kwargs):
        raw_data = request.data.get('barcode', '')
        print("Raw scanned input:", repr(raw_data))  # Safe print

        # Strip ASCII 29 (FNC1) if present at the beginning
        # Also strip common scanner prefixes like '>'
        if raw_data and raw_data.startswith(chr(29)):
            raw_data = raw_data[1:]
        if raw_data and raw_data.startswith('>'):
            raw_data = raw_data[1:]

        parsed_data = {
            "gtin": None,
            "expiration_date": None,
            "batch_number": None,
            "serial_number": None,
            "ai_8015_data": None, # To capture data for AI 8015
            "unparsed_remainder": None, # For debugging
        }

        # Define known GS1 Application Identifiers (AI) and their parsing rules.
        # Fixed length AIs: (AI_prefix, length_of_data)
        # Variable length AIs: (AI_prefix, max_length_of_data) - need to be terminated by FNC1 or next AI
        # This list should be ordered by length of AI prefix (longest first) for correct matching.
        # AI Data Format: n = numeric, an = alphanumeric
        
        # We define a list of AIs and their properties for parsing.
        # The key is the AI prefix, value is a tuple: (data_length, field_name, is_variable)
        # is_variable=True means it's terminated by next AI or end of string.
        # Data lengths are total characters including AI prefix.
        
        # A map of AI prefixes to their expected data length (after the AI prefix itself)
        # and the key to store them in parsed_data.
        # For variable length AIs, None for data_length means it's variable and
        # terminated by the next AI or end of string.
        
        ai_rules = [
            ("01", 14, "gtin", False),             # GTIN - 14 digits
            ("17", 6, "expiration_date", False),   # Expiration Date YYMMDD - 6 digits
            ("10", None, "batch_number", True),    # Batch/Lot Number - up to 20 alphanumeric (variable)
            ("21", None, "serial_number", True),   # Serial Number - up to 20 alphanumeric (variable)
            ("8015", None, "ai_8015_data", True),  # GTIN of grouped item - variable, up to 14 alphanumeric
            # Add other common AIs if they might appear:
            # ("00", 18, "sscc", False),            # Serial Shipping Container Code
            # ("240", None, "additional_product_id", True), # Additional product identification
            # ("37", None, "number_of_units", True), # Number of units contained
            # ... add more as per your requirements
        ]
        
        # Sort AI rules by the length of the AI prefix in descending order
        # to ensure that longer AIs (e.g., "8015") are matched before shorter ones (e.g., "80").
        ai_rules.sort(key=lambda x: len(x[0]), reverse=True)

        current_pos = 0
        temp_data = raw_data

        while current_pos < len(temp_data):
            matched_an_ai = False
            for ai_prefix, data_length, field_name, is_variable in ai_rules:
                if temp_data[current_pos:].startswith(ai_prefix):
                    ai_start = current_pos
                    data_body_start = current_pos + len(ai_prefix)

                    if not is_variable:
                        # Fixed-length AI
                        expected_total_length = len(ai_prefix) + data_length
                        if len(temp_data) >= ai_start + expected_total_length:
                            parsed_data[field_name] = temp_data[data_body_start:ai_start + expected_total_length]
                            current_pos += expected_total_length
                            matched_an_ai = True
                            break # Found and processed this AI, move to next part of string
                        else:
                            # Malformed: data too short for fixed-length AI
                            print(f"Error: Malformed data for fixed-length AI {ai_prefix}. Data too short.")
                            return Response({"error": f"Invalid barcode format: Malformed data for AI {ai_prefix}"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Variable-length AI
                        # Find the end of the data for this variable AI.
                        # It's either the start of the next AI, or the end of the string.
                        data_end = len(temp_data) # Default to end of string

                        # Check for the next AI prefix (excluding the current one)
                        # We need to find the *first* occurrence of *any* other AI prefix.
                        # Create a list of other AI prefixes to search for.
                        other_ai_prefixes = [rule[0] for rule in ai_rules if rule[0] != ai_prefix]
                        
                        # Sort these by length descending to ensure longer AIs are checked first as terminators
                        other_ai_prefixes.sort(key=len, reverse=True)

                        for next_ai_prefix in other_ai_prefixes:
                            match_index = temp_data.find(next_ai_prefix, data_body_start)
                            if match_index != -1:
                                data_end = match_index
                                break # Found the next AI, this is where the current AI's data ends

                        parsed_data[field_name] = temp_data[data_body_start:data_end]
                        current_pos = data_end
                        matched_an_ai = True
                        break # Found and processed this AI, move to next part of string
            
            if not matched_an_ai:
                # If no known AI was matched at the current position, it indicates an issue
                # e.g., unexpected characters, unknown AI, or malformed data.
                print(f"Error: No known AI found at position {current_pos} in: {temp_data[current_pos:]}")
                parsed_data["unparsed_remainder"] = temp_data[current_pos:]
                break # Stop parsing, as we're stuck

        # Check if GTIN or Expiration Date (critical fields for SGTIN) were found.
        # This part depends on what you consider "valid SGTIN format" for Tatmeen.
        # If your input example `>8015890121300800517261100103074V052` is indeed a valid SGTIN for Tatmeen,
        # then the requirement for AI "01" and "17" at the very beginning might be too strict.
        # Tatmeen documentation indicates GTIN, Serial Number, Batch/Lot Number, and Expiry date are all required data elements for dispensing.
        # It also explicitly states "SGTIN = (01)GTIN(21)SERIAL" for manual entry.
        # This implies that a standard SGTIN still uses 01 and 21.
        # The barcode `>8015...` is likely a different GS1 structure (e.g., for logistic units) that also carries some SGTIN-like data.

        # Let's adjust the error message based on the input example.
        # If AI 8015 is present, and we're looking for SGTIN specific data, then we need to see if the
        # GTIN (01), Expiry (17), Batch (10), and Serial (21) are embedded.

        # Given your provided example: `>8015890121300800517261100103074V052`
        # Let's re-parse it with the new logic:
        # 1. `>` stripped: `8015890121300800517261100103074V052`
        # 2. `8015` is matched (AI 8015, variable length)
        #    - `parsed_data["ai_8015_data"]` will capture `890121300800517261100103074V052`
        #    - `current_pos` becomes `len(raw_data)` so the loop ends.
        
        # This explains why your original regex didn't match and why the new general parser captures `8015`'s data as the whole remainder.
        # If Tatmeen expects (01), (17), (10), (21) *within* an (8015) structure or separately,
        # then the parsing logic needs to become even more complex (e.g., parsing the `ai_8015_data` itself).
        # However, typically AIs are at the top level of the GS1-128 string, not nested within other AI data fields.

        # Based on the typical GS1-128 structure, if the barcode starts with `8015`, it's not starting with `01`.
        # Therefore, if the expectation for SGTIN is strictly `01(GTIN) ...`, then the input `>8015...` is not a direct SGTIN.

        # For the provided example to yield GTIN, Expiration, Batch, Serial from AI 8015 data,
        # the format inside AI 8015 would need to contain the other AIs (01, 17, 10, 21),
        # which is not standard GS1-128 practice.

        # Let's return the extracted data. If specific AIs are *missing* and are required,
        # you should add a final validation step.
        
        # Example: If GTIN (01) and Expiration Date (17) are mandatory for your SGTIN context:
        if not parsed_data["gtin"] and not parsed_data["ai_8015_data"]:
             return Response({"error": "Invalid barcode format: Neither GTIN (AI 01) nor AI 8015 found."}, status=status.HTTP_400_BAD_REQUEST)
        
        # If your definition of "SGTIN" requires AI 01, 17, 10, 21, then you should check for their presence.
        # If it's flexible and accepts AI 8015 as a primary identifier, then this is fine.
        
        # For the provided input `>8015890121300800517261100103074V052`, the `ai_8015_data` will contain the entire rest of the string.
        # This implies that the 'GTIN', 'expiration_date', 'batch_number', 'serial_number' you expect might be *encoded within* the 8015 data,
        # but that's not standard GS1-128 parsing; typically, AIs are top-level.
        # Given your Tatmeen reference, Tatmeen specifically mentions SGTIN as `(01)GTIN(21)SERIAL`.
        # This suggests your sample barcode might be for a different type of GS1-128 label, or it's a "logistic unit" barcode rather than a "product item" SGTIN.

        # If you *must* extract (01), (17), (10), (21) from an input like `>8015...`,
        # then the `8015` data itself must contain those AIs.
        # Let's assume the `raw_data` will contain the AIs explicitly, and the input example
        # was just to show the `>` prefix and a different starting AI.

        # **To make your code work with the example `>8015...` if it's supposed to represent an SGTIN:**
        # This is the tricky part. The input `8015890121300800517261100103074V052`
        # doesn't contain the `01` and `17` AI prefixes.
        # If "8015" is some custom "SGTIN-like" format for Tatmeen that *doesn't* use explicit AIs for GTIN/Expiry/Batch/Serial within it,
        # you would need to define fixed positions or internal structure for the data following "8015".

        # For instance, if `8015` implies a specific structure like:
        # 8015 (AI) + 14 digits (GTIN) + 6 digits (Expiry) + rest (Batch/Serial)
        # That would be a *custom interpretation* of `8015` data.
        # Based on GS1 standards, AI 8015 usually precedes a variable-length GTIN of a trade item grouped for a logistic unit, and this GTIN itself might not have the AI 01 prefix because it's *already* implied by 8015.

        # Let's refine the error for missing SGTIN components, assuming SGTIN *must* have (01) GTIN.
        if not parsed_data["gtin"] or not parsed_data["expiration_date"]:
             return Response({"error": "Invalid SGTIN format: GTIN (AI 01) and/or Expiration Date (AI 17) not found as top-level AIs. If this is a logistics unit barcode (AI 8015), specific SGTIN data might be missing or not parsable by this endpoint."}, status=status.HTTP_400_BAD_REQUEST)

        # If you want to return the ai_8015_data even if it's not a standard SGTIN, you can:
        response_data = {
            "gtin": parsed_data["gtin"],
            "expiration_date": parsed_data["expiration_date"],
            "batch_number": parsed_data["batch_number"],
            "serial_number": parsed_data["serial_number"],
        }
        if parsed_data["ai_8015_data"]:
            response_data["ai_8015_data"] = parsed_data["ai_8015_data"]
        if parsed_data["unparsed_remainder"]:
            response_data["unparsed_remainder"] = parsed_data["unparsed_remainder"] # For debugging unknown parts

        return Response(response_data, status=status.HTTP_200_OK)


#Scanning for SSCC
class ScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')

        # Pattern to extract SSCC
        # pattern = r"\(00\)(\d{18})"
        pattern = r"(?:\(00\))?(\d{18})"
        match = re.match(pattern, barcode)
        
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)
        
        sscc = match.group(1)

        data = {
            "sscc": sscc
        }
        return Response(data, status=status.HTTP_200_OK)




# Query Message Status
class QueryMessageStatusAPIView(APIView):
    def post(self, request):
        try:
            instance_id = request.data.get('instance_id')
            if not instance_id:
                return Response({'error': 'Missing instance_id'}, status=400)

            # Build SOAP XML
            status_query_xml = f"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <tatmeenMsgStatusQuery xsi:noNamespaceSchemaLocation="schema.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                        <language>E</language>
                        <instanceIdentifier>{instance_id}</instanceIdentifier>
                    </tatmeenMsgStatusQuery>
                </soap:Body>
            </soap:Envelope>
            """

            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/MsgStatusQuery',
                data=status_query_xml,
                headers=headers
            )

            if response.status_code != 200:
                return Response({
                    'status_code': response.status_code,
                    'response_text': response.text
                }, status=response.status_code)

            # Parse the XML response
            root = ET.fromstring(response.text)
            ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}

            # Navigate to tatmeenResponse
            body = root.find('soap:Body', ns)
            tatmeen_response = body.find('tatmeenResponse')

            instance_identifier = tatmeen_response.findtext('instanceIdentifier')
            message_status = tatmeen_response.findtext('messagestatus', default='')

            log_list = []
            log_entries = tatmeen_response.find('logList')
            if log_entries is not None:
                for log in log_entries.findall('log'):
                    log_type = log.findtext('type')
                    log_message = log.findtext('message')
                    log_list.append({'type': log_type, 'message': log_message})

            return Response({
                'status_code': 200,
                'instanceIdentifier': instance_identifier,
                'messagestatus': message_status.strip() if message_status else None,
                'logList': log_list
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ProductVerificationAPIView(APIView):
    def post(self, request):
        data = request.data
        gtin = data.get('product_name')
        serial = data.get('serial')

        if not gtin:
            return Response({'error': 'Missing product_name (GTIN)'}, status=400)

        try:
            indicator_digit = gtin[0]
            core_gtin = gtin[1:-1]  # Remove indicator and check digit
            vendor = None
            matched_prefix = ''

            for v in vendor_master.objects.using('default').all():
                if core_gtin.startswith(v.CompanyPrefix):
                    vendor = v
                    matched_prefix = v.CompanyPrefix
                    break

            if not vendor:
                return Response({'error': 'No matching CompanyPrefix found in vendor_master'}, status=404)

            item_ref = core_gtin[len(matched_prefix):]
            sgtin = f"urn:epc:id:sgtin:{matched_prefix}.{indicator_digit}{item_ref}.{serial}"

        except Exception as e:
            return Response({'error': f'Failed to process GTIN: {str(e)}'}, status=500)

        # Build SOAP XML body
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
        <env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
            <env:Header/>
            <env:Body>
                <ProductVerificationRequest>
                    <GeoLatitude/>
                    <GeoLongitude/>
                    <Language>E</Language>
                    <ProductID>{sgtin}</ProductID>
                </ProductVerificationRequest>
            </env:Body>
        </env:Envelope>"""

        # Tatmeen API Call
        token_data = get_valid_token()
        headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "apikey": settings.TATMEEN_API_KEY,
            "Content-Type": "application/soap+xml; charset=utf-8"
        }

        response = requests.post(
            'https://tatmeenapim.mohap.gov.ae/v1/VerifyProduct',
            data=xml_body,
            headers=headers
        )

        response_data = {}

        try:
            root = ET.fromstring(response.text)
            ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}

            body = root.find('soap:Body', ns)
            verification_response = body.find('ProductVerificationResponse')

            # Check for ProductDetails (Success)
            product_details = verification_response.find('ProductDetails')
            if product_details is not None:
                response_data['ProductID'] = product_details.findtext('ProductID')
                response_data['GLN'] = product_details.findtext('GLN')
                response_data['LocationName'] = product_details.findtext('LocationName')
                response_data['RegulationAuthority'] = product_details.findtext('./LocationNumber/RegulationAuthority')
                response_data['RegulationLicense'] = product_details.findtext('./LocationNumber/RegulationLicense')
                response_data['GeoLatitude'] = product_details.findtext('GeoLatitude')
                response_data['GeoLongitude'] = product_details.findtext('GeoLongitude')
                response_data['ProductDescription'] = product_details.findtext('ProductDescription')
                response_data['LotNumber'] = product_details.findtext('LotNumber')
                response_data['DateOfManufacture'] = product_details.findtext('DateOfManufacture')
                response_data['DateOfExpiry'] = product_details.findtext('DateOfExpiry')

                # Status
                status_node = verification_response.find('./ProductStatusList/ProductStatus/Status')
                response_data['ProductStatus'] = status_node.text if status_node is not None else None

            else:
                # Check for error
                log = verification_response.find('./LogList/Log')
                response_data['ErrorType'] = log.findtext('Type')
                response_data['ErrorCode'] = log.findtext('code')
                response_data['ErrorMessage'] = log.findtext('Message')

        except Exception as e:
            return Response({'error': 'Failed to parse Tatmeen response', 'details': str(e)})

        return Response({
            'status': 'sent',
            'vendor': vendor.vendor_name,
            'product_sgtin': sgtin,
            'response_code': response.status_code,
            'tatmeen_response': response_data
        })



class SSCCProductVerificationAPIView(APIView):
    def post(self, request):
        scanned_sscc = request.data.get("sscc")
        if not scanned_sscc:
            return Response({"error": "Missing SSCC"}, status=400)

        try:
            if not scanned_sscc.isdigit() or len(scanned_sscc) != 18:
                raise ValueError("SSCC must be 18-digit numeric")

            extension_digit = scanned_sscc[0]
            check_digit = scanned_sscc[-1]
            core = scanned_sscc[1:-1]  # remove extension and check digit

            vendor = None
            matched_prefix = ""

            for v in vendor_master.objects.using('default').all():
                if core.startswith(v.CompanyPrefix):
                    vendor = v
                    matched_prefix = v.CompanyPrefix
                    break

            if not vendor:
                raise ValueError("Company prefix not found in SSCC")

            serial_ref_only = core[len(matched_prefix):]
            full_serial_ref = extension_digit + serial_ref_only

            sscc_urn = f"urn:epc:id:sscc:{matched_prefix}.{full_serial_ref}"

        except Exception as e:
            return Response({'error': f"Invalid SSCC format: {str(e)}"}, status=400)

        # Build SOAP request
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
        <env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
            <env:Header/>
            <env:Body>
                <ProductVerificationRequest>
                    <GeoLatitude/>
                    <GeoLongitude/>
                    <Language>E</Language>
                    <ProductID>{sscc_urn}</ProductID>
                </ProductVerificationRequest>
            </env:Body>
        </env:Envelope>"""

        token_data = get_valid_token()
        headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "apikey": settings.TATMEEN_API_KEY,
            "Content-Type": "application/soap+xml; charset=utf-8"
        }

        response = requests.post(
            'https://tatmeenapim.mohap.gov.ae/v1/VerifyProduct',
            data=xml_body,
            headers=headers
        )

        # Parse Tatmeen response
        response_data = {}
        try:
            root = ET.fromstring(response.text)
            ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
            body = root.find('soap:Body', ns)
            verification_response = body.find('ProductVerificationResponse')

            product_details = verification_response.find('ProductDetails')
            if product_details is not None:
                response_data['ProductID'] = product_details.findtext('ProductID')
                response_data['GLN'] = product_details.findtext('GLN')
                response_data['LocationName'] = product_details.findtext('LocationName')
                response_data['RegulationAuthority'] = product_details.findtext('./LocationNumber/RegulationAuthority')
                response_data['RegulationLicense'] = product_details.findtext('./LocationNumber/RegulationLicense')
                response_data['GeoLatitude'] = product_details.findtext('GeoLatitude')
                response_data['GeoLongitude'] = product_details.findtext('GeoLongitude')
                response_data['ProductDescription'] = product_details.findtext('ProductDescription')
                response_data['LotNumber'] = product_details.findtext('LotNumber')
                response_data['DateOfManufacture'] = product_details.findtext('DateOfManufacture')
                response_data['DateOfExpiry'] = product_details.findtext('DateOfExpiry')
                response_data['ProductStatus'] = verification_response.findtext('./ProductStatusList/ProductStatus/Status')

            else:
                log = verification_response.find('./LogList/Log')
                response_data['ErrorType'] = log.findtext('Type')
                response_data['ErrorCode'] = log.findtext('code')
                response_data['ErrorMessage'] = log.findtext('Message')

        except Exception as e:
            return Response({'error': 'Failed to parse Tatmeen response', 'details': str(e)})

        return Response({
            'status': 'sent',
            'vendor': vendor.vendor_name if vendor else None,
            'sscc_urn': sscc_urn,
            'response_code': response.status_code,
            'tatmeen_response': response_data
        })







class GtinCountAPIView(APIView):
    def get(self, request):
        try:
            # Count distinct GTINs from ProductMaster table
            gtin_count = ProductMaster.objects.using('default').values('gtin').distinct().count()
            
            return Response({
                'status': 'success',
                'gtin_count': gtin_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PartnerCountAPIView(APIView):
    def get(self, request):
        try:
            # Count total business partners from user_details table
            partner_count = user_details.objects.using('default').count()
            
            if partner_count == 0:
                return Response({
                    'status': 0,
                    'message': 'No business partners found in the system'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'status': 1,
                'total_partners': partner_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 0,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            ############################Destination api###################################
            #destination gln details for dropdown
class DestinationGlnAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC get_destination_gln_details")
            columns = [col[0] for col in cursor.description]
            destination_gln_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'destination_gln_data': destination_gln_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


###################################### NEW PROCESS ###########################################
###################################### 1. RECEIVING  #########################################

class TestFunction(APIView):
    def post(self, request):
        data = request.data
        instance_id = data.get('instance_id')

        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC rec_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                result.append(dict(zip(columns, row)))

        if not result:
            return Response({'error': 'No data found for the given instance ID'}, status=404)

        return Response(result)



def generate_sscc_urn(sscc, supplier_gln):
    """
    Generate URN for SSCC using company prefix from vendor_master (based on supplier_gln).
    """
    vendor = vendor_master.objects.filter(GLN=supplier_gln).first()
    if not vendor:
        raise ValueError(f"No vendor found for SupplierGLN: {supplier_gln}")

    company_prefix = vendor.CompanyPrefix
    extension_digit = sscc[0]
    check_digit = sscc[-1]
    core = sscc[1:-1]  # Remove extension and check digit

    serial_ref_only = core[len(company_prefix):]
    full_serial_ref = extension_digit + serial_ref_only
    return f"urn:epc:id:sscc:{company_prefix}.{full_serial_ref}"

def generate_sgln_urn(sender_gln):
    """
    Generate URN for SGLN using company prefix from CompanyDetails (based on sender_gln).
    """
    company = CompanyDetails.objects.filter(GLN=sender_gln).first()
    if not company:
        raise ValueError(f"No company prefix found for SenderGLN: {sender_gln}")

    company_prefix = company.company_prefix
    location_reference = sender_gln[len(company_prefix):-1]
    sgln_serial = str(random.randint(100000, 999999))  # Replace with your logic if needed
    return f"urn:epc:id:sgln:{company_prefix}.{location_reference}.{sgln_serial}"


def generate_destination_sgln_urn(destination_gln):
    """
    Generate URN for SGLN using company prefix from Customer Master (based on customer GLN).
    """
    customer = customer_master.objects.filter(customerGLN=destination_gln).first()
    if not customer:
        raise ValueError(f"No company prefix found for Customer GLN: {destination_gln}")

    customerCompanyPrefix = customer.customerCompanyPrefix
    location_reference = destination_gln[len(customerCompanyPrefix):-1]
    sgln_serial = str(random.randint(100000, 999999))  # Replace with your logic if needed
    return f"urn:epc:id:sgln:{customerCompanyPrefix}.{location_reference}.{sgln_serial}"


# def generate_sgtin_from_gtin(gtin: str, product_model, vendor_model):
#     try:
#         product = product_model.objects.get(gtin=gtin)
#     except product_model.DoesNotExist:
#         raise ValueError(f"No product found for GTIN: {gtin}")

#     manufacturer_gln = product.manufacturer

#     try:
#         vendor = vendor_model.objects.get(GLN=manufacturer_gln)
#     except vendor_model.DoesNotExist:
#         raise ValueError(f"No vendor found with GLN: {manufacturer_gln}")

#     company_prefix = vendor.CompanyPrefix
#     gtin_body = gtin[:-1]
#     item_ref = gtin_body[len(company_prefix):]
#     serial_number = f"{random.randint(100000, 999999)}"
#     sgtin = f"urn:epc:id:sgtin:{company_prefix}.{item_ref}.{serial_number}"
#     return sgtin

def generate_sgtin_from_gtin(gtin: str, product_model, vendor_model):
    try:
        product = product_model.objects.get(gtin=gtin)
    except product_model.DoesNotExist:
        raise ValueError(f"No product found for GTIN: {gtin}")

    manufacturer_gln = product.manufacturer

    try:
        vendor = vendor_model.objects.get(GLN=manufacturer_gln)
    except vendor_model.DoesNotExist:
        raise ValueError(f"No vendor found with GLN: {manufacturer_gln}")

    company_prefix = vendor.CompanyPrefix
    cp_len = len(company_prefix)

    # GTIN-14: Indicator (1) + Company Prefix + Item Ref + Check Digit
    gtin_body = gtin[:-1]  # Remove check digit
    indicator = gtin_body[0]  # First digit is indicator
    item_ref = gtin_body[1+cp_len:]  # Skip indicator + company prefix

    serial_number = f"{random.randint(100000, 999999)}"
    sgtin = f"urn:epc:id:sgtin:{company_prefix}.{indicator}{item_ref}.{serial_number}"
    return sgtin


def get_tatmeen_instance_status(instance_id):
    """
    Function to get Tatmeen instance status for a given instance_id.
    Returns a dictionary with status, messagestatus, and logList.
    """
    if not instance_id:
        return {'status': 'error', 'message': 'Missing instance_id'}

    # Build SOAP XML
    status_query_xml = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
        <soap:Header/>
        <soap:Body>
            <tatmeenMsgStatusQuery xsi:noNamespaceSchemaLocation="schema.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <language>E</language>
                <instanceIdentifier>{instance_id}</instanceIdentifier>
            </tatmeenMsgStatusQuery>
        </soap:Body>
    </soap:Envelope>"""

    # try:
    token_data = get_valid_token()
    headers = {
        "Authorization": f"Bearer {token_data['access_token']}",
        "apikey": settings.TATMEEN_API_KEY,
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    response = requests.post(
        'https://tatmeenapim.mohap.gov.ae/v1/MsgStatusQuery',
        data=status_query_xml,
        headers=headers,
        timeout=15
    )

    print("MsgStatusQuery Status Code:", response.status_code)
    if response.status_code != 200:
        return {
            'status': 'error',
            'http_status': response.status_code,
            'message': response.text
        }

    # Parse XML
    root = ET.fromstring(response.text)
    ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
    body = root.find('soap:Body', ns)
    tatmeen_response = body.find('tatmeenResponse')
    print("=====tatmeenResponse=====",tatmeen_response)
    instance_identifier = tatmeen_response.findtext('instanceIdentifier')
    print("=======instance identifier======", instance_identifier)
    raw_message_status = tatmeen_response.findtext('messagestatus', default='')
    message_status = re.sub(r'\s+', ' ', raw_message_status).strip()
    print("=======message status======",message_status)

    log_list = []
    log_entries = tatmeen_response.find('logList')
    if log_entries is not None:
        for log in log_entries.findall('log'):
            log_type = log.findtext('type')
            log_message = log.findtext('message')
            log_list.append({'type': log_type, 'message': log_message})

            with connection.cursor() as y:
                y.execute("EXEC InsertTatmeenLog @InstanceIdentifier=%s,@MessageStatus=%s,@LogType=%s,@LogMessage=%s",[instance_identifier, message_status, log_type, log_message])
    rec_tat_msg = []
    with connection.cursor() as z:
        z.execute("EXEC fetch_rec_tatmeen_logs @InstanceIdentifier = %s", [instance_identifier])
        columns = [col[0] for col in z.description]
        for row in z.fetchall():
            row_dict = dict(zip(columns, row))
            if 'MessageStatus' in row_dict and row_dict['MessageStatus'] is not None:
                # Also clean when retrieving from DB, in case old data has the issue
                row_dict['MessageStatus'] = re.sub(r'\s+', ' ', row_dict['MessageStatus']).strip()
            rec_tat_msg.append(row_dict)
    return {
        'messagestatus': message_status,
        'logList': log_list,
        'rec_tat_msg':rec_tat_msg
    }

    # except Exception as e:
    #     return {'status': 'error', 'message': str(e)}


class REC_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = receiving_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"REC{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    receiving_guid_map.objects.create(
                        guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender', '')
        receiver_gln = request.data.get('receiver', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempReceiveScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_rec_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC rec_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"rec_results":results}, status=status.HTTP_200_OK)
        

                
class RecFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_recscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            rec_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'rec_scan_data': rec_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiveSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']

        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC rec_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======", result)

        if not result:
            return Response({"error": "No data found for this instance_id"}, status=404)

        # Use the first row for shared fields
        first = result[0]
        sender_gln = first['SenderGLN']
        receiver_gln = first['ReceiverGLN']
        event_time = first['EventTime']
        sgln_urn = first['sgln']
        uuid = first['UUID']  # UUID is same across rows

        # Format event_time to UTC with Dubai TZ
        if isinstance(event_time, datetime):
            if event_time.tzinfo is None:
                dubai_tz = pytz.timezone('Asia/Dubai')
                event_time = dubai_tz.localize(event_time)
            event_time_utc = event_time.astimezone(pytz.utc)
            event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        else:
            event_time_str = str(event_time)

        event_time_zone_offset = "+04:00"

        # Build the <epcList> with all SSCC URNs
        epc_list_xml = ""
        for row in result:
            epc_list_xml += f"<epc>{row['sscc_urn']}</epc>\n"

        # Build the full XML body
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
            <soap:Header/>
            <soap:Body>
                <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                    <EPCISHeader>
                        <sbdh:StandardBusinessDocumentHeader>
                            <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                            <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender_gln}</sbdh:Identifier></sbdh:Sender>
                            <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver_gln}</sbdh:Identifier></sbdh:Receiver>
                            <sbdh:DocumentIdentification>
                                <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                <sbdh:InstanceIdentifier>{uuid}</sbdh:InstanceIdentifier>
                                <sbdh:Type>Events</sbdh:Type>
                                <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                            </sbdh:DocumentIdentification>
                        </sbdh:StandardBusinessDocumentHeader>
                    </EPCISHeader>
                    <EPCISBody>
                        <EventList>
                            <ObjectEvent>
                                <eventTime>{event_time_str}</eventTime>
                                <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                <epcList>
                                    {epc_list_xml.strip()}
                                </epcList>
                                <action>OBSERVE</action>
                                <bizStep>urn:epcglobal:cbv:bizstep:receiving</bizStep>
                                <disposition>urn:epcglobal:cbv:disp:in_progress</disposition>
                                <readPoint><id>{sgln_urn}</id></readPoint>
                                <bizLocation><id>{sgln_urn}</id></bizLocation>
                            </ObjectEvent>
                        </EventList>
                    </EPCISBody>
                </epcis:EPCISDocument>
            </soap:Body>
        </soap:Envelope>"""

        print("======= XML BODY =======", xml_body)

        token_data = get_valid_token()
        headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "apikey": settings.TATMEEN_API_KEY,
            "Content-Type": "application/soap+xml; charset=utf-8"
        }

        response = requests.post(
            'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
            data=xml_body,
            headers=headers
        )

        print("SendEPCIS Status Code:", response.status_code)
        print("SendEPCIS Response Text:", response.text)

        if response.status_code == 202:
            root = ET.fromstring(response.text)
            code_elem = root.find('.//code')

            if code_elem is not None and code_elem.text == '202':
                print("--------incoming---------")

                with connection.cursor() as r:
                    r.execute("EXEC update_receiving_guid_map @identifier = %s", [uuid])
                with connection.cursor() as s:
                    s.execute("EXEC usp_DumpTempReceiveScanDetails @identifier = %s", [uuid])
                with connection.cursor() as t:
                    t.execute("EXEC clear_rec_temp_data @identifier = %s", [uuid])

                status_response = get_tatmeen_instance_status(uuid)
                print("========status_response=======", status_response)

                message_status = status_response.get("messagestatus", "").strip()
                print("======Message status=====", message_status)

                if message_status == "S - Successful":
                    with connection.cursor() as u:
                        u.execute("EXEC update_receiving_sscc_event @identifier = %s", [uuid])
                    return Response({"log": status_response.get("logList", [])})

                elif message_status == "A - Technical Error":
                    with connection.cursor() as v:
                        v.execute("EXEC update_receiving_sscc_event_error @identifier = %s", [uuid])
                    return Response({"log": status_response.get("logList", [])})

                elif message_status == "":
                    return Response({
                        "error": "No message status returned. The instance might not exist or failed to process.",
                        "log": status_response.get("logList", [])
                    })

                else:
                    with connection.cursor() as w:
                        w.execute("EXEC update_receiving_sscc_event_unknown @identifier = %s", [uuid])
                    return Response({
                        "error": f"Unhandled message status: {message_status}",
                        "log": status_response.get("logList", [])
                    })

            else:
                return Response({
                    "error": "Failed to fetch message status from Tatmeen API.",
                    "log": status_response.get("logList", [])
                }, status=status_response.status_code)

        else:
            send_receive_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
            return Response({
                "message": "Tatmeen API did not accept the request. Retry scheduled.",
                "status_code": response.status_code,
                "retry": True
            })

########################## commissioning sscc products #############################

class COM_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = commision_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.cm_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"COM{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    commision_guid_map.objects.create(
                        cm_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.  
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender', '')
        receiver_gln = request.data.get('receiver', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')
        print("barcode cleaned:",barcode_cleaned)
        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)
        print("barcode cleaned:",sscc)

       
        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempCommSSCCScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_commsscc_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC comm_sscc_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"comm_results":results}, status=status.HTTP_200_OK)
        

class CommFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_CommSSCCScan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            comm_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'comm_scan_data': comm_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SubmitSSCCorPalletAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']

        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC comm_sscc_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))

        print("-----result----", result)

        if not result:
            return Response({"error": "No data found for this instance_id"}, status=404)

        # Use the first row for shared fields
        first = result[0]
        uuid = first['UUID']
        sender = first['SenderGLN']
        receiver = first['ReceiverGLN']
        event_time = first['EventTime']
        sgln = first['sgln']

        if isinstance(event_time, datetime):
            if event_time.tzinfo is None:
                dubai_tz = pytz.timezone('Asia/Dubai')
                event_time = dubai_tz.localize(event_time)
            event_time_utc = event_time.astimezone(pytz.utc)
            event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        else:
            event_time_str = str(event_time)

        event_time_zone_offset = "+04:00"

        # Build epcList
        epc_list_xml = ""
        for row in result:
            epc_list_xml += f"<epc>{row['sscc_urn']}</epc>\n"

        try:
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{uuid}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <!--Commissioning of SSCC/PALLET-->
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList>
                                        {epc_list_xml.strip()}
                                    </epcList>
                                    <action>ADD</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:commissioning</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:active</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            print("======= Final XML Body =======")
            print(xml_body)

            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code)

            if response.status_code == 202:
                root = ET.fromstring(response.text)
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    with connection.cursor() as r:
                        r.execute("EXEC update_comm_sscc_guid_map @identifier = %s", [uuid])
                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempCommssccScanDetails @identifier = %s", [uuid])
                    with connection.cursor() as t:
                        t.execute("EXEC clear_comm_sscc_temp_data @identifier = %s", [uuid])

                    status_response = get_tatmeen_instance_status(uuid)
                    message_status = status_response.get("messagestatus", "").strip()

                    if message_status == "S - Successful":
                        with connection.cursor() as u:
                            u.execute("EXEC update_comm_sscc_event @identifier = %s", [uuid])
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        with connection.cursor() as v:
                            v.execute("EXEC update_comm_sscc_event_error @identifier = %s", [uuid])
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        }, status=400)

                    else:
                        with connection.cursor() as w:
                            w.execute("EXEC update_comm_sscc_event_unknown @identifier = %s", [uuid])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        }, status=400)

            else:
                send_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
                return Response({
                    "message": "Tatmeen API did not accept the request. Retry scheduled.",
                    "status_code": response.status_code,
                    "retry": True
                }, status=response.status_code)

        except Exception as e:
            return Response({'error': str(e)}, status=500)


############ Shipping  #############

class SHIP_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = shipping_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.sh_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"SHIP{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    shipping_guid_map.objects.create(
                        sh_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShippingScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender', '')
        receiver_gln = request.data.get('receiver', '')
        supplier_gln = request.data.get('supplier_gln', '')
        destination_gln=request.data.get('destination_gln')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # if TempShippingScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
        #     return Response({
        #         "error": "This SSCC has already been scanned with this identifier and is still pending.",
        #         "identifier": identifier,
        #         "sscc": sscc
        #     })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
            des_sgln_urn=generate_destination_sgln_urn(destination_gln)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_shippingsscc_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s,
                    @destination_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s,
                    @des_sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln,destination_gln, event_time_dt,sscc_urn, sgln_urn,des_sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC ship_sscc_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"ship_results":results}, status=status.HTTP_200_OK)
        
class ShipppingFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_shipscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            ship_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'ship_scan_data': ship_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ShippingSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']

        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC ship_sscc_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))

        if not result:
            return Response({"error": "No data found for this instance_id"}, status=404)

        # Shared values from first row
        first = result[0]
        sender = first['SenderGLN']
        receiver = first['ReceiverGLN']
        sender_sgln = first['sgln']
        destination_sgln = first['destination_sgln']
        event_time = first['EventTime']

        if isinstance(event_time, datetime):
            if event_time.tzinfo is None:
                dubai_tz = pytz.timezone('Asia/Dubai')
                event_time = dubai_tz.localize(event_time)
            event_time_utc = event_time.astimezone(pytz.utc)
            event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        else:
            event_time_str = str(event_time)

        event_time_zone_offset = "+04:00"

        # Build EPC list from all rows
        epc_list_xml = ""
        for row in result:
            epc_list_xml += f"<epc>{row['sscc_urn']}</epc>\n"

        try:
            # Construct XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.0</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList>
                                        {epc_list_xml.strip()}
                                    </epcList>
                                    <action>OBSERVE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:shipping</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:in_transit</disposition>
                                    <readPoint><id>{sender_sgln}</id></readPoint>
                                    <bizLocation><id>{sender_sgln}</id></bizLocation>
                                    <extension>
                                        <sourceList>
                                            <source type="urn:epcglobal:cbv:sdt:owning_party">{sender_sgln}</source>
                                        </sourceList>
                                        <destinationList>
                                            <destination type="urn:epcglobal:cbv:sdt:owning_party">{destination_sgln}</destination>
                                            <destination type="urn:epcglobal:cbv:sdt:location">{destination_sgln}</destination>
                                        </destinationList>
                                    </extension>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>
            """

            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
                data=xml_body,
                headers=headers
            )

            print("SendEPCIS Status Code:", response.status_code)

            if response.status_code == 202:
                root = ET.fromstring(response.text)
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    # Update DB
                    with connection.cursor() as r:
                        r.execute("EXEC update_ship_sscc_guid_map @identifier = %s", [instance_id])
                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempShipssccScanDetails @identifier = %s", [instance_id])
                    with connection.cursor() as t:
                        t.execute("EXEC clear_ship_sscc_temp_data @identifier = %s", [instance_id])

                    # Get status
                    status_response = get_tatmeen_instance_status(instance_id)
                    message_status = status_response.get("messagestatus", "").strip()

                    if message_status == "S  - Successful":
                        with connection.cursor() as u:
                            u.execute("EXEC update_ship_sscc_event @identifier = %s", [instance_id])
                        return Response({"log": status_response.get("logList", [])})

                    elif "Technical Error" in message_status:
                        with connection.cursor() as v:
                            v.execute("EXEC update_ship_sscc_event_error @identifier = %s", [instance_id])
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        }, status=400)

                    else:
                        with connection.cursor() as w:
                            w.execute("EXEC update_ship_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        }, status=400)

            else:
                send_shipping_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
                return Response({
                    "message": "Tatmeen API did not accept the request. Retry scheduled.",
                    "status_code": response.status_code,
                    "retry": True
                }, status=response.status_code)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

############# export ############

class Exported_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = exported_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.ex_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"EXP{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    exported_guid_map.objects.create(
                        ex_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ExportedScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempExportedScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_exported_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC export_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"exp_results":results}, status=status.HTTP_200_OK)
            

                
# class ExportedFetchDataAPIView(APIView):
#     def post(self,request):
#         try:
#             body_unicode = request.body.decode('utf-8')
#             data = json.loads(body_unicode)

#             identifier=data['identifier']

#             cursor = connection.cursor()
#             cursor.execute("EXEC fetch_exportedscan_dataone @identifier = %s", [identifier])
#             columns = [col[0] for col in cursor.description]
#             expt_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

#             return Response({'expt_scan_data': expt_scan_data}, status=status.HTTP_200_OK)
#         except Exception as e:  
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ExportedSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC exported_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender= row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            instance_id=row['UUID']
            sscc_urn=row['sscc_urn']
            sgln=row['sgln']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"
            
            # Build the XML
            
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.0</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList><epc>{sscc_urn}</epc></epcList>
                                    <action>DELETE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:decommissioning</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:non_sellable_other</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>
            """

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_exported_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempExportedScanDetails @identifier = %s", [instance_id])

                    with connection.cursor() as t:
                        t.execute("EXEC clear_exported_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_exported_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_exported_sscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        with connection.cursor() as w:
                            w.execute("EXEC update_exported_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_exported_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})

            # except Exception as e:
            #     return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })


############ Lost #############

class Lost_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = lost_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.lt_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"LOST{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    lost_guid_map.objects.create(
                        lt_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class LostScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempLostScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_lost_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC lost_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"lost_results":results}, status=status.HTTP_200_OK)
        

                
class LostFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_lostscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            lost_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'lost_scan_data': lost_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class LostSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC lost_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender= row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            instance_id=row['UUID']
            sscc_urn=row['sscc_urn']
            sgln=row['sgln']
            
            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"
            
            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.0</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList><epc>{sscc_urn}</epc></epcList>
                                    <action>DELETE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:decommissioning</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:inactive</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_lost_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempLostScanDetails @identifier = %s", [instance_id])

                    with connection.cursor() as t:
                        t.execute("EXEC clear_lost_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_lost_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_lost_sscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        with connection.cursor() as w:
                            w.execute("EXEC update_receiving_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_lost_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})

            # except Exception as e:
            #     return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })


################# Sample ##############

class Sample_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = sample_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.sa_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"SAMPLE{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    sample_guid_map.objects.create(
                        sa_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SampleScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')
        reason_code=request.data.get('reason_code', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        
        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempSampleScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_sample_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s,
                    @reason_code = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,sscc_urn, sgln_urn,reason_code]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC sample_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"sample_results":results}, status=status.HTTP_200_OK)
        

                
class SampleFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_samplescan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            sample_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'sample_scan_data': sample_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SampleSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC sample_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            instance_id=row['UUID']
            sscc_urn=row['sscc_urn']
            sgln=row['sgln']
            reason_code=row['reason_code']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"
            
            # try:
            
            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.0</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList><epc>{sscc_urn}</epc></epcList>
                                    <action>OBSERVE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:inspecting</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:destroyed</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                    <tatmeen:reasonCode>{reason_code}</tatmeen:reasonCode>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_sample_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempSampleScanDetails @identifier = %s", [instance_id])

                    with connection.cursor() as t:
                        t.execute("EXEC clear_sample_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======in receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_sample_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_sample_sscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        with connection.cursor() as w:
                            w.execute("EXEC update_sample_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_sample_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})

            # except Exception as e:
            #     return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })





class TatmeenInstanceStatusAPIView(APIView):
    """
    API endpoint to check Tatmeen instance status (for Postman testing).
    """

    def post(self, request):
        instance_id = request.data.get("instance_id")
        if not instance_id:
            return Response({'error': 'Missing instance_id'}, status=status.HTTP_400_BAD_REQUEST)

        # Build SOAP XML
        status_query_xml = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
            <soap:Header/>
            <soap:Body>
                <tatmeenMsgStatusQuery xsi:noNamespaceSchemaLocation="schema.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <language>E</language>
                    <instanceIdentifier>{instance_id}</instanceIdentifier>
                </tatmeenMsgStatusQuery>
            </soap:Body>
        </soap:Envelope>"""

        try:
            token_data = get_valid_token()  # Get access token
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/MsgStatusQuery',
                data=status_query_xml,
                headers=headers,
                timeout=15
            )

            if response.status_code != 200:
                return Response({
                    'status': 'error',
                    'http_status': response.status_code,
                    'message': response.text
                }, status=response.status_code)

            # Parse XML response
            root = ET.fromstring(response.text)
            ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
            body = root.find('soap:Body', ns)
            tatmeen_response = body.find('tatmeenResponse')

            instance_identifier = tatmeen_response.findtext('instanceIdentifier')
            message_status = tatmeen_response.findtext('messagestatus', default='')

            # Parse logs
            log_list = []
            log_entries = tatmeen_response.find('logList')
            if log_entries is not None:
                for log in log_entries.findall('log'):
                    log_type = log.findtext('type')
                    log_message = log.findtext('message')
                    log_list.append({'type': log_type, 'message': log_message})

            return Response({
                'messagestatus': message_status.strip() if message_status else None,
                'logList': log_list
            })

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=500)


#################################### 15-07-2025 ################################

########################## commissioning sscc products #############################

class COM_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = commision_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.cm_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"COM{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    commision_guid_map.objects.create(
                        cm_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

########## commissioning sgtin #####################

#####  back here 1 #####

class Commission_SSGTIN_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = commision_guid_sgtin.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.cmsgtin_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"CSGTN{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    commision_guid_sgtin.objects.create(
                        cmsgtin_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommScanSGTINView(APIView):
    """
    API View to scan and parse SGTIN barcode and handle multiple EPCs or plain GTINs.
    """

    def post(self, request, *args, **kwargs):
        raw_data = request.data.get('barcode', '').strip()
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')
        shipment_permit = request.data.get('shipment_permit', '')
        expiry_date = request.data.get('expiration_date', '')
        manufacturing_date = request.data.get('manufacturing_date', '')
        lot_number = request.data.get('lot_number', '')
        epc_count = request.data.get('epc_count', '')

        print("Raw scanned input:", repr(raw_data))  # Debug safe print

        gtin = None
        expiration_date = None
        batch_number = None

        # Remove leading FNC1 if present
        raw_data = raw_data.lstrip(chr(29) + '>')

        # Detect if this is a full SGTIN string with AIs
        if "01" in raw_data and len(raw_data) > 16:
            idx = raw_data.find('01')
            raw_data = raw_data[idx:]
            pattern = r"01(\d{14})17(\d{6})10(.+)"
            match = re.match(pattern, raw_data)

            if not match:
                return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

            gtin, expiration_date, batch_number = match.groups()
            print("Extracted GTIN:", gtin)
            print("Extracted Expiration Date:", expiration_date)
            print("Extracted Batch Number:", batch_number)

        # If it's just GTIN-13 or GTIN-14
        elif raw_data.isdigit() and len(raw_data) in (13, 14):
            # Convert GTIN-13 to GTIN-14 (prepend 0)
            if len(raw_data) == 13:
                gtin = "0" + raw_data
            else:
                gtin = raw_data
            print("Detected plain GTIN:", gtin)

        else:
            return Response({"error": "Unrecognized barcode format"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse event_time safely
        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {"error": f"Invalid event_time format: '{event_time_str}'. Expected 'YYYY-MM-DDTHH:MM:SS'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse epc_count
        try:
            epc_count = int(epc_count) if epc_count else 1
        except ValueError:
            return Response({"error": "Invalid epc_count. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)

            sgtins = []
            for _ in range(epc_count):
                sgtin = generate_sgtin_from_gtin(gtin, ProductMaster, vendor_master)
                sgtins.append(sgtin)
            print("====Generated SGTINs:", sgtins)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        with connection.cursor() as cursor:
            for sgtin in sgtins:
                cursor.execute(
                    """
                    EXEC insert_commsgtin_tempscan_data 
                        @barcode = %s, 
                        @identifier = %s, 
                        @sender_gln = %s, 
                        @receiver_gln = %s,
                        @supplier_gln=%s, 
                        @EventTime = %s,
                        @expiration_date=%s,
                        @mfg_date=%s,
                        @shp_prmt=%s,
                        @lot_no=%s,
                        @sgln_urn = %s,
                        @sgtin=%s
                    """,
                    [gtin, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,
                     expiry_date, manufacturing_date, shipment_permit, lot_number, sgln_urn, sgtin]
                )

                cursor.execute("EXEC comm_sgtin_data_one @identifier = %s, @barcode = %s", [identifier, gtin])
                columns = [col[0] for col in cursor.description]
                fetched_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                results.extend(fetched_rows)

        return Response({"message": "Success", "comm_sgtin_results": results}, status=status.HTTP_200_OK)


class CommSGTINFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_CommSGTINProductScan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            comm_sgtin_products_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'comm_sgtin_products_data': comm_sgtin_products_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubmitEPCISAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']

        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC comm_sgtin_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))

        if not result:
            return Response({"error": "No data found for given instance_id"}, status=404)

        # Extract shared fields from the first row
        first = result[0]
        sender = first['SenderGLN']
        receiver = first['ReceiverGLN']
        event_time = first['EventTime']
        uuid = first['UUID']
        sgln = first['sgln']
        lot_number = first['lot_number']
        expiration_date = first['expiration_date']
        manufacturing_date = first['manufacturing_date']
        shipment_permit = first['shipment_permit']

        # Convert event_time to UTC string
        if isinstance(event_time, datetime):
            if event_time.tzinfo is None:
                dubai_tz = pytz.timezone('Asia/Dubai')
                event_time = dubai_tz.localize(event_time)
            event_time_utc = event_time.astimezone(pytz.utc)
            event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        else:
            event_time_str = str(event_time)

        event_time_zone_offset = "+04:00"

        # Build epcList from all rows (sgtin)
        epc_list_xml = ""
        for row in result:
            epc_list_xml += f"<epc>{row['sgtin']}</epc>\n"

        try:
            # Build XML once with full EPC list
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{uuid}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList>
                                        {epc_list_xml}
                                    </epcList>
                                    <action>ADD</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:commissioning</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:active</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                    <extension>
                                        <ilmd>
                                            <cbvmda:lotNumber>{lot_number}</cbvmda:lotNumber>
                                            <cbvmda:itemExpirationDate>{expiration_date}</cbvmda:itemExpirationDate>
                                        </ilmd>
                                    </extension>
                                    <tatmeen:lotManufacturingDate>{manufacturing_date}</tatmeen:lotManufacturingDate>
                                    <tatmeen:manufacturingOrigin>I</tatmeen:manufacturingOrigin>
                                    <tatmeen:shipmentPermit>{shipment_permit}</tatmeen:shipmentPermit>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>
            """

            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code)

            if response.status_code == 202:
                root = ET.fromstring(response.text)
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    with connection.cursor() as r:
                        r.execute("EXEC update_comm_sgtin_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempCommsgtinScanDetails @identifier = %s", [instance_id])

                    with connection.cursor() as t:
                        t.execute("EXEC clear_comm_sgtin_temp_data @identifier = %s", [instance_id])

                    status_response = get_tatmeen_instance_status(uuid)
                    message_status = status_response.get("messagestatus", "").strip()

                    if "successful" in message_status.lower():
                        with connection.cursor() as u:
                            u.execute("EXEC update_comm_sgtin_event @identifier = %s", [instance_id])
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A  - Technical Error":
                        with connection.cursor() as v:
                            v.execute("EXEC update_comm_sgtin_event_error @identifier = %s", [instance_id])
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        }, status=400)

                    else:
                        with connection.cursor() as w:
                            w.execute("EXEC update_comm_sgtin_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        }, status=400)

            elif response.status_code != 202:
                send_epcis_to_tatmeen.send(xml_body, token_data['access_token'])
                return Response({
                    "message": "Tatmeen API did not accept the request. Retry scheduled.",
                    "status_code": response.status_code,
                    "retry": True
                }, status=response.status_code)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

        return Response({"message": "success"})



### commissioning -- Shipper cases ###

class Commission_shippercase_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = commision_guid_shippercase.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.cmsh_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"CSC{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    commision_guid_shippercase.objects.create(
                        cmsh_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommScanShippercasesView(APIView):
    """
    API View to scan and parse SGTIN barcode and handle multiple EPCs.
    """

    def post(self, request, *args, **kwargs):
        raw_data = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender', '')
        receiver_gln = request.data.get('receiver', '')
        supplier_gln = request.data.get('supplier', '')
        event_time_str = request.data.get('event_time', '')
        shipment_permit = request.data.get('shipment_permit', '')
        expiry_date = request.data.get('expiration_date', '')
        manufacturing_date = request.data.get('manufacturing_date', '')
        lot_number = request.data.get('lot_number', '')
        epc_count = request.data.get('epc_count', '')

        print("Raw scanned input:", repr(raw_data))  # Safe print

        # Strip ASCII 29 (FNC1) if present
        raw_data = raw_data.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = raw_data.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        raw_data = raw_data[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, raw_data)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()
        print("Extracted GTIN:", gtin)
        print("Extracted Expiration Date:", expiration_date)
        print("Extracted Batch Number:", batch_number)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DDTHH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse epc_count safely
        try:
            epc_count = int(epc_count) if epc_count else 1
        except ValueError:
            return Response({"error": "Invalid epc_count. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)

            sgtins = []
            for _ in range(epc_count):
                sgtin = generate_sgtin_from_gtin(gtin, ProductMaster, vendor_master)
                sgtins.append(sgtin)
            print("====Generated SGTINs:", sgtins)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        with connection.cursor() as cursor:
            for sgtin in sgtins:
                cursor.execute(
                    """
                    EXEC insert_commshippercases_tempscan_data 
                        @barcode = %s, 
                        @identifier = %s, 
                        @sender_gln = %s, 
                        @receiver_gln = %s, 
                        @supplier_gln=%s,
                        @EventTime = %s,
                        @expiration_date=%s,
                        @mfg_date=%s,
                        @shp_prmt=%s,
                        @lot_no=%s,
                        @sgln_urn = %s,
                        @sgtin=%s
                    """,
                    [gtin, identifier, sender_gln, receiver_gln, supplier_gln,event_time_dt, expiry_date,
                     manufacturing_date, shipment_permit, lot_number, sgln_urn, sgtin]
                )

                cursor.execute("EXEC comm_shippercases_data_one @identifier = %s, @barcode = %s", [identifier, gtin])
                columns = [col[0] for col in cursor.description]
                fetched_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                results.extend(fetched_rows)

        return Response({"message": "Success", "comm_shipper_results": results}, status=status.HTTP_200_OK)

    

class CommShippercasesFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_CommShipperCasesScan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            comm_shipper_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'comm_shipper_scan_data': comm_shipper_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShipperCasesAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']

        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC comm_shippercases_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))

        if not result:
            return Response({"error": "No data found for given instance_id"}, status=404)

        # Take static values from the first row
        first_row = result[0]
        sender = first_row['SenderGLN']
        receiver = first_row['ReceiverGLN']
        event_time = first_row['EventTime']
        expiration_date = first_row['expiration_date']
        manufacturing_date = first_row['manufacturing_date']
        shipment_permit = first_row['shipment_permit']
        lot_number = first_row['lot_number']
        sgln = first_row['sgln']

        # Handle event time conversion to UTC
        if isinstance(event_time, datetime):
            if event_time.tzinfo is None:
                dubai_tz = pytz.timezone('Asia/Dubai')
                event_time = dubai_tz.localize(event_time)
            event_time_utc = event_time.astimezone(pytz.utc)
            event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        else:
            event_time_str = str(event_time)
        event_time_zone_offset = "+04:00"

        # Build epcList XML with all SGTINs
        epc_list_xml = ""
        for row in result:
            epc_list_xml += f"<epc>{row['sgtin']}</epc>\n"

        try:
            # Build the XML
            xml_body = f"""<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument 
                        schemaVersion="1.2" 
                        creationDate="{event_time_str}" 
                        xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" 
                        xmlns:epcis="urn:epcglobal:epcis:xsd:1" 
                        xmlns:cbvmda="urn:epcglobal:cbv:mda" 
                        xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender>
                                    <sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier>
                                </sbdh:Sender>
                                <sbdh:Receiver>
                                    <sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier>
                                </sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>

                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList>
                                        {epc_list_xml.strip()}
                                    </epcList>
                                    <action>ADD</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:commissioning</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:active</disposition>
                                    <readPoint>
                                        <id>{sgln}</id>
                                    </readPoint>
                                    <bizLocation>
                                        <id>{sgln}</id>
                                    </bizLocation>
                                    <extension>
                                        <ilmd>
                                            <cbvmda:lotNumber>{lot_number}</cbvmda:lotNumber>
                                            <cbvmda:itemExpirationDate>{expiration_date}</cbvmda:itemExpirationDate>
                                        </ilmd>
                                    </extension>
                                    <tatmeen:lotManufacturingDate>{manufacturing_date}</tatmeen:lotManufacturingDate>
                                    <tatmeen:manufacturingOrigin>I</tatmeen:manufacturingOrigin>
                                    <tatmeen:shipmentPermit>{shipment_permit}</tatmeen:shipmentPermit>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code)

            if response.status_code == 202:
                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")
                    with connection.cursor() as r:
                        r.execute("EXEC update_comm_shippercases_guid_map @identifier = %s", [instance_id])
                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempCommshippercasesScanDetails @identifier = %s", [instance_id])
                    with connection.cursor() as t:
                        t.execute("EXEC clear_comm_shippercases_temp_data @identifier = %s", [instance_id])

                    status_response = get_tatmeen_instance_status(instance_id)
                    message_status = status_response.get("messagestatus", "").strip()

                    if message_status == "S  - Successful":
                        with connection.cursor() as u:
                            u.execute("EXEC update_comm_shippercases_event @identifier = %s", [instance_id])
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A  - Technical Error":
                        with connection.cursor() as v:
                            v.execute("EXEC update_comm_shippercases_event_error @identifier = %s", [instance_id])
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        return Response({
                            "error": "No message status returned.",
                            "log": status_response.get("logList", [])
                        }, status=400)

                    else:
                        with connection.cursor() as w:
                            w.execute("EXEC update_comm_shippercases_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        }, status=400)

            else:
                send_shipper_cases_to_tatmeen.send(xml_body, token_data['access_token'])
                return Response({
                    "message": "Tatmeen API did not accept the request. Retry scheduled.",
                    "status_code": response.status_code,
                    "retry": True
                }, status=response.status_code)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

        return Response({"message": "success"})

############### Packing ###########

class Pack_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = pack_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.pk_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"PACK{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    pack_guid_map.objects.create(
                        pk_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class packingParentSSCCScanView(APIView):
    def post(self, request, *args, **kwargs):
        barcode_sscc = request.data.get('barcode_sscc', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        # supplier_gln = request.data.get('supplier_gln', '')
        
        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode_sscc.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        parent_sscc = match.group(1)
        print("---- parent sscc----",parent_sscc)
        
        matching_vendor = (
            vendor_master.objects.using('default')
            .filter(status=1)
            .order_by(-models.functions.Length('CompanyPrefix'))  # longest first
            .filter(CompanyPrefix__isnull=False)
        )
        print("----matching vendor ------")

        matched_vendor = None
        for vendor in matching_vendor:
            if parent_sscc[1:].startswith(vendor.CompanyPrefix):  # Skip extension digit
                matched_vendor = vendor
                break


        if not matched_vendor:
            return Response({"error": "No vendor found with a matching CompanyPrefix"}, status=status.HTTP_404_NOT_FOUND)

        supplier_gln = matched_vendor.GLN
        print("--------supplier gln ------",supplier_gln)

        
        obj_exists=TempParentSSCCPackingScanDetails.objects.filter(UUID=identifier,SSCC=parent_sscc).exists()
        
        if not obj_exists:
            TempParentSSCCPackingScanDetails.objects.create(
                UUID=identifier,
                SSCC=parent_sscc,
                SenderGLN=sender_gln,
                ReceiverGLN=receiver_gln,
                SupplierGLN=supplier_gln
            )
        input_data=TempParentSSCCPackingScanDetails.objects.filter(UUID=identifier).values('UUID','SSCC')
        if input_data.exists():
            return Response({"message":"Success",
                             "PackSscc_results":list(input_data),
                             "Sttaus":1
                             },status=status.HTTP_200_OK)
        else:
            return Response({"message": "No data found for given UUID"
            }, status=status.HTTP_404_NOT_FOUND)



class PackScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """
    def post(self, request, *args, **kwargs):
        barcode_sscc = request.data.get('barcode_sscc', '')
        barcode_sgtin = request.data.get('barcode_sgtin', '')
        identifier = request.data.get('identifier', '')
        event_time_str = request.data.get('event_time', '')

        obj=TempParentSSCCPackingScanDetails.objects.filter(UUID=identifier,SSCC=barcode_sscc,status=0).first()
        if not obj:
            return Response({"message":"Parent SSCC not found for the given identifier","Status":0},status=status.HTTP_404_NOT_FOUND)
        
        sender_gln=obj.SenderGLN
        receiver_gln=obj.ReceiverGLN
        supplier_gln=obj.SupplierGLN

        # # Clean the {GS} or ASCII 29 group separator
        # barcode_cleaned = barcode_sscc.replace('{GS}', '').replace(chr(29), '')

        # # Extract SSCC from Application Identifier (00)
        # match = re.search(r"00(\d{18})", barcode_cleaned)
        # if not match:
        #     return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        # sscc = match.group(1)

        # sgtin extraction
        barcode_sgtin = barcode_sgtin.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = barcode_sgtin.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        barcode_sgtin = barcode_sgtin[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, barcode_sgtin)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()

        # try:
        event_time_dt = (
            datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
            if event_time_str else None
        )
       

        # Generate SSCC URN and SGLN URN
        # try:
        sscc_urn = generate_sscc_urn(barcode_sscc, supplier_gln)
        print("====SSCC URN:", sscc_urn)
        sgln_urn = generate_sgln_urn(sender_gln)
        print("====SGLN URN:", sgln_urn)
        sgtin = generate_sgtin_from_gtin(gtin,ProductMaster,vendor_master)
        print("====SGTIN:", sgtin)
        # except ValueError as e:
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_packingsscc_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s,
                    @EventTime = %s,
                    @sscc_urn = %s,    
                    @sgln_urn = %s,
                    @gtin = %s,
                    @expiration_date = %s,
                    @batch_no = %s,
                    @sgtin = %s
                """,
                [barcode_sscc, identifier, sender_gln, receiver_gln, supplier_gln,event_time_dt,sscc_urn, sgln_urn, gtin, expiration_date, batch_number,sgtin]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC pack_sscc_data_one @identifier = %s, @barcode = %s", [identifier, barcode_sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"pack_results":results}, status=status.HTTP_200_OK)



class PackFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_packscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            pack_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'pack_scan_data': pack_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PackClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']
            
            with connection.cursor() as cursor:
                cursor.execute("EXEC clear_PackingScan_Parentdataone @identifier = %s", [identifier])


            cursor = connection.cursor()
            cursor.execute("EXEC clear_packscan_dataone @identifier = %s", [identifier])
           
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PackingSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC pack_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            sscc_urn= row['sscc_urn']      
            sgln = row['sgln']
            instance_id=row['UUID']
            sgtin = row['sgtin']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

           
            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
            <soap:Header/>
            <soap:Body>
                <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                <EPCISHeader>
                    <sbdh:StandardBusinessDocumentHeader>
                        <sbdh:HeaderVersion>1.0</sbdh:HeaderVersion>
                        <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                        <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                        <sbdh:DocumentIdentification>
                            <sbdh:Standard>EPCGlobal</sbdh:Standard>
                            <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                            <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                            <sbdh:Type>Events</sbdh:Type>
                            <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                        </sbdh:DocumentIdentification>
                    </sbdh:StandardBusinessDocumentHeader>
                </EPCISHeader>
                <EPCISBody>
                    <EventList>
                        <AggregationEvent>
                            <eventTime>{event_time_str}</eventTime>
                            <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                            <parentID>{sscc_urn}</parentID>
                            <childEPCs><epc>{sgtin}</epc></childEPCs>
                            <action>ADD</action>
                            <bizStep>urn:epcglobal:cbv:bizstep:packing</bizStep>
                            <readPoint><id>{sgln}</id></readPoint>
                            <bizLocation><id>{sgln}</id></bizLocation>
                        </AggregationEvent>
                    </EventList>
                </EPCISBody>
                </epcis:EPCISDocument>
            </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_pack_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempPackScanDetails @identifier = %s", [instance_id])
                        
                    
                    #change============================================================================
                    with connection.cursor() as q:
                        q.execute("EXEC usp_PackingScan_Parenttemp_data @identifier = %s", [instance_id])
                    #change============================================================================


                    with connection.cursor() as t:
                        t.execute("EXEC clear_pack_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_pack_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_pack_sscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        with connection.cursor() as w:
                            w.execute("EXEC update_pack_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_packing_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })




################  Decommissioning  ################

class Decommission_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = decommission_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.dcom_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"DC{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    decommission_guid_map.objects.create(
                        dcom_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DecommScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')
        reason_code = request.data.get('reason_code', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempDeCommSSCCScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_decomm_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s, 
                    @EventTime = %s,
                    @reason_code = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,reason_code,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC decomm_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"decomm_results":results}, status=status.HTTP_200_OK)
        

                
class DecommFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_decommscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            decomm_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'decomm_scan_data': decomm_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DecommissionSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC decomm_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            sscc_urn= row['sscc_urn']      
            reason_code = row['ReasonCode']
            sgln = row['sgln']
            instance_id=row['UUID']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"
           

            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.0</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList><epc>{sscc_urn}</epc></epcList>
                                    <action>DELETE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:decommissioning</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:damaged</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                    <tatmeen:reasonCode>{reason_code}</tatmeen:reasonCode>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>
            """

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_decomm_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempDecommScanDetails @identifier = %s", [instance_id])

                    with connection.cursor() as t:
                        t.execute("EXEC clear_decomm_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_decommissioning_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_decommissioning_sscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        with connection.cursor() as w:
                            w.execute("EXEC update_decommissioning_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_decommission_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})

            # except Exception as e:
            #     return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })



########### Stolen ##########

class Stolen_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = stolen_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.st_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"ST{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    stolen_guid_map.objects.create(
                        st_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class StolenScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempStolenScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_stolen_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC stolen_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"stolen_results":results}, status=status.HTTP_200_OK)
        

                
class StolenFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_stolenscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            stolen_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'stolen_scan_data': stolen_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class StolenSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC stolen_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            instance_id=row['UUID']
            sscc_urn = row['sscc_urn']
            sgln = row['sgln']
            
            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  
            event_time_zone_offset = "+04:00"

            # Build the XML
            
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.0</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList><epc>{sscc_urn}</epc></epcList>
                                    <action>DELETE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:decommissioning</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:stolen</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>
            """

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_stolen_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempStolenScanDetails @identifier = %s", [instance_id])

                    with connection.cursor() as t:
                        t.execute("EXEC clear_stolen_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======inn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_stolen_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_stolen_sscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        # with connection.cursor() as w:
                        #     w.execute("EXEC update_receiving_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_stolen_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})

            # except Exception as e:
            #     return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })


########### Exported ##########                
class ExportedFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_exportedscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            expt_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'expt_scan_data': expt_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

##### dispense sscc #####

class Dispense_GenerateIdentifierView_SSCC(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = dispense_guid_sscc.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.dsscc_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"DSSCC{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    dispense_guid_sscc.objects.create(
                        dsscc_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DispenseScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """
    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        # supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')
        lot_number= request.data.get('lot_number', '')
        expiry_date = request.data.get('expiry_date', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)


        matching_vendor = (
            vendor_master.objects.using('default')
            .filter(status=1)
            .order_by(-models.functions.Length('CompanyPrefix'))  # longest first
            .filter(CompanyPrefix__isnull=False)
        )
        print("----matching vendor ------")

        matched_vendor = None
        for vendor in matching_vendor:
            if sscc[1:].startswith(vendor.CompanyPrefix):  # Skip extension digit
                matched_vendor = vendor
                break


        if not matched_vendor:
            return Response({"error": "No vendor found with a matching CompanyPrefix"}, status=status.HTTP_404_NOT_FOUND)

        supplier_gln = matched_vendor.GLN
        print("--------supplier gln ------",supplier_gln)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempDispenseSSCCScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_dispensesscc_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s,
                    @lot_number = %s,
                    @expiry_date = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,sscc_urn, sgln_urn, lot_number, expiry_date]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC dispensesscc_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"dispense_sscc_results":results}, status=status.HTTP_200_OK)
        

                
class DispenseFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_DispenseSSCC_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            dis_sscc_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'dis_sscc_scan_data': dis_sscc_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DispenseSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC dispensesscc_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            instance_id = row['UUID']
            sscc_urn = row['sscc_urn']
            sgln=row['sgln']
            lot_number=row['lot_number']
            expiry_date=row['expiry_date']
            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"
            

            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader"
                        xmlns:epcis="urn:epcglobal:epcis:xsd:1"
                        xmlns:cbvmda="urn:epcglobal:cbv:mda"
                        xmlns:tatmeen="http://tatmeen.ae/epcis/"
                        schemaVersion="1.2" creationDate="{event_time_str}">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList><epc>{sscc_urn}</epc></epcList>
                                    <action>OBSERVE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:retail_selling</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:retail_sold</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                    <cbvmda:lotNumber>{lot_number}</cbvmda:lotNumber>
                                    <cbvmda:itemExpirationDate>{expiry_date}</cbvmda:itemExpirationDate>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/Dispensation',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_dispense_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempDispenseSSCCScanDetails @identifier = %s", [instance_id])

                    with connection.cursor() as t:
                        t.execute("EXEC clear_dis_sscc_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)
                    
                   
                        # You might even want to log the raw, problematic status here for future reference

                    message_status = status_response.get("messagestatus","").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_dispense_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_dispense_sscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        # with connection.cursor() as w:
                        #     w.execute("EXEC update_receiving_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_dispensed_sscc_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})

            # except Exception as e:
            #     return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })



######## dispense sgtin ########

class Dispense_GenerateIdentifierView_SGTIN(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = dispense_guid_sgtin.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.dsgtin_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"DSGTIN{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    dispense_guid_sgtin.objects.create(
                        dsgtin_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DispenseScanSGTINView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """
    def post(self, request, *args, **kwargs):
        raw_data = request.data.get('parent_gtin', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender', '')
        receiver_gln = request.data.get('receiver', '')
        event_time_str = request.data.get('event_time', '')
        lot_number= request.data.get('lot_number', '')
        expiry_date = request.data.get('expiry_date', '')


        print("Raw scanned input:", repr(raw_data))  # Safe print

        # Strip ASCII 29 (FNC1) if present
        raw_data = raw_data.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = raw_data.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        raw_data = raw_data[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, raw_data)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()

        print("Extracted GTIN:", gtin)
        print("Extracted Expiration Date:", expiration_date)
        print("Extracted Batch Number:", batch_number)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        # Generate SSCC URN and SGLN URN
        try:
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)

     
            sgtin = generate_sgtin_from_gtin(gtin, ProductMaster, vendor_master)
   

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_dispensesgtin_tempscan_data 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @EventTime = %s,
                    @barcode=%s,
                    @sgtin=%s,
                    @sgln_urn = %s,
                    @lot_number = %s,
                    @expiry_date = %s
                """,
                [identifier, sender_gln, receiver_gln, event_time_dt,gtin,sgtin,sgln_urn, lot_number, expiry_date]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC dispensesgtin_data_one @identifier = %s, @barcode = %s", [identifier, gtin])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"dispense_sgtin_results":results}, status=status.HTTP_200_OK)
        

                
class DispenseSGTINFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_dispensesgtinscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            dis_sgtin_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'dis_sgtin_scan_data': dis_sgtin_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DispenseSGTINAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC dispensesgtin_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            instance_id = row['UUID']
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            sgtin=row['sgtin']
            sgln=row['sgln']
            lot_number=row['lot_number']
            expiry_date=row['expiry_date']
            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"
            
            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader"
                        xmlns:epcis="urn:epcglobal:epcis:xsd:1"
                        xmlns:cbvmda="urn:epcglobal:cbv:mda"
                        xmlns:tatmeen="http://tatmeen.ae/epcis/"
                        schemaVersion="1.2" creationDate="{event_time_str}">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList><epc>{sgtin}</epc></epcList>
                                    <action>OBSERVE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:retail_selling</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:retail_sold</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                    <cbvmda:lotNumber>{lot_number}</cbvmda:lotNumber>
                                    <cbvmda:itemExpirationDate>{expiry_date}</cbvmda:itemExpirationDate>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/Dispensation',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_dispensesgtin_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempDispenseSGTINScanDetails @identifier = %s", [instance_id])

                    with connection.cursor() as t:
                        t.execute("EXEC clear_dis_sgtin_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)
                    
                   
                    # You might even want to log the raw, problematic status here for future reference

                    message_status = status_response.get("messagestatus","").strip()
                    print("======in receiving message status=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_dispense_sgtin_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_dispense_sgtin_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        # with connection.cursor() as w:
                        #     w.execute("EXEC update_receiving_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_dispensed_sgtin_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})

            # except Exception as e:
            #     return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })


#### Return Receiving ######

class ReturnRec_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = return_rec_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.rr_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"REC{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    return_rec_guid_map.objects.create(
                        rr_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RetRecScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempReturnReceiveScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_returnreceiving_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, event_time_dt,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC returnreceiving_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"retrec_results":results}, status=status.HTTP_200_OK)
        
                
class ReturnReceivingFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_ret_rec_scan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            ret_rec_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'ret_rec_scan_data': ret_rec_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReturnReceivingAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data.get('instance_id')
        
        if not instance_id:
            return Response({"error": "Missing 'instance_id' in request."}, status=400)

        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC ret_rec_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))

        if not result:
            return Response({"error": "No records found for the given instance_id."}, status=404)

       
        for row in result:
           
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            instance_id = row['UUID']
            sscc_urn = row['sscc_urn']
            sgln = row['sgln']
            
            if isinstance(event_time, datetime):
            # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

            # Build XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <ObjectEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <epcList><epc>{sscc_urn}</epc></epcList>
                                    <action>OBSERVE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:receiving</bizStep>
                                    <disposition>urn:epcglobal:cbv:disp:returned</disposition>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                    <bizTransactionList>
                                        <bizTransaction type="urn:epcglobal:cbv:btt:desadv">urn:epcglobal:cbv:bt:xxxxxxxx00000:TSTOBD001</bizTransaction>
                                    </bizTransactionList>
                                </ObjectEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_ret_rec_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempRetRecScanDetails @identifier = %s", [instance_id])

                    with connection.cursor() as t:
                        t.execute("EXEC clear_ret_rec_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)
                    
                
                        # You might even want to log the raw, problematic status here for future reference

                    message_status = status_response.get("messagestatus","").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_ret_rec_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_ret_rec_sscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        with connection.cursor() as w:
                            w.execute("EXEC update_receiving_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_return_receiving_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})

            # except Exception as e:
            #     return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })




######## return shipping ########

class ReturnShip_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = return_shipping_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.rs_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"RSHIP{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    return_shipping_guid_map.objects.create(
                        rs_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReturnShippingScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        destination_gln=request.data.get('destination_gln')
        event_time_str = request.data.get('event_time', '')
        reason_code = request.data.get('reason_code', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempReturnShippingScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
            des_sgln_urn=generate_destination_sgln_urn(destination_gln)
            print("====Destination SGLN URN:", des_sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_return_shippingsscc_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s,
                    @destination_gln = %s, 
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s,
                    @des_sgln_urn = %s,
                    @reason_code = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln,destination_gln, event_time_dt,sscc_urn, sgln_urn,des_sgln_urn,reason_code]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC returnship_sscc_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"return_ship_results":results}, status=status.HTTP_200_OK)
        

                
class ReturnShipppingFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_retshipscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            ret_ship_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'ret_ship_scan_data': ret_ship_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class ReturnShippingAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC ret_ship_sscc_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))

        xml_bodies = []

        for row in result:
            sender= row['SenderGLN']
            receiver = row['ReceiverGLN']
            sscc_urn = row['sscc_urn']
            sender_sgln = row['sgln']
            destination_sgln = row['destination_sgln']
            event_time = row['EventTime']
            reason_code = row['reason_code']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

            try:
                

                # Build the XML
                xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
                <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                    <soap:Header/>
                    <soap:Body>
                        <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                            <EPCISHeader>
                                <sbdh:StandardBusinessDocumentHeader>
                                    <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                    <sbdh:Sender>
                                        <sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier>
                                    </sbdh:Sender>
                                    <sbdh:Receiver>
                                        <sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier>
                                    </sbdh:Receiver>
                                    <sbdh:DocumentIdentification>
                                        <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                        <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                        <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                        <sbdh:Type>Events</sbdh:Type>
                                        <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                    </sbdh:DocumentIdentification>
                                </sbdh:StandardBusinessDocumentHeader>
                            </EPCISHeader>
                            <EPCISBody>
                                <EventList>
                                    <ObjectEvent>
                                        <eventTime>{event_time_str}</eventTime>
                                        <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                        <epcList>
                                            <epc>{sscc_urn}</epc>
                                        </epcList>
                                        <action>OBSERVE</action>
                                        <bizStep>urn:epcglobal:cbv:bizstep:shipping</bizStep>
                                        <disposition>urn:epcglobal:cbv:disp:returned</disposition>
                                        <readPoint>
                                            <id>{sender_sgln}</id>
                                        </readPoint>
                                        <bizLocation>
                                            <id>{sender_sgln}</id>
                                        </bizLocation>
                                        <bizTransactionList>
                                            <bizTransaction type="urn:epcglobal:cbv:btt:desadv">urn:epcglobal:cbv:bt:{sender}:TSTOBD001</bizTransaction>
                                        </bizTransactionList>
                                        <extension>
                                            <sourceList>
                                                <source type="urn:epcglobal:cbv:sdt:owning_party">{sender_sgln}</source>
                                                <source type="urn:epcglobal:cbv:sdt:location">{sender_sgln}</source>
                                            </sourceList>
                                            <destinationList>
                                                <destination type="urn:epcglobal:cbv:sdt:owning_party">{destination_sgln}</destination>
                                                <destination type="urn:epcglobal:cbv:sdt:location">{destination_sgln}</destination>
                                            </destinationList>
                                        </extension>
                                        <tatmeen:reasonCode>{reason_code}</tatmeen:reasonCode>
                                    </ObjectEvent>
                                </EventList>
                            </EPCISBody>
                        </epcis:EPCISDocument>
                    </soap:Body>
                </soap:Envelope>"""

                xml_bodies.append(xml_body)

                token_data = get_valid_token()
                headers = {
                    "Authorization": f"Bearer {token_data['access_token']}",
                    "apikey": settings.TATMEEN_API_KEY,
                    "Content-Type": "application/soap+xml; charset=utf-8"
                }

                response = requests.post(
                    'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                    data=xml_body,
                    headers=headers
                )
                print("SendEPCIS Status Code:", response.status_code) 

                if response.status_code==202:

                    root = ET.fromstring(response.text)
                    ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                    code_elem = root.find('.//code')

                    if code_elem is not None and code_elem.text == '202':
                        print("--------incoming---------")

                        # Execute DB procedures inside context managers
                        with connection.cursor() as r:
                            r.execute("EXEC update_ret_ship_sscc_guid_map @identifier = %s", [instance_id])

                        with connection.cursor() as s:
                            s.execute("EXEC usp_DumpTempRetShipssccScanDetails @identifier = %s", [instance_id])

                        with connection.cursor() as t:
                            t.execute("EXEC clear_ret_ship_temp_data @identifier = %s", [instance_id])

                        #message status
                        status_response = get_tatmeen_instance_status(instance_id)

                        message_status = status_response.get("messagestatus", "").strip()

                        if message_status == "S  - Successful":
                            print("========message success=======")
                            with connection.cursor() as u:
                                u.execute("EXEC update_ret_ship_sscc_event @identifier = %s", [instance_id])
                                print("=====status updated 1=====")
                            return Response({"log": status_response.get("logList", [])})

                        elif message_status == "A  - Technical Error":
                            print("========technical error=======")
                            with connection.cursor() as v:
                                v.execute("EXEC update_ret_ship_sscc_event_error @identifier = %s", [instance_id])
                                print("=====status updated 2=====")
                            return Response({"log": status_response.get("logList", [])})

                        elif message_status == "":
                            print("========no status returned=======")
                            return Response({
                                "error": "No message status returned. The instance might not exist or failed to process.",
                                "log": status_response.get("logList", [])
                            }, status=400)

                        else:
                            print(f"========unexpected status: {message_status}=======")
                            # Optional: Log this for further analysis
                            with connection.cursor() as w:
                                w.execute("EXEC update_ret_ship_sscc_event_unknown @identifier = %s", [instance_id])
                            return Response({
                                "error": f"Unhandled message status: {message_status}",
                                "log": status_response.get("logList", [])
                            }, status=400)
                
                elif response.status_code!=202:
                    send_return_shipping_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True}, status=response.status_code)

            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })



######### commission aggregation SSCC -- SGTIN  #########

class Commission_aggregation_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = commision_guid_aggregation.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.cma_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"CA{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    commision_guid_aggregation.objects.create(
                        cma_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommAggParentSSCCScanView(APIView):
    def post(self, request, *args, **kwargs):
        barcode_sscc = request.data.get('barcode_sscc', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        
        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode_sscc.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        parent_sscc = match.group(1)
        print("---- parent sscc----",parent_sscc)
        
        # matching_vendor = (
        #     vendor_master.objects.using('default')
        #     .filter(status=1)
        #     .order_by(-models.functions.Length('CompanyPrefix'))  # longest first
        #     .filter(CompanyPrefix__isnull=False)
        # )
        # print("----matching vendor ------")

        # matched_vendor = None
        # for vendor in matching_vendor:
        #     if parent_sscc[1:].startswith(vendor.CompanyPrefix):  # Skip extension digit
        #         matched_vendor = vendor
        #         break


        # if not matched_vendor:
        #     return Response({"error": "No vendor found with a matching CompanyPrefix"}, status=status.HTTP_404_NOT_FOUND)

        # supplier_gln = matched_vendor.GLN
        # print("--------supplier gln ------",supplier_gln)

        
        obj_exists=TempParentSSCCCommAggregationCPScanDetails.objects.filter(UUID=identifier,SSCC=parent_sscc).exists()
        
        if not obj_exists:
            TempParentSSCCCommAggregationCPScanDetails.objects.create(
                UUID=identifier,
                SSCC=parent_sscc,
                SenderGLN=sender_gln,
                ReceiverGLN=receiver_gln,
                SupplierGLN=supplier_gln
            )
        input_data=TempParentSSCCCommAggregationCPScanDetails.objects.filter(UUID=identifier).values('UUID','SSCC')
        if input_data.exists():
            return Response({"message":"Success",
                             "commAggregation_results":list(input_data),
                             "Sttaus":1
                             },status=status.HTTP_200_OK)
        else:
            return Response({"message": "No data found for given UUID"
            }, status=status.HTTP_404_NOT_FOUND)




class CommAggregationScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """
    def post(self, request, *args, **kwargs):
        barcode_sscc = request.data.get('barcode_sscc', '')
        barcode_sgtin = request.data.get('barcode_sgtin', '')
        identifier = request.data.get('identifier', '')
        event_time_str = request.data.get('event_time', '')
        
        obj=TempParentSSCCCommAggregationCPScanDetails.objects.filter(UUID=identifier,SSCC=barcode_sscc,status=0).first()
        
        if not obj:
            return Response({"message":"Parent SSCC not found for the given identifier","Status":0},status=status.HTTP_404_NOT_FOUND)
        
        sender_gln=obj.SenderGLN
        receiver_gln=obj.ReceiverGLN
        supplier_gln=obj.SupplierGLN
            
        # # sgtin extraction
        barcode_sgtin = barcode_sgtin.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = barcode_sgtin.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        barcode_sgtin = barcode_sgtin[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, barcode_sgtin)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()

        # try:
        event_time_dt = (
            datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
            if event_time_str else None
        )
       

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(barcode_sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
            sgtin = generate_sgtin_from_gtin(gtin,ProductMaster,vendor_master)
            print("====SGTIN:", sgtin)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_commAggregation_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s,
                    @EventTime = %s,
                    @sscc_urn = %s,    
                    @sgln_urn = %s,
                    @gtin = %s,
                    @expiration_date = %s,
                    @batch_no = %s,
                    @sgtin = %s
                """,
                [barcode_sscc, identifier, sender_gln, receiver_gln, supplier_gln,event_time_dt,sscc_urn, sgln_urn,gtin,expiration_date,batch_number,sgtin]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC commAggregation_sscc_data_one @identifier = %s, @barcode = %s", [identifier, barcode_sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":1,"commAggregation_results":results}, status=status.HTTP_200_OK)

        

class CommAggregationFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_CommAggregationScan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            CommAggregation_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'CommAggregation_scan_data': CommAggregation_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CommAggregationClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']
            
            with connection.cursor() as cursor:
                cursor.execute("EXEC clear_CommAggregationScan_Parentdataone @identifier = %s", [identifier])

            cursor = connection.cursor()
            cursor.execute("EXEC clear_CommAggregationScan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AggregationCaseIntoPalletAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC CommAggregation_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            sscc_urn= row['sscc_urn']      
            sgln = row['sgln']
            instance_id=row['UUID']
            sgtin = row['sgtin']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

           
            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <AggregationEvent>
                                    <!-- AGGREGATION OF CASE INTO A PALLET -->
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <parentID>{sscc_urn}</parentID>
                                    <childEPCs><epc>{sgtin}</epc></childEPCs>
                                    <action>ADD</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:packing</bizStep>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                </AggregationEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_CommAggregation_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempCommAggregationScanDetails @identifier = %s", [instance_id])

                    #change============================================================================
                    with connection.cursor() as q:
                        q.execute("EXEC usp_CommAggregationScan_Parenttemp_data @identifier = %s", [instance_id])
                    #change============================================================================

                    with connection.cursor() as t:
                        t.execute("EXEC clear_CommAggregation_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_CommAggregation_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_CommAggregation_sscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        # with connection.cursor() as w:
                        #     w.execute("EXEC update_receiving_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_case_into_pallet_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })


                


######## Unpack #######

class Unpack_SSCC_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = unpack_guid_sscc.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.usscc_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"USSCC{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    unpack_guid_sscc.objects.create(
                        usscc_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DisAggCSfromSSCCParentSSCCScanView(APIView):
    def post(self, request, *args, **kwargs):
        barcode_sscc = request.data.get('barcode_sscc', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        # supplier_gln = request.data.get('supplier_gln', '')
        
        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode_sscc.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        parent_sscc = match.group(1)
        print("---- parent sscc----",parent_sscc)
        
        matching_vendor = (
            vendor_master.objects.using('default')
            .filter(status=1)
            .order_by(-models.functions.Length('CompanyPrefix'))  # longest first
            .filter(CompanyPrefix__isnull=False)
        )
        print("----matching vendor ------")

        matched_vendor = None
        for vendor in matching_vendor:
            if parent_sscc[1:].startswith(vendor.CompanyPrefix):  # Skip extension digit
                matched_vendor = vendor
                break


        if not matched_vendor:
            return Response({"error": "No vendor found with a matching CompanyPrefix"}, status=status.HTTP_404_NOT_FOUND)

        supplier_gln = matched_vendor.GLN
        print("--------supplier gln ------",supplier_gln)

        
        obj_exists=TempParentDisAggCSfromSSCCScanDetails.objects.filter(UUID=identifier,SSCC=parent_sscc).exists()
        
        if not obj_exists:
            TempParentDisAggCSfromSSCCScanDetails.objects.create(
                UUID=identifier,
                SSCC=parent_sscc,
                SenderGLN=sender_gln,
                ReceiverGLN=receiver_gln,
                SupplierGLN=supplier_gln
            )
        input_data=TempParentDisAggCSfromSSCCScanDetails.objects.filter(UUID=identifier).values('UUID','SSCC')
        if input_data.exists():
            return Response({"message":"Success",
                             "commAggregation_results":list(input_data),
                             "Sttaus":1
                             },status=status.HTTP_200_OK)
        else:
            return Response({"message": "No data found for given UUID"
            }, status=status.HTTP_404_NOT_FOUND)



class DisAggCSfromSSCCScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode_sscc = request.data.get('barcode_sscc', '')
        barcode_sgtin = request.data.get('barcode_sgtin', '')
        identifier = request.data.get('identifier', '')
        event_time_str = request.data.get('event_time', '')


        obj=TempParentDisAggCSfromSSCCScanDetails.objects.filter(UUID=identifier,SSCC=barcode_sscc,status=0).first()
        
        if not obj:
            return Response({"message":"Parent SSCC not found for the given identifier","Status":0},status=status.HTTP_404_NOT_FOUND)
        
        
        sender_gln=obj.SenderGLN
        receiver_gln=obj.ReceiverGLN
        supplier_gln=obj.SupplierGLN

        
        # Clean the {GS} or ASCII 29 group separator
        # barcode_cleaned = barcode_sscc.replace('{GS}', '').replace(chr(29), '')

        # # Extract SSCC from Application Identifier (00)
        # match = re.search(r"00(\d{18})", barcode_cleaned)
        # if not match:
        #     return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        # sscc = match.group(1)

        # sgtin extraction
        barcode_sgtin = barcode_sgtin.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = barcode_sgtin.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        barcode_sgtin = barcode_sgtin[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, barcode_sgtin)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(barcode_sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
            sgtin = generate_sgtin_from_gtin(gtin,ProductMaster,vendor_master)
            print("====SGTIN:", sgtin)
            
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_disaggcsfromsscc_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s,
                    @EventTime = %s,
                    @sscc_urn = %s,    
                    @sgln_urn = %s,
                    @gtin = %s,
                    @sgtin = %s
                """,
                [barcode_sscc, identifier, sender_gln, receiver_gln, supplier_gln,event_time_dt,sscc_urn, sgln_urn, gtin,sgtin]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC disaggcsfromsscc_data_one @identifier = %s, @barcode = %s", [identifier, barcode_sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"disaggcsfromsscc_results":results}, status=status.HTTP_200_OK)


class DisAggCSfromSSCCFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_disaggcsfromsscc_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            disaggcsfromsscc_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'disaggcsfromsscc_scan_data': disaggcsfromsscc_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DisAggCSfromSSCCClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            with connection.cursor() as cursor:
                cursor.execute("EXEC clear_DisAggCSfromSSCCScan_Parentdataone @identifier = %s", [identifier])

            cursor = connection.cursor()
            cursor.execute("EXEC clear_disaggcsfromsscc_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
			
class DisaggregationCSfromSSCCAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC disaggcsfromsscc_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            sscc_urn= row['sscc_urn']      
            sgln = row['sgln']
            instance_id=row['UUID']
            sgtin = row['sgtin']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

           
            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <AggregationEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <parentID>{sscc_urn}</parentID>
                                    <childEPCs><epc>{sgtin}</epc></childEPCs>
                                    <action>DELETE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:unpacking</bizStep>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                </AggregationEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_disaggcsfromsscc_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DisAggCSfromSSCCScan_Parenttemp_data @identifier = %s", [instance_id])

                    #change============================================================================
                    with connection.cursor() as q:
                        q.execute("EXEC usp_CommAggregationScan_Parenttemp_data @identifier = %s", [instance_id])
                    #change============================================================================

                    
                    with connection.cursor() as t:
                        t.execute("EXEC clear_disaggcsfromsscc_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_disaggcsfromsscc_sscc_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_disaggcsfromsscc_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        # with connection.cursor() as w:
                        #     w.execute("EXEC update_receiving_sscc_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_disaggregation_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })



### Shipping cancellation ###

class ShippingCancel_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = shipping_cancel_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.sc_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"SC{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    shipping_cancel_guid_map.objects.create(
                        sc_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ShippingCancelScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempShippingCancellationScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        with connection.cursor() as cursor:
            cursor.execute("EXEC get_shipping_data'" + str(sscc) + "'")
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        if result:
                instance_identifier_reference = result[0]["instance_identifier_reference"]
        else:
            raise ValueError("No data returned for the given SSCC code")
        
        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_shippingcancelsscc_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s,
                    @ref_identifier=%s,
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, instance_identifier_reference,event_time_dt,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC ship_calcel_sscc_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"cancel_ship_results":results}, status=status.HTTP_200_OK)
        

                
class ShipppingCancelFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_ship_cancelscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            ship_cancel_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'ship_cancel_scan_data': ship_cancel_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class ShippingCancellationAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC ship_cancel_sscc_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            sscc_urn = row['sscc_urn']
            sgln = row['sgln']
            reference_identifier=row['ShippingReference']
            event_time = row['EventTime']
            
            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

            try:

                # Build the XML
                xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
                <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                    <soap:Header/>
                    <soap:Body>
                        <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                            <EPCISHeader>
                                <sbdh:StandardBusinessDocumentHeader>
                                    <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                    <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                    <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                    <sbdh:DocumentIdentification>
                                        <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                        <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                        <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                        <sbdh:Type>Events</sbdh:Type>
                                        <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                    </sbdh:DocumentIdentification>
                                </sbdh:StandardBusinessDocumentHeader>
                            </EPCISHeader>
                            <EPCISBody>
                                <EventList>
                                    <ObjectEvent>
                                        <eventTime>{event_time_str}</eventTime>
                                        <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                        <epcList>
                                            <epc>{sscc_urn}</epc>
                                        </epcList>
                                        <action>OBSERVE</action>
                                        <bizStep>urn:epcglobal:cbv:bizstep:void_shipping</bizStep>
                                        <disposition>urn:epcglobal:cbv:disp:in_progress</disposition>
                                        <readPoint>
                                            <id>{sgln}</id>
                                        </readPoint>
                                        <bizLocation>
                                            <id>{sgln}</id>
                                        </bizLocation>
                                        <tatmeen:instanceIdentifierReference xmlns:tatmeen="https://tatmeen.ae/epcis/">{reference_identifier}</tatmeen:instanceIdentifierReference>
                                    </ObjectEvent>
                                </EventList>
                            </EPCISBody>
                        </epcis:EPCISDocument>
                    </soap:Body>
                </soap:Envelope>"""

                xml_bodies.append(xml_body)

                token_data = get_valid_token()
                headers = {
                    "Authorization": f"Bearer {token_data['access_token']}",
                    "apikey": settings.TATMEEN_API_KEY,
                    "Content-Type": "application/soap+xml; charset=utf-8"
                }

                response = requests.post(
                    'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
                    data=xml_body,
                    headers=headers
                )
                print("SendEPCIS Status Code:", response.status_code) 

                if response.status_code==202:

                    root = ET.fromstring(response.text)
                    ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                    code_elem = root.find('.//code')

                    if code_elem is not None and code_elem.text == '202':
                        print("--------incoming---------")

                        # Execute DB procedures inside context managers
                        with connection.cursor() as r:
                            r.execute("EXEC update_ship_cancel_sscc_guid_map @identifier = %s", [instance_id])

                        with connection.cursor() as s:
                            s.execute("EXEC usp_DumpTempShipCancelssccScanDetails @identifier = %s", [instance_id])

                        with connection.cursor() as t:
                            t.execute("EXEC clear_ship_cancel_sscc_temp_data @identifier = %s", [instance_id])

                        #message status
                        status_response = get_tatmeen_instance_status(instance_id)

                        message_status = status_response.get("messagestatus", "").strip()

                        if message_status == "S  - Successful":
                            print("========message success=======")
                            with connection.cursor() as u:
                                u.execute("EXEC update_ship_cancel_sscc_event @identifier = %s", [instance_id])
                                print("=====status updated 1=====")
                            return Response({"log": status_response.get("logList", [])})

                        elif "Technical Error" in message_status:
                            print("========technical error=======")
                            with connection.cursor() as v:
                                v.execute("EXEC update_ship_cancel_sscc_event_error @identifier = %s", [instance_id])
                                print("=====status updated 2=====")
                            return Response({"log": status_response.get("logList", [])})

                        elif message_status == "":
                            print("========no status returned=======")
                            return Response({
                                "error": "No message status returned. The instance might not exist or failed to process.",
                                "log": status_response.get("logList", [])
                            }, status=400)

                        else:
                            print(f"========unexpected status: {message_status}=======")
                            # Optional: Log this for further analysis
                            with connection.cursor() as w:
                                w.execute("EXEC update_ship_cancel_sscc_event_unknown @identifier = %s", [instance_id])
                            return Response({
                                "error": f"Unhandled message status: {message_status}",
                                "log": status_response.get("logList", [])
                            }, status=400)
                
                elif response.status_code!=202:
                    send_shippingcancellation_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True}, status=response.status_code)

            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })



### return shipping cancellation ###

class ReturnShippingCancellation_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = return_shipping_cancel_guid.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.rsc_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"RSC{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    return_shipping_cancel_guid.objects.create(
                        rsc_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReturnShippingCancelScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempReturnShippingCancelScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        with connection.cursor() as cursor:
            cursor.execute("EXEC get_return_shipping_data'" + str(sscc) + "'")
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        if result:
                instance_identifier_reference = result[0]["instance_identifier_reference"]
        else:
            return Response({"error":"No data returned for the given SSCC code"})
        
        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_returnshippingcancelsscc_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s,
                    @ref_identifier=%s,
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, instance_identifier_reference,event_time_dt,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC return_ship_cancel_sscc_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"returnshipcancel_results":results}, status=status.HTTP_200_OK)
        

                
class ReturnShipppingCancelFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_return_ship_cancelscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            returnship_cancel_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'returnship_cancel_scan_data': returnship_cancel_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class ReturnShippingCancellationAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC returnshipcancel_sscc_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            sscc_urn = row['sscc_urn']
            sgln = row['sgln']
            reference_identifier=row['ReferenceIdentifier']
            event_time = row['EventTime']
            
            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

            try:

                # Build the XML
                xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
                <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                    <soap:Header/>
                    <soap:Body>
                        <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                            <EPCISHeader>
                                <sbdh:StandardBusinessDocumentHeader>
                                    <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                    <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                    <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                    <sbdh:DocumentIdentification>
                                        <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                        <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                        <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                        <sbdh:Type>Events</sbdh:Type>
                                        <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                    </sbdh:DocumentIdentification>
                                </sbdh:StandardBusinessDocumentHeader>
                            </EPCISHeader>
                            <EPCISBody>
                                <EventList>
                                    <ObjectEvent>
                                        <eventTime>{event_time_str}</eventTime>
                                        <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                        <epcList><epc>{sscc_urn}</epc></epcList>
                                        <action>OBSERVE</action>
                                        <bizStep>urn:epcglobal:cbv:bizstep:void_shipping</bizStep>
                                        <disposition>urn:epcglobal:cbv:disp:returned</disposition>
                                        <readPoint><id>{sgln}</id></readPoint>
                                        <bizLocation><id>{sgln}</id></bizLocation>
                                        <tatmeen:instanceIdentifierReference>{reference_identifier}</tatmeen:instanceIdentifierReference>
                                    </ObjectEvent>
                                </EventList>
                            </EPCISBody>
                        </epcis:EPCISDocument>
                    </soap:Body>
                </soap:Envelope>"""

                xml_bodies.append(xml_body)

                token_data = get_valid_token()
                headers = {
                    "Authorization": f"Bearer {token_data['access_token']}",
                    "apikey": settings.TATMEEN_API_KEY,
                    "Content-Type": "application/soap+xml; charset=utf-8"
                }

                response = requests.post(
                    'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
                    data=xml_body,
                    headers=headers
                )
                print("SendEPCIS Status Code:", response.status_code) 

                if response.status_code==202:

                    root = ET.fromstring(response.text)
                    ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                    code_elem = root.find('.//code')

                    if code_elem is not None and code_elem.text == '202':
                        print("--------incoming---------")

                        # Execute DB procedures inside context managers
                        with connection.cursor() as r:
                            r.execute("EXEC update_returnship_cancel_sscc_guid_map @identifier = %s", [instance_id])

                        with connection.cursor() as s:
                            s.execute("EXEC usp_DumpTempReturnShipCancelScanDetails @identifier = %s", [instance_id])

                        with connection.cursor() as t:
                            t.execute("EXEC clear_returnshipcancel_sscc_temp_data @identifier = %s", [instance_id])

                        #message status
                        status_response = get_tatmeen_instance_status(instance_id)

                        message_status = status_response.get("messagestatus", "").strip()

                        if message_status == "S  - Successful":
                            print("========message success=======")
                            with connection.cursor() as u:
                                u.execute("EXEC update_returnship_cancel_sscc_event @identifier = %s", [instance_id])
                                print("=====status updated 1=====")
                            return Response({"log": status_response.get("logList", [])})

                        elif "Technical Error" in message_status: 
                            print("========technical error=======")
                            with connection.cursor() as v:
                                v.execute("EXEC update_returnship_cancel_sscc_event_error @identifier = %s", [instance_id])
                                print("=====status updated 2=====")
                            return Response({"log": status_response.get("logList", [])})

                        elif message_status == "":
                            print("========no status returned=======")
                            return Response({
                                "error": "No message status returned. The instance might not exist or failed to process.",
                                "log": status_response.get("logList", [])
                            }, status=400)

                        else:
                            print(f"========unexpected status: {message_status}=======")
                            # Optional: Log this for further analysis
                            with connection.cursor() as w:
                                w.execute("EXEC update_returnshipcancel_sscc_event_unknown @identifier = %s", [instance_id])
                            return Response({
                                "error": f"Unhandled message status: {message_status}",
                                "log": status_response.get("logList", [])
                            }, status=400)
                
                elif response.status_code!=202:
                    send_returnshippingcancellation_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True}, status=response.status_code)

            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })


### Return Receiving Cancellation ###

class ReturnRecCancel_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = return_rec_cancel_guid_map.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.rrc_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"REC{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    return_rec_cancel_guid_map.objects.create(
                        rrc_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ReturnReceiveCancelScanSSCCView(APIView):
    """
    API View to scan and parse SSCC barcode.
    """

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        event_time_str = request.data.get('event_time', '')

        # Clean the {GS} or ASCII 29 group separator
        barcode_cleaned = barcode.replace('{GS}', '').replace(chr(29), '')

        # Extract SSCC from Application Identifier (00)
        match = re.search(r"00(\d{18})", barcode_cleaned)
        if not match:
            return Response({"error": "Invalid SSCC format"}, status=status.HTTP_400_BAD_REQUEST)

        sscc = match.group(1)

        try:
            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        f"Invalid event_time format: '{event_time_str}'. "
                        "Expected 'YYYY-MM-DD HH:MM:SS'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if TempReturnReceiveCancellationScanDetails.objects.filter(UUID=identifier, SSCC=sscc, rec_status=0).exists():
            return Response({
                "error": "This SSCC has already been scanned with this identifier and is still pending.",
                "identifier": identifier,
                "sscc": sscc
            })

        # Generate SSCC URN and SGLN URN
        try:
            sscc_urn = generate_sscc_urn(sscc, supplier_gln)
            print("====SSCC URN:", sscc_urn)
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        with connection.cursor() as cursor:
            cursor.execute("EXEC get_return_receiving_data'" + str(sscc) + "'")
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        print("===result===",result)
            
        if result:
                instance_identifier_reference = result[0]["instance_identifier_reference"]
                print("====instance_identifier_reference===",instance_identifier_reference)
        else:
            return Response({"error":"No data returned for the given SSCC code"})
        
        # Execute the stored procedure using parameterized query
        
        with connection.cursor() as cursor:
            # Insert using stored procedure
            cursor.execute(
                """
                EXEC insert_returnreceivingcancelsscc_tempscan_data 
                    @barcode = %s, 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @supplier_gln = %s,
                    @ref_identifier=%s,
                    @EventTime = %s,
                    @sscc_urn = %s,
                    @sgln_urn = %s
                """,
                [sscc, identifier, sender_gln, receiver_gln, supplier_gln, instance_identifier_reference,event_time_dt,sscc_urn, sgln_urn]
            )

            # Fetch stored record using second procedure
            cursor.execute("EXEC return_receive_cancel_sscc_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"message": "Success","status":0,"returnreceivecancel_results":results}, status=status.HTTP_200_OK)
        

                
class ReturnReceiveCancelFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_return_receive_cancelscan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            returnreceive_cancel_scan_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'returnreceive_cancel_scan_data': returnreceive_cancel_scan_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class ReturnReceivingCancellationAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC returnreceivecancel_sscc_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            sscc_urn = row['sscc_urn']
            sgln = row['sgln']
            reference_identifier=row['ReferenceIdentifier']
            event_time = row['EventTime']
            
            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

            try:

                # Build the XML
                xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
                <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                    <soap:Header/>
                    <soap:Body>
                        <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                            <EPCISHeader>
                                <sbdh:StandardBusinessDocumentHeader>
                                    <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                    <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                    <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                    <sbdh:DocumentIdentification>
                                        <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                        <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                        <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                        <sbdh:Type>Events</sbdh:Type>
                                        <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                    </sbdh:DocumentIdentification>
                                </sbdh:StandardBusinessDocumentHeader>
                            </EPCISHeader>
                            <EPCISBody>
                                <EventList>
                                    <ObjectEvent>
                                        <eventTime>{event_time_str}</eventTime>
                                        <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                        <epcList><epc>{sscc_urn}</epc></epcList>
                                        <action>OBSERVE</action>
                                        <bizStep>urn:epcglobal:cbv:bizstep:void_receiving</bizStep>
                                        <disposition>urn:epcglobal:cbv:disp:returned</disposition>
                                        <readPoint><id>{sgln}</id></readPoint>
                                        <bizLocation><id>{sgln}</id></bizLocation>
                                        <tatmeen:instanceIdentifierReference xmlns:tatmeen="https://tatmeen.ae/epcis/">{reference_identifier}</tatmeen:instanceIdentifierReference>
                                    </ObjectEvent>
                                </EventList>
                            </EPCISBody>
                        </epcis:EPCISDocument>
                    </soap:Body>
                </soap:Envelope>"""

                xml_bodies.append(xml_body)

                token_data = get_valid_token()
                headers = {
                    "Authorization": f"Bearer {token_data['access_token']}",
                    "apikey": settings.TATMEEN_API_KEY,
                    "Content-Type": "application/soap+xml; charset=utf-8"
                }

                response = requests.post(
                    'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
                    data=xml_body,
                    headers=headers
                )
                print("SendEPCIS Status Code:", response.status_code) 

                if response.status_code==202:

                    root = ET.fromstring(response.text)
                    ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                    code_elem = root.find('.//code')

                    if code_elem is not None and code_elem.text == '202':
                        print("--------incoming---------")

                        # Execute DB procedures inside context managers
                        with connection.cursor() as r:
                            r.execute("EXEC update_returnreceive_cancel_sscc_guid_map @identifier = %s", [instance_id])

                        with connection.cursor() as s:
                            s.execute("EXEC usp_DumpTempReturnReceiveCancelScanDetails @identifier = %s", [instance_id])

                        with connection.cursor() as t:
                            t.execute("EXEC clear_returnreceivecancel_sscc_temp_data @identifier = %s", [instance_id])

                        #message status
                        status_response = get_tatmeen_instance_status(instance_id)

                        message_status = status_response.get("messagestatus", "").strip()

                        if message_status == "S  - Successful":
                            print("========message success=======")
                            with connection.cursor() as u:
                                u.execute("EXEC update_returnreceivecancel_sscc_event @identifier = %s", [instance_id])
                                print("=====status updated 1=====")
                            return Response({"log": status_response.get("logList", [])})

                        elif message_status == "A  - Technical Error":
                            print("========technical error=======")
                            with connection.cursor() as v:
                                v.execute("EXEC update_returnreceivecancel_sscc_event_error @identifier = %s", [instance_id])
                                print("=====status updated 2=====")
                            return Response({"log": status_response.get("logList", [])})

                        elif message_status == "":
                            print("========no status returned=======")
                            return Response({
                                "error": "No message status returned. The instance might not exist or failed to process.",
                                "log": status_response.get("logList", [])
                            }, status=400)

                        else:
                            print(f"========unexpected status: {message_status}=======")
                            # Optional: Log this for further analysis
                            with connection.cursor() as w:
                                w.execute("EXEC update_returnreceivecancel_sscc_event_unknown @identifier = %s", [instance_id])
                            return Response({
                                "error": f"Unhandled message status: {message_status}",
                                "log": status_response.get("logList", [])
                            }, status=400)
                
                elif response.status_code!=202:
                    send_returnreceiving_cancellation_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True}, status=response.status_code)

            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })


### Dis- Aggregation BE From CASE ###

class Unpack_Case_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = unpack_guid_case.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.ucase_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"UCASE{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    unpack_guid_case.objects.create(
                        ucase_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

### here 2 ###
class DisAggBEfromCASEScanParentSGTINView(APIView):
    """
    API View to scan and parse parent and child SGTIN barcodes.
    """

    def post(self, request, *args, **kwargs):
        raw_data = request.data.get('barcode', '')

        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        
        print("Raw scanned input:", repr(raw_data))  # Safe print

        # Strip ASCII 29 (FNC1) if present
        raw_data = raw_data.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = raw_data.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        raw_data = raw_data[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, raw_data)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()
        print("Extracted GTIN:", gtin)
        print("Extracted Expiration Date:", expiration_date)
        print("Extracted Batch Number:", batch_number)
        
        
        # Check if record already exists
        obj_exists = TempParentDisAggBEfromCASEScan.objects.filter(
            UUID=identifier,
            parent_sgtin=gtin
        ).exists()

        # If not, create a new record
        if not obj_exists:
            TempParentDisAggBEfromCASEScan.objects.create(
                UUID=identifier,
                SenderGLN=sender_gln,
                ReceiverGLN=receiver_gln,
                SupplierGLN=supplier_gln,
                parent_sgtin=gtin
            )

        # ❌ Error in your original query: `identifier=UUID` is wrong
        # ✅ Corrected:
        input_data = TempParentDisAggBEfromCASEScan.objects.filter(
            UUID=identifier
        ).values('UUID', 'parent_sgtin')

        if input_data.exists():
            return Response({
                "message": "Success",
                "DisAggBEfromCASES_results": list(input_data),
                "Status":1
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "No data found for given UUID"
            }, status=status.HTTP_404_NOT_FOUND)
        
## here 3 ###
class DisAggBEfromCASEScanSGTINView(APIView):
    """
    API View to scan and parse parent and child SGTIN barcodes.
    """

    def post(self, request, *args, **kwargs):
        parent_barcode = request.data.get('barcode', '')
        raw_data = request.data.get('child_barcode', '')
        identifier = request.data.get('identifier', '')
        event_time_str = request.data.get('event_time', '')
        
        print("Raw scanned input:", repr(raw_data))  # Safe print

        # Strip ASCII 29 (FNC1) if present
        raw_data = raw_data.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = raw_data.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        raw_data = raw_data[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, raw_data)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()
        print("Extracted GTIN:", gtin)
        print("Extracted Expiration Date:", expiration_date)
        print("Extracted Batch Number:", batch_number)
        
        obj= TempParentDisAggBEfromCASEScan.objects.filter(
            UUID=identifier,
            parent_sgtin=parent_barcode,
            status=0
        ).first()
        if not obj:
            return Response({
                "message": "Parent SGTIN not found for the given identifier","Status":0
            }, status=status.HTTP_404_NOT_FOUND)
        sender_gln = obj.SenderGLN
        receiver_gln = obj.ReceiverGLN
        
        try:
            
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)

            parent_sgtin = generate_sgtin_from_gtin(parent_barcode, ProductMaster, vendor_master)
            print("====Parent SGTIN:", parent_barcode)

            child_sgtin = generate_sgtin_from_gtin(gtin, ProductMaster, vendor_master)
            print("====Child SGTIN:", gtin)

            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                EXEC insert_DisAggBE_CASE_tempscan_data 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @EventTime = %s,
                    @sgln_urn = %s,
                    @parent_gtin = %s,
                    @child_gtin = %s,
                    @parent_sgtin = %s,
                    @child_sgtin = %s
                """,
                [
                    identifier,
                    sender_gln,
                    receiver_gln,
                    event_time_dt,
                    sgln_urn,
                    parent_barcode,
                    gtin,
                    parent_sgtin,
                    child_sgtin
                ]
            )

            # Fetch related EPC data after inserts (optional, for UI)
            cursor.execute("EXEC DisAggBE_CASE_data_one @identifier = %s, @barcode = %s", [identifier, parent_barcode])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({
            "message": "Success","DisAggBE_CASE_results": results}, status=status.HTTP_200_OK)

class DisAggCASEFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_DisAggBE_CASEScan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            DisAggBE_CASE_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'DisAggBE_CASE_data': DisAggBE_CASE_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class DisAggCASEClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']
            with connection.cursor() as cursor:
            # Clear data using stored procedure
                 cursor.execute("EXEC clear_TempParentDisAggBEfromCASEScan @identifier = %s", [identifier])

            cursor = connection.cursor()
            cursor.execute("EXEC clear_DisAggBE_CASEScan_dataone @identifier = %s", [identifier])
        
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DisaggregationBEfromCaseAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC DisAggBE_CASE_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            sgln = row['sgln']
            instance_id=row['UUID']
            parent_sgtin = row['parent_sgtin']
            child_sgtin=row['child_sgtin']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

           
            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender>
                                    <sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier>
                                </sbdh:Sender>
                                <sbdh:Receiver>
                                    <sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier>
                                </sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <AggregationEvent>
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <parentID>{parent_sgtin}</parentID>
                                    <childEPCs>
                                        <epc>{child_sgtin}</epc>
                                    </childEPCs>
                                    <action>DELETE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:unpacking</bizStep>
                                    <readPoint>
                                        <id>{sgln}</id>
                                    </readPoint>
                                    <bizLocation>
                                        <id>{sgln}</id>
                                    </bizLocation>
                                </AggregationEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_DisAggBE_CASE_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempDisAggBE_CASEScanDetails @identifier = %s", [instance_id])


                    #change----------------------------------------------------------

                    with connection.cursor() as t:
                        t.execute("EXEC usp_TempParentDisAggBEfromCASEScan @identifier = %s", [instance_id])

                    #change----------------------------------------------------------

                    with connection.cursor() as t:
                        t.execute("EXEC clear_DisAggBE_CASE_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_DisAggBE_CASE_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_DisAggBE_CASE_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        with connection.cursor() as w:
                            w.execute("EXEC update_DisAggBE_CASE_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_disaggregationBE_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })

### DIS-AGGREGATION OF 1 EA FROM BE ###

class Unpack_BA_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = unpack_guid_ba.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.uba_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"UBA{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    unpack_guid_ba.objects.create(
                        uba_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

## here 1 ###

class DisAggEAfromBEAScanParentSGTINView(APIView):
    def post(self, request, *args, **kwargs):
        parent_barcode = request.data.get('barcode', '')
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')


        parent_barcode = parent_barcode.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = parent_barcode.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        parent_barcode = parent_barcode[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, parent_barcode)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()

        obj_exists = TempParentDisAggEAfromBEAScan.objects.filter(
            uuid=identifier,
            parent_sgtin=gtin
        ).exists()

        if not obj_exists:
            TempParentDisAggEAfromBEAScan.objects.create(
                uuid=identifier,
                sender_gln=sender_gln,
                receiver_gln=receiver_gln,
                parent_sgtin=gtin
            )

        input_data = TempParentDisAggEAfromBEAScan.objects.filter(
            uuid=identifier
        ).values('uuid', 'parent_sgtin')

        if input_data.exists():
            return Response({
                "message": "Success",
                "DisAggBEfromCASES_results": list(input_data),
                "Status": 1
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "No data found for given UUID"
            }, status=status.HTTP_404_NOT_FOUND)



class DisAggEAfromBEAScanSGTINView(APIView):
    """
    API View to scan and parse parent and child SGTIN barcodes.
    """

    def post(self, request, *args, **kwargs):
        parent_barcode = request.data.get('barcode', '')
        raw_data = request.data.get('child_barcode', '')
        identifier = request.data.get('identifier', '')
        event_time_str = request.data.get('event_time', '')

        print("Raw scanned input:", repr(raw_data))  # Safe print

        # Strip ASCII 29 (FNC1) if present
        raw_data = raw_data.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = raw_data.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        raw_data = raw_data[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, raw_data)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()
        print("Extracted GTIN:", gtin)
        print("Extracted Expiration Date:", expiration_date)
        print("Extracted Batch Number:", batch_number)

        obj= TempParentDisAggEAfromBEAScan.objects.filter(
            uuid=identifier,
            parent_sgtin=parent_barcode,
            status=0
        ).first()
        if not obj:
            return Response({
                "message": "Parent SGTIN not found for the given identifier","Status":0
            }, status=status.HTTP_404_NOT_FOUND)
        sender_gln = obj.sender_gln
        receiver_gln = obj.receiver_gln
        
        try:
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)

            parent_sgtin = generate_sgtin_from_gtin(parent_barcode, ProductMaster, vendor_master)
            print("====Parent SGTIN:", parent_barcode)

            child_sgtin = generate_sgtin_from_gtin(gtin, ProductMaster, vendor_master)
            print("====Child SGTIN:", gtin)

            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                EXEC insert_DisAggEAfromBEA_tempscan_data 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s, 
                    @EventTime = %s,
                    @sgln_urn = %s,
                    @parent_gtin = %s,
                    @child_gtin = %s,
                    @parent_sgtin = %s,
                    @child_sgtin = %s
                """,
                [
                    identifier,
                    sender_gln,
                    receiver_gln,
                    event_time_dt,
                    sgln_urn,
                    parent_barcode,
                    gtin,
                    parent_sgtin,
                    child_sgtin
                ]
            )

            # Fetch related EPC data after inserts (optional, for UI)
            cursor.execute("EXEC DisAggEAfromBEA_data_one @identifier = %s, @barcode = %s", [identifier, parent_barcode])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({
            "message": "Success","DisAggEAfromBEA_results": results}, status=status.HTTP_200_OK)

    


class DisAggEAfromBEFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_DisAggEAfromBEAScan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            DisAggEAfromBEA_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'DisAggEAfromBEA_data': DisAggEAfromBEA_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class DisAggEAfromBEClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            with connection.cursor() as cursor:
            # Clear data using stored procedure
                cursor.execute("EXEC clear_TempParentDisAggEAfromBEAScan @identifier = %s", [identifier])
            cursor = connection.cursor()
            cursor.execute("EXEC clear_DisAggEAfromBEAScan_dataone @identifier = %s", [identifier])
        
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DisaggregationEAfromBEAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC DisAggEAfromBEA_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            sgln = row['sgln']
            instance_id=row['UUID']
            parent_sgtin = row['parent_sgtin']
            child_sgtin=row['child_sgtin']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

           
            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}Z" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender>
                                    <sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier>
                                </sbdh:Sender>
                                <sbdh:Receiver>
                                    <sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier>
                                </sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}Z</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <AggregationEvent>
                                    <eventTime>{event_time_str}Z</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <parentID>{parent_sgtin}</parentID>
                                    <childEPCs>
                                        <epc>{child_sgtin}</epc>
                                    </childEPCs>
                                    <action>DELETE</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:unpacking</bizStep>
                                    <readPoint>
                                        <id>{sgln}</id>
                                    </readPoint>
                                    <bizLocation>
                                        <id>{sgln}</id>
                                    </bizLocation>
                                </AggregationEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/scp/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_DisAggEAfromBEA_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempDisEAfromBEAScanDetails @identifier = %s", [instance_id])


                    #change----------------------------------------------------------
                    with connection.cursor() as m:
                        m.execute("EXEC usp_TempParentDisAggEAfromBEAScan @identifier = %s", [instance_id])
                    #change----------------------------------------------------------

                    with connection.cursor() as t:
                        t.execute("EXEC clear_DisAggEAfromBE_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_DisAggEAfromBE_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_DisAggEAfromBE_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        with connection.cursor() as w:
                            w.execute("EXEC update_DisAggEAfromBE_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_disaggregationEA_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })



############## Commissioning -- Aggregation Eaches Into Case ################

class Commission_EachesIntoCase_GenerateIdentifierView(APIView):
    def post(self, request):
        try:
            # Check if an unused identifier exists
            existing_record = commision_guid_eaches.objects.filter(status=0).first()
            if existing_record:
                return Response({"identifier": existing_record.cmeach_guid}, status=status.HTTP_200_OK)

            # Fetch company prefix (up to 10 chars)
            company_data = CompanyDetails.objects.values('company_prefix').first()
            company_prefix = company_data['company_prefix'] if company_data else ""
            guid_prefix = f"CP{company_prefix}"

            total_required_length = 32
            min_random_length = total_required_length - len(guid_prefix)

            max_attempts = 10
            for _ in range(max_attempts):
                random_suffix = generate_random_string_with_uuid_seed(min_random_length)
                code = guid_prefix + random_suffix

                # Ensure code is unique
                if not UniqueIdentifier.objects.using('default').filter(code=code).exists():
                    UniqueIdentifier.objects.using('default').create(code=code)
                    commision_guid_eaches.objects.create(
                        cmeach_guid=code,
                        created_date=timezone.now(),
                        status=0
                    )
                    return Response({"identifier": code}, status=status.HTTP_201_CREATED)

            return Response(
                {"error": "Could not generate a unique identifier. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AggEachesIntoCaseScanParentSGTINView(APIView):
    """
    API View to scan and parse parent and child SGTIN barcodes.
    """

    def post(self, request, *args, **kwargs):
        raw_data = request.data.get('barcode', '')  # parent barcode
        identifier = request.data.get('identifier', '')
        sender_gln = request.data.get('sender_gln', '')
        receiver_gln = request.data.get('receiver_gln', '')
        supplier_gln = request.data.get('supplier_gln', '')
        
        print("Raw scanned input:", repr(raw_data))  # Safe print

        # Strip ASCII 29 (FNC1) if present
        raw_data = raw_data.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = raw_data.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        raw_data = raw_data[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, raw_data)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()
        print("Extracted GTIN:", gtin)
        print("Extracted Expiration Date:", expiration_date)
        print("Extracted Batch Number:", batch_number)

        # Check if record already exists
        obj_exists = TempAggEachesIntoCaseParentSGTIN.objects.filter(
            UUID=identifier,
            parent_sgtin=gtin
        ).exists()

        # If not, create a new record
        if not obj_exists:
            TempAggEachesIntoCaseParentSGTIN.objects.create(
                UUID=identifier,
                SenderGLN=sender_gln,
                ReceiverGLN=receiver_gln,
                SupplierGLN=supplier_gln,
                parent_sgtin=gtin
            )

        # ❌ Error in your original query: `identifier=UUID` is wrong
        # ✅ Corrected:
        input_data = TempAggEachesIntoCaseParentSGTIN.objects.filter(
            UUID=identifier
        ).values('UUID', 'parent_sgtin')

        if input_data.exists():
            return Response({
                "message": "Success",
                "AggEachesIntoCase_results": list(input_data),
                "Status":1
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "No data found for given UUID"
            }, status=status.HTTP_404_NOT_FOUND)


class AggEachesIntoCaseScanChildSGTINView(APIView):
    """
    API View to scan and parse parent and child SGTIN barcodes.
    """

    def post(self, request, *args, **kwargs):
        parent_barcode = request.data.get('barcode', '')#parent barcode
        raw_data = request.data.get('child_barcode', '')#child barcode
        identifier = request.data.get('identifier', '')
        event_time_str = request.data.get('event_time', '')

        print("Raw scanned input:", repr(raw_data))  # Safe print

        # Strip ASCII 29 (FNC1) if present
        raw_data = raw_data.lstrip(chr(29) + '>')

        # Find the position of '01' to ignore leading noise
        idx = raw_data.find('01')
        if idx == -1:
            return Response({"error": "AI '01' not found in barcode"}, status=status.HTTP_400_BAD_REQUEST)

        # Only parse from the '01' onwards
        raw_data = raw_data[idx:]

        # Use regex to extract GTIN (01), Expiry (17), and Batch (10)
        pattern = r"01(\d{14})17(\d{6})10(.+)"
        match = re.match(pattern, raw_data)

        if not match:
            return Response({"error": "Invalid SGTIN format"}, status=status.HTTP_400_BAD_REQUEST)

        gtin, expiration_date, batch_number = match.groups()
        print("Extracted GTIN:", gtin)
        print("Extracted Expiration Date:", expiration_date)
        print("Extracted Batch Number:", batch_number)
        
        
        obj= TempAggEachesIntoCaseParentSGTIN.objects.filter(
            UUID=identifier,
            parent_sgtin=parent_barcode,
            status=0
        ).first()
        
        if not obj:
            return Response({
                "message": "Parent SGTIN not found for the given identifier","Status":0
            }, status=status.HTTP_404_NOT_FOUND)
            
        sender_gln = obj.SenderGLN
        receiver_gln = obj.ReceiverGLN
        supplier_gln = obj.SupplierGLN
       
        try:
            
            sgln_urn = generate_sgln_urn(sender_gln)
            print("====SGLN URN:", sgln_urn)

            parent_sgtin = generate_sgtin_from_gtin(parent_barcode, ProductMaster, vendor_master)
            print("====Parent SGTIN:", parent_barcode)

            child_sgtin = generate_sgtin_from_gtin(gtin, ProductMaster, vendor_master)
            print("====Child SGTIN:", gtin)

            event_time_dt = (
                datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
                if event_time_str else None
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                EXEC insert_AggEachesIntoCase_tempscan_data 
                    @identifier = %s, 
                    @sender_gln = %s, 
                    @receiver_gln = %s,
                    @supplier_gln = %s,  
                    @EventTime = %s,
                    @sgln_urn = %s,
                    @parent_gtin = %s,
                    @child_gtin = %s,
                    @parent_sgtin = %s,
                    @child_sgtin = %s
                """,
                [
                    identifier,
                    sender_gln,
                    receiver_gln,
                    supplier_gln,
                    event_time_dt,
                    sgln_urn,
                    parent_barcode,
                    gtin,
                    parent_sgtin,
                    child_sgtin
                ]
            )

            # Fetch related EPC data after inserts (optional, for UI)
            cursor.execute("EXEC AggEachesIntoCase_data_one @identifier = %s, @barcode = %s", [identifier, parent_barcode])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({
            "message": "Success","AggEachesIntoCase_results": results}, status=status.HTTP_200_OK)



class AggEachesIntoCaseFetchDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC fetch_AggEachesIntoCaseScan_dataone @identifier = %s", [identifier])
            columns = [col[0] for col in cursor.description]
            AggEachesIntoCase_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({'AggEachesIntoCase_data': AggEachesIntoCase_data}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AggEachesIntoCaseClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']
            with connection.cursor() as cursor:
                cursor.execute("EXEC clear_AggEachesIntoCaseScan_Parentdataone @identifier = %s", [identifier])

            cursor = connection.cursor()
            cursor.execute("EXEC clear_AggEachesIntoCaseScan_dataone @identifier = %s", [identifier])
        
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AggregationEachesIntoCaseAPIView(APIView):
    def post(self, request):
        data = request.data
        instance_id = data['instance_id']
        
        result = []
        with connection.cursor() as cursor:
            cursor.execute("EXEC AggEachesIntoCase_data_list @identifier = %s", [instance_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
        print("===== result ======",result)

        xml_bodies = []

        for row in result:
            sender = row['SenderGLN']
            receiver = row['ReceiverGLN']
            event_time = row['EventTime']
            sgln = row['sgln']
            instance_id=row['UUID']
            parent_sgtin = row['parent_sgtin']
            child_sgtin=row['child_sgtin']

            if isinstance(event_time, datetime):
                # Assume it's Dubai time if not tz-aware
                if event_time.tzinfo is None:
                    dubai_tz = pytz.timezone('Asia/Dubai')
                    event_time = dubai_tz.localize(event_time)
                event_time_utc = event_time.astimezone(pytz.utc)
                event_time_str = event_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                event_time_str = str(event_time)  # fallback (not recommended)
            event_time_zone_offset = "+04:00"

           
            # Build the XML
            xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
                <soap:Header/>
                <soap:Body>
                    <epcis:EPCISDocument schemaVersion="1.2" creationDate="{event_time_str}" xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" xmlns:epcis="urn:epcglobal:epcis:xsd:1" xmlns:cbvmda="urn:epcglobal:cbv:mda" xmlns:tatmeen="http://tatmeen.ae/epcis/">
                        <EPCISHeader>
                            <sbdh:StandardBusinessDocumentHeader>
                                <sbdh:HeaderVersion>1.3</sbdh:HeaderVersion>
                                <sbdh:Sender><sbdh:Identifier Authority="GS1">{sender}</sbdh:Identifier></sbdh:Sender>
                                <sbdh:Receiver><sbdh:Identifier Authority="GS1">{receiver}</sbdh:Identifier></sbdh:Receiver>
                                <sbdh:DocumentIdentification>
                                    <sbdh:Standard>EPCGlobal</sbdh:Standard>
                                    <sbdh:TypeVersion>1.0</sbdh:TypeVersion>
                                    <sbdh:InstanceIdentifier>{instance_id}</sbdh:InstanceIdentifier>
                                    <sbdh:Type>Events</sbdh:Type>
                                    <sbdh:CreationDateAndTime>{event_time_str}</sbdh:CreationDateAndTime>
                                </sbdh:DocumentIdentification>
                            </sbdh:StandardBusinessDocumentHeader>
                        </EPCISHeader>
                        <EPCISBody>
                            <EventList>
                                <AggregationEvent>
                                    <!-- AGGREGATION OF EACHES INTO CASE -->
                                    <eventTime>{event_time_str}</eventTime>
                                    <eventTimeZoneOffset>{event_time_zone_offset}</eventTimeZoneOffset>
                                    <parentID>{parent_sgtin}</parentID>
                                    <childEPCs><epc>{child_sgtin}</epc></childEPCs>
                                    <action>ADD</action>
                                    <bizStep>urn:epcglobal:cbv:bizstep:packing</bizStep>
                                    <readPoint><id>{sgln}</id></readPoint>
                                    <bizLocation><id>{sgln}</id></bizLocation>
                                </AggregationEvent>
                            </EventList>
                        </EPCISBody>
                    </epcis:EPCISDocument>
                </soap:Body>
            </soap:Envelope>"""

            xml_bodies.append(xml_body)
            print("=======xml data=======",xml_bodies)
            token_data = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "apikey": settings.TATMEEN_API_KEY,
                "Content-Type": "application/soap+xml; charset=utf-8"
            }

            response = requests.post(
                'https://tatmeenapim.mohap.gov.ae/v1/mah/B2B/SendEPCIS',
                data=xml_body,
                headers=headers
            )
            print("SendEPCIS Status Code:", response.status_code) 
            print("SendEPCIS Response Text:", response.text)

            if response.status_code==202:

                root = ET.fromstring(response.text)
                ns = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
                code_elem = root.find('.//code')

                if code_elem is not None and code_elem.text == '202':
                    print("--------incoming---------")

                    # Execute DB procedures inside context managers
                    with connection.cursor() as r:
                        r.execute("EXEC update_AggEachesIntoCase_guid_map @identifier = %s", [instance_id])

                    with connection.cursor() as s:
                        s.execute("EXEC usp_DumpTempAggEachesIntoCaseScanDetails @identifier = %s", [instance_id])

                    #change============================================================================
                    with connection.cursor() as q:
                        q.execute("EXEC usp_AggEachesIntoCase_Parenttemp_data @identifier = %s", [instance_id])
                    #change============================================================================

                    with connection.cursor() as t:
                        t.execute("EXEC clear_AggEachesIntoCase_temp_data @identifier = %s", [instance_id])

                    #message status
                    status_response = get_tatmeen_instance_status(instance_id)
                    # if status_response.status_code==200:
                    print("========in receiving api status_response=======", status_response)

                    message_status = status_response.get("messagestatus", "").strip()
                    print("======iinn receiving message sttatus=====",message_status)

                    if message_status == "S - Successful":
                        print("========message success=======")
                        with connection.cursor() as u:
                            u.execute("EXEC update_AggEachesIntoCase_event @identifier = %s", [instance_id])
                            print("=====status updated 1=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "A - Technical Error":
                        print("========technical error=======")
                        with connection.cursor() as v:
                            v.execute("EXEC update_AggEachesIntoCase_event_error @identifier = %s", [instance_id])
                            print("=====status updated 2=====")
                        return Response({"log": status_response.get("logList", [])})

                    elif message_status == "":
                        print("========no status returned=======")
                        return Response({
                            "error": "No message status returned. The instance might not exist or failed to process.",
                            "log": status_response.get("logList", [])
                        })

                    else:
                        print(f"========unexpected status: {message_status}=======")
                        # Optional: Log this for further analysis
                        with connection.cursor() as w:
                            w.execute("EXEC update_AggEachesIntoCase_event_unknown @identifier = %s", [instance_id])
                        return Response({
                            "error": f"Unhandled message status: {message_status}",
                            "log": status_response.get("logList", [])
                        })
                else:
                    return Response({"error": "Failed to fetch message status from Tatmeen API.",
                                        "log": status_response.get("logList", [])}, status=status_response.status_code)
            elif response.status_code!=202:
                    send_aggregationEACHES_to_tatmeen.send(xml_body, token_data['access_token'])
                    return Response({
                        "message": "Tatmeen API did not accept the request. Retry scheduled.","status_code": response.status_code,
                        "retry": True})
        return Response({
            "message": "success"
            # "message_response": status_response,
            # "log": status_response.get("logList", [])
            })

########################### CLEAR FUNCTIONS #################

class RecClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_recscan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommSGTINClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_CommSGTINProductScan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_CommSSCCScan_dataone @identifier = %s", [identifier])
           
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommShippercasesClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_CommShipperCasesScan_dataone @identifier = %s", [identifier])
    
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CommAggregationClearDataAPIView(APIView):
#     def post(self,request):
#         try:
#             body_unicode = request.body.decode('utf-8')
#             data = json.loads(body_unicode)

#             identifier=data['identifier']

#             cursor = connection.cursor()
#             cursor.execute("EXEC clear_CommAggregationScan_dataone @identifier = %s", [identifier])
            

#             return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
#         except Exception as e:  
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class AggEachesIntoCaseClearDataAPIView(APIView):
#     def post(self,request):
#         try:
#             body_unicode = request.body.decode('utf-8')
#             data = json.loads(body_unicode)

#             identifier=data['identifier']

#             cursor = connection.cursor()
#             cursor.execute("EXEC clear_AggEachesIntoCaseScan_dataone @identifier = %s", [identifier])
        
#             return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
#         except Exception as e:  
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class DisAggCSfromSSCCClearDataAPIView(APIView):
#     def post(self,request):
#         try:
#             body_unicode = request.body.decode('utf-8')
#             data = json.loads(body_unicode)

#             identifier=data['identifier']

#             cursor = connection.cursor()
#             cursor.execute("EXEC clear_disaggcsfromsscc_dataone @identifier = %s", [identifier])
            
#             return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
#         except Exception as e:  
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DisAggCSfromSSCCClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            with connection.cursor() as cursor:
                cursor.execute("EXEC clear_DisAggCSfromSSCCScan_Parentdataone @identifier = %s", [identifier])

            cursor = connection.cursor()
            cursor.execute("EXEC clear_disaggcsfromsscc_dataone @identifier = %s", [identifier])

            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
			
class ShipppingCancelClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_ship_cancelscan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)			
			

class ReturnShipppingCancelClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_return_ship_cancelscan_dataone @identifier = %s", [identifier])
        
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReturnReceiveCancelClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_return_receive_cancelscan_dataone @identifier = %s", [identifier])
        
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
		
			
class DisAggCASEClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']
            with connection.cursor() as cursor:
            # Clear data using stored procedure
                 cursor.execute("EXEC clear_TempParentDisAggBEfromCASEScan @identifier = %s", [identifier])

            cursor = connection.cursor()
            cursor.execute("EXEC clear_DisAggBE_CASEScan_dataone @identifier = %s", [identifier])

            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class DisAggEAfromBEClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            with connection.cursor() as cursor:
            # Clear data using stored procedure
                cursor.execute("EXEC clear_TempParentDisAggEAfromBEAScan @identifier = %s", [identifier])
            cursor = connection.cursor()
            cursor.execute("EXEC clear_DisAggEAfromBEAScan_dataone @identifier = %s", [identifier])

            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
			
class ReturnReceivingClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_ret_rec_scan_dataone @identifier = %s", [identifier])
        
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
class StolenClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_stolenscan_dataone @identifier = %s", [identifier])
           
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DecommClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_decommscan_dataone @identifier = %s", [identifier])
           
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShipppingClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_shipscan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
			
class ExportedClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_exportedscan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LostClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC cleared_lostscan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
			
class DispenseClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_dispensessccscan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
			
class DispenseSGTINClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_dispensesgtinscan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)			



class SampleClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_samplescan_dataone @identifier = %s", [identifier])
            
            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
class ReturnShipppingClearDataAPIView(APIView):
    def post(self,request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            identifier=data['identifier']

            cursor = connection.cursor()
            cursor.execute("EXEC clear_retshipscan_dataone @identifier = %s", [identifier])

            return Response({'message': "The Data is cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




############# Excel Upload ##############

import pandas as pd
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser

from django.conf import settings
import os


# views.py
from datetime import datetime, timedelta




# ---------- Helpers ----------

AI_01_21_REGEX = re.compile(r"\(01\)(\d{14})\(21\)([0-9A-Za-z\-\.\/]+)")
AI_10_REGEX = re.compile(r"\(10\)([^\(\)]+)")

def _parse_epc_ai_01_21(epc: str):
    if not isinstance(epc, str):
        raise ValueError("EPC must be a string")
    m = AI_01_21_REGEX.search(epc.replace(" ", ""))
    if not m:
        raise ValueError(f"Invalid EPC format: {epc}")
    return m.group(1), m.group(2)

def _parse_lot_from_parent(parent: str):
    if not isinstance(parent, str):
        return None
    m = AI_10_REGEX.search(parent)
    return m.group(1).strip() if m else None

def _to_naive_datetime(val):
    if pd.isna(val):
        return None
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime().replace(tzinfo=None)
    if isinstance(val, datetime):
        return val.replace(tzinfo=None)
    s = str(val).strip().rstrip("T")
    ts = pd.to_datetime(s, errors="coerce", utc=False)
    if pd.isna(ts):
        return None
    if getattr(ts, "tzinfo", None) is not None:
        ts = ts.tz_convert("UTC").tz_localize(None)
    return ts.to_pydatetime()

def _to_date(val):
    if pd.isna(val):
        return None
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.date()
    s = str(val).strip().rstrip("T")
    ts = pd.to_datetime(s, errors="coerce", utc=False)
    if pd.isna(ts):
        return None
    return ts.date()

def _parse_time_offset(offset_str: str) -> timedelta | None:
    if not offset_str or not isinstance(offset_str, str):
        return None
    s = offset_str.strip()
    m = re.match(r"^([+-])(\d{1,2}):([0-5]\d)$", s)
    if not m:
        return None
    sign = -1 if m.group(1) == "-" else 1
    hours = int(m.group(2))
    mins = int(m.group(3))
    return sign * timedelta(hours=hours, minutes=mins)

def _apply_offset(dt, offset):
    if dt is None or offset is None:
        return dt
    return dt + offset

def _safe_str(x):
    return None if (x is None or (isinstance(x, float) and pd.isna(x))) else str(x).strip()


##### back here2 ######

def generate_sgtin_from_gtin_and_serial(gtin: str, serial_number: str, product_model, vendor_model):
    """
    Build SGTIN from GTIN & existing serial number (from EPC),
    using product/vendor master for company prefix.
    """
    try:
        product = product_model.objects.get(gtin=gtin)
    except product_model.DoesNotExist:
        raise ValueError(f"No product found for GTIN: {gtin}")

    manufacturer_gln = product.manufacturer

    try:
        vendor = vendor_model.objects.get(GLN=manufacturer_gln)
    except vendor_model.DoesNotExist:
        raise ValueError(f"No vendor found with GLN: {manufacturer_gln}")

    company_prefix = vendor.CompanyPrefix
    cp_len = len(company_prefix)

    # GTIN-14: Indicator (1) + Company Prefix + Item Ref + Check Digit
    gtin_body = gtin[:-1]  # Remove check digit
    indicator = gtin_body[0]
    item_ref = gtin_body[1+cp_len:]

    return f"urn:epc:id:sgtin:{company_prefix}.{indicator}{item_ref}.{serial_number}"




class CommissionSGTINExcelUploadView(APIView):
    """
    Upload Excel with columns:
        epc | eventTime | timeOffset (optional) | parent | permit | expiryDate | manufDate
    Rest of the data (identifier, sender_gln, receiver_gln, supplier_gln)
    is provided as form-data fields (same as CommScanSGTINView).
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Form-data inputs
        identifier = _safe_str(request.data.get("identifier"))
        sender_gln = _safe_str(request.data.get("sender_gln"))
        receiver_gln = _safe_str(request.data.get("receiver_gln"))
        supplier_gln = _safe_str(request.data.get("supplier_gln"))

        # Save temporarily
        saved_path = default_storage.save(f"tmp/{excel_file.name}", excel_file)
        full_path = os.path.join(settings.MEDIA_ROOT, saved_path)

        try:
            df = pd.read_excel(full_path, engine="openpyxl")
        except Exception as e:
            return Response({"error": f"Unable to read Excel: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = ["epc", "eventTime", "parent", "permit", "expiryDate", "`    ``"]
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            return Response({"error": f"Missing columns in Excel: {missing}"}, status=status.HTTP_400_BAD_REQUEST)

        all_results = []
        errors = []

        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    # Parse EPC and basic fields
                    epc = _safe_str(row["epc"])
                    if not epc:
                        raise ValueError("EPC is empty")

                    event_time = _to_naive_datetime(row["eventTime"])
                    if event_time is None:
                        raise ValueError(f"Invalid eventTime: {row['eventTime']}")

                    time_offset = _parse_time_offset(_safe_str(row.get("timeOffset")))
                    event_time = _apply_offset(event_time, time_offset)

                    parent = _safe_str(row["parent"])
                    permit = _safe_str(row["permit"])
                    expiry_date = _to_date(row["expiryDate"])
                    manuf_date = _to_date(row["manufDate"])

                    # Extract GTIN & Serial from EPC
                    gtin, serial = _parse_epc_ai_01_21(epc)
                    lot_number = _parse_lot_from_parent(parent)

                    # Generate SGTIN using existing GTIN + serial number
                    sgtin = generate_sgtin_from_gtin_and_serial(gtin, serial, ProductMaster, vendor_master)

                    # Build SGLN URN
                    sgln_urn = generate_sgln_urn(sender_gln)

                    # Insert into DB
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            EXEC insert_commsgtin_tempscan_data 
                                @barcode = %s, 
                                @identifier = %s, 
                                @sender_gln = %s, 
                                @receiver_gln = %s,
                                @supplier_gln = %s, 
                                @EventTime = %s,
                                @expiration_date = %s,
                                @mfg_date = %s,
                                @shp_prmt = %s,
                                @lot_no = %s,
                                @sgln_urn = %s,
                                @sgtin = %s
                            """,
                            [
                                gtin,
                                identifier,
                                sender_gln,
                                receiver_gln,
                                supplier_gln,
                                event_time,
                                expiry_date,
                                manuf_date,
                                permit,
                                lot_number,
                                sgln_urn,
                                sgtin
                            ]
                        )

                        # Fetch inserted record
                        cursor.execute(
                            "EXEC comm_sgtin_data_one @identifier = %s, @barcode = %s",
                            [identifier, gtin]
                        )
                        columns = [col[0] for col in cursor.description]
                        fetched = [dict(zip(columns, r)) for r in cursor.fetchall()]
                        all_results.extend(fetched)

                except Exception as e:
                    errors.append({
                        "rowIndex": int(idx) + 2,  # Excel row number (1-based + header)
                        "epc": row.get("epc"),
                        "error": str(e)
                    })

        return Response({
            "message": "Excel processed",
            "identifier": identifier,
            "inserted_count": len(all_results),
            "errors": errors,
            "results": all_results
        }, status=status.HTTP_200_OK)


###  back here 3 ###


class ShipperCasesExcelUploadView(APIView):
    """
    Upload Excel with columns:
        seqNo | bizstep | eventTime | timeOffset (optional) | epc | parent |
        Import | permit | expiryDate | manufDate
    Other metadata (identifier, sender_gln, receiver_gln, supplier_gln)
    is provided as form-data fields.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Form-data inputs
        identifier = _safe_str(request.data.get("identifier"))
        sender_gln = _safe_str(request.data.get("sender_gln"))
        receiver_gln = _safe_str(request.data.get("receiver_gln"))
        supplier_gln = _safe_str(request.data.get("supplier_gln"))

        # Save temporarily
        saved_path = default_storage.save(f"tmp/{excel_file.name}", excel_file)
        full_path = os.path.join(settings.MEDIA_ROOT, saved_path)

        try:
            df = pd.read_excel(full_path, engine="openpyxl")
        except Exception as e:
            return Response({"error": f"Unable to read Excel: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = ["seqNo", "bizstep", "eventTime", "epc", "parent", "permit", "expiryDate", "manufDate"]
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            return Response({"error": f"Missing columns in Excel: {missing}"}, status=status.HTTP_400_BAD_REQUEST)

        all_results = []
        errors = []

        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    epc = _safe_str(row["epc"])
                    if not epc:
                        raise ValueError("EPC is empty")

                    event_time = _to_naive_datetime(row["eventTime"])
                    if event_time is None:
                        raise ValueError(f"Invalid eventTime: {row['eventTime']}")

                    time_offset = _parse_time_offset(_safe_str(row.get("timeOffset")))
                    event_time = _apply_offset(event_time, time_offset)

                    permit = _safe_str(row["permit"])
                    expiry_date = _to_date(row["expiryDate"])
                    manuf_date = _to_date(row["manufDate"])
                    parent = _safe_str(row["parent"])

                    # Extract GTIN & Serial from EPC (01 + 21)
                    gtin, serial = _parse_epc_ai_01_21(epc)
                    lot_number = _parse_lot_from_parent(parent)

                    # Generate SGTIN
                    sgtin = generate_sgtin_from_gtin_and_serial(gtin, serial, ProductMaster, vendor_master)

                    # Build SGLN
                    sgln_urn = generate_sgln_urn(sender_gln)

                    # Insert into shipper temp table
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            EXEC insert_commshippercases_tempscan_data
                                @barcode = %s,
                                @identifier = %s,
                                @sender_gln = %s,
                                @receiver_gln = %s,
                                @supplier_gln = %s,
                                @EventTime = %s,
                                @expiration_date = %s,
                                @mfg_date = %s,
                                @shp_prmt = %s,
                                @lot_no = %s,
                                @sgln_urn = %s,
                                @sgtin = %s
                            """,
                            [
                                gtin,
                                identifier,
                                sender_gln,
                                receiver_gln,
                                supplier_gln,
                                event_time,
                                expiry_date,
                                manuf_date,
                                permit,
                                lot_number,
                                sgln_urn,
                                sgtin
                            ]
                        )

                        cursor.execute("EXEC comm_shippercases_data_one @identifier = %s, @barcode = %s", [identifier, gtin])
                        columns = [col[0] for col in cursor.description]
                        fetched = [dict(zip(columns, r)) for r in cursor.fetchall()]
                        all_results.extend(fetched)

                except Exception as e:
                    errors.append({
                        "rowIndex": int(idx) + 2,  # Excel row number (header+1)
                        "epc": row.get("epc"),
                        "error": str(e)
                    })

        return Response({
            "message": "Excel processed",
            "identifier": identifier,
            "inserted_count": len(all_results),
            "errors": errors,
            "results": all_results
        }, status=status.HTTP_200_OK)


#### back here 4 ####

class SSCCExcelUploadView(APIView):
    """
    Upload Excel with columns:
        seqNo | bizstep | eventTime | timeOffset (optional) | epc | parent | Import | permit | expiryDate | manufDate
    Form-data must also include: identifier, sender_gln, receiver_gln, supplier_gln.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Form-data inputs
        identifier = _safe_str(request.data.get("identifier"))
        sender_gln = _safe_str(request.data.get("sender_gln"))
        receiver_gln = _safe_str(request.data.get("receiver_gln"))
        supplier_gln = _safe_str(request.data.get("supplier_gln"))

        # Save temporarily
        saved_path = default_storage.save(f"tmp/{excel_file.name}", excel_file)
        full_path = os.path.join(settings.MEDIA_ROOT, saved_path)

        try:
            df = pd.read_excel(full_path, engine="openpyxl")
        except Exception as e:
            return Response({"error": f"Unable to read Excel: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = ["seqNo", "bizstep", "eventTime", "epc", "parent", "permit", "expiryDate", "manufDate"]
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            return Response({"error": f"Missing columns in Excel: {missing}"}, status=status.HTTP_400_BAD_REQUEST)

        all_results = []
        errors = []

        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    epc_raw = _safe_str(row["epc"])
                    if not epc_raw:
                        raise ValueError("EPC is empty")

                    # Extract SSCC from EPC (AI 00)
                    match = re.search(r"00(\d{18})", epc_raw.replace(" ", ""))
                    if not match:
                        raise ValueError(f"Invalid EPC format (SSCC missing): {epc_raw}")
                    sscc = match.group(1)

                    # Parse event time + offset
                    event_time = _to_naive_datetime(row["eventTime"])
                    if event_time is None:
                        raise ValueError(f"Invalid eventTime: {row['eventTime']}")
                    time_offset = _parse_time_offset(_safe_str(row.get("timeOffset")))
                    event_time = _apply_offset(event_time, time_offset)

                    permit = _safe_str(row["permit"])
                    expiry_date = _to_date(row["expiryDate"])
                    manuf_date = _to_date(row["manufDate"])
                    parent = _safe_str(row["parent"])

                    # Generate SSCC + SGLN URNs
                    sscc_urn = generate_sscc_urn(sscc, supplier_gln)
                    sgln_urn = generate_sgln_urn(sender_gln)

                    # Insert into temp table
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            EXEC insert_commsscc_tempscan_data
                                @barcode = %s,
                                @identifier = %s,
                                @sender_gln = %s,
                                @receiver_gln = %s,
                                @supplier_gln = %s,
                                @EventTime = %s,
                                @sscc_urn = %s,
                                @sgln_urn = %s
                            """,
                            [
                                sscc,
                                identifier,
                                sender_gln,
                                receiver_gln,
                                supplier_gln,
                                event_time,
                                sscc_urn,
                                sgln_urn
                            ]
                        )

                        # Fetch record back
                        cursor.execute("EXEC comm_sscc_data_one @identifier = %s, @barcode = %s", [identifier, sscc])
                        columns = [col[0] for col in cursor.description]
                        fetched = [dict(zip(columns, r)) for r in cursor.fetchall()]
                        all_results.extend(fetched)

                except Exception as e:
                    errors.append({
                        "rowIndex": int(idx) + 2,  # Excel row number (header+1)
                        "epc": row.get("epc"),
                        "error": str(e)
                    })

        return Response({
            "message": "Excel processed",
            "identifier": identifier,
            "inserted_count": len(all_results),
            "errors": errors,
            "results": all_results
        }, status=status.HTTP_200_OK)
