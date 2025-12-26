from django.shortcuts import render

# Create your views here.
import json
from rest_framework.views import APIView    
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from admin_management.models import *
from material_inward.models import *
from django.db import connection
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from tat_login.models import *
from rest_framework import status
import io
import barcode
from barcode.writer import ImageWriter
from django.http import FileResponse
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
import os
import re
import random
from barcode import get_barcode_class
from PIL import Image, ImageDraw, ImageFont



@method_decorator(csrf_exempt, name='dispatch')
class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        
        business_partner_name=data['business_partner_name']
        login_creation_date=data['login_creation_date']     
        login_validity_date=data['login_validity_date']
        email=data['email']
        phone1=data['phone1']
        phone2=data['phone2']
        postal_code=data['postal_code']
        street=data['street']
        country_code=data['country_code']
        house_number=data['house_number']
        city=data['city']
        region=data['region']
        area=data['area']
        username = data['username']
        password = data['password']

        # Inline password validation
        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[A-Z]", password):
            return Response({'error': 'Password must contain at least one uppercase letter.'}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[a-z]", password):
            return Response({'error': 'Password must contain at least one lowercase letter.'}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[0-9]", password):
            return Response({'error': 'Password must contain at least one digit.'}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return Response({'error': 'Password must contain at least one special character.'}, status=status.HTTP_400_BAD_REQUEST)

        if user_details.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        # try:
            # Check if the user already exists
        if user_details.objects.filter(username=username,status=1).exists():
            return Response({'error': 'User already exists'})
        
        if not user_details.objects.filter(username=username,status=1).exists():
            cursor = connections['default'].cursor()

            # cursor.execute("EXEC create_user'" + str(business_partner_name) + "', '" + str(login_creation_date) + "', '" + str(login_validity_date) + "', '" + str(GLN) + "', '" + str(company_prefix) + "', '" + str(email) + "', '" + str(phone1) + "', '" + str(phone2) + "', '" + str(spoc_first_name) + "', '" + str(spoc_last_name) + "', '" + str(spoc_phone) + "', '" + str(spoc_work_phone) + "', '" + str(postal_code) + "', '" + str(street) + "', '" + str(country_code) + "', '" + str(house_number) + "', '" + str(city) + "', '" + str(region) + "', '" + str(gps_coordinates) + "', '" + str(area)  +"', '"+str(username)+"'")
            cursor.execute("EXEC create_user'" + str(business_partner_name) + "', '" + str(login_creation_date) + "', '" + str(login_validity_date) + "','" + str(email) + "', '" + str(phone1) + "', '" + str(phone2) + "','" + str(postal_code) + "', '" + str(street) + "', '" + str(country_code) + "', '" + str(house_number) + "', '" + str(city) + "', '" + str(region) + "', '" + str(area)  +"', '"+str(username)+"'")
        
        if not usermaster.objects.filter(uname=username).exists():
            
            cursor = connections['remote'].cursor()
            cursor.execute("EXEC insert_into_usermaster'"+str(username)+"','" + str(business_partner_name) + "','"+str(password)+"'")

            # cursor.connections['default'].cursor()  # Commit the transaction to save changes
            # cursor.execute("EXEC insert_into_usermaster'"+str(username)+"','" + str(business_partner_name) + "','"+str(password)+"'")           
            
        if not UserRoleMapping.objects.filter(username=username).exists():
            cursor = connections['default'].cursor()
            cursor.execute("EXEC insert_into_userrolemapping'"+str(username)+"','" + str(business_partner_name) + "'")

        return Response({'message': 'User registered successfully'})

        # except Exception as e:
        #     return Response({'error': str(e)})
        

class UserDataAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            cursor = connections['default'].cursor()
            cursor.execute("EXEC fetch_user_details")
            columns = [col[0] for col in cursor.description]
            user_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            if not user_data:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'user_data': user_data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteUserDetailsAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            user_id = data['user_id']
            
            if not user_details.objects.filter(id=user_id, status=1).exists():
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            cursor = connections['default'].cursor()
            cursor.execute("EXEC delete_user_details %s", [user_id])
            
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UpdateUserDetailsAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))

            user_id = data['user_id']
            username = data['username']
            new_name = data['business_partner_name']
            email = data['email']
            phone1 = data['phone1']
            phone2 = data['phone2']
            postal_code = data['postal_code']
            street = data['street']
            country_code = data['country_code']
            house_number = data['house_number']
            city = data['city']
            region = data['region']
            area = data['area']

            # Check user exists in user_details
            if not user_details.objects.filter(id=user_id, username=username, status=1).exists():
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Update user_details
            with connections['default'].cursor() as local_cursor:
                local_cursor.execute("""
                    EXEC update_user_details 
                        @user_id=%s, @business_partner_name=%s, @email=%s, @phone1=%s, @phone2=%s, 
                        @postal_code=%s, @street=%s, @country_code=%s, @house_number=%s, 
                        @city=%s, @region=%s, @area=%s
                """, [
                    user_id, new_name, email, phone1, phone2,
                    postal_code, street, country_code, house_number,
                    city, region, area
                ])

            # Update UserRoleMapping in local DB
            with connections['default'].cursor() as local_cursor:
                local_cursor.execute("""
                    UPDATE UserRoleMapping
                    SET name = %s
                    WHERE username = %s
                """, [new_name, username])

            # Update usermaster in remote DB
            with connections['remote'].cursor() as remote_cursor:
                remote_cursor.execute("EXEC update_usermaster_name @username=%s, @new_name=%s", [username, new_name])

            return Response({'message': 'User details updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            





# class UpdateUserDetailsAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         try:
#             body_unicode = request.body.decode('utf-8')
#             data = json.loads(body_unicode)
            
#             user_id=data['user_id']
#             business_partner_name = data['business_partner_name']
#             email = data['email']
#             phone1 = data['phone1']
#             phone2 = data['phone2']
#             postal_code = data['postal_code']
#             street = data['street']
#             country_code = data['country_code']
#             house_number = data['house_number']
#             city = data['city']
#             region = data['region']
#             area = data['area']
            
#             if not user_details.objects.filter(business_partner_name=business_partner_name,email=email,phone1=phone1,phone2=phone2,postal_code=postal_code,street=street,country_code=country_code,house_number=house_number,city=city
#             ,region=region,area=area,status=1).exists():
#                 return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

#             cursor = connections['default'].cursor()
#             cursor.execute("EXEC update_user_details'" + str(user_id) + "','" + str(business_partner_name) + "','" + str(email) + "', '" + str(phone1) + "', '" + str(phone2) + "', '" + str(postal_code) + "', '" + str(street) + "', '" + str(country_code) + "', '" + str(house_number) + "', '" + str(city) + "', '" + str(region) + "', '" + str(area)  +"'")   
#             return Response({'message': 'User details updated successfully'}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# username update
class UpdateUsernameAPIView(APIView):
  
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))

            old_username = data.get("old_username")
            new_username = data.get("new_username")

            if not old_username or not new_username:
                return Response({'error': 'Both old and new usernames are required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if old username exists in local and remote
            if not usermaster.objects.using('remote').filter(uname=old_username).exists():
                return Response({'error': 'Old username not found in remote database.'}, status=status.HTTP_404_NOT_FOUND)

            if not user_details.objects.using('default').filter(username=old_username).exists():
                return Response({'error': 'Old username not found in local database.'}, status=status.HTTP_404_NOT_FOUND)

            # Check if new username already exists
            if usermaster.objects.using('remote').filter(uname=new_username).exists() or \
               user_details.objects.using('default').filter(username=new_username).exists():
                return Response({'error': 'New username already taken.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update remote DB
            with connections['remote'].cursor() as remote_cursor:
                remote_cursor.execute("EXEC update_username @old_username=%s, @new_username=%s", [old_username, new_username])

            # Update local DB
            with connections['default'].cursor() as local_cursor:
                local_cursor.execute("UPDATE user_details SET username = %s WHERE username = %s", [new_username, old_username])

            # Also update UserRoleMapping or any other dependent table
            UserRoleMapping.objects.filter(username=old_username).update(username=new_username)

            return Response({'message': 'Username updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# password update 
@method_decorator(csrf_exempt, name='dispatch')
class UpdatePasswordRemoteAPIView(APIView):
    def post(self, request):
        try:
            data = request.data

            username = data.get("username")
            old_password = data.get("old_password")
            new_password = data.get("new_password")

            # Check if required fields are present
            if not username or not old_password or not new_password:
                return Response({'error': 'Username, old password, and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Password strength validation
            import re
            if len(new_password) < 8 \
                or not re.search(r"[A-Z]", new_password) \
                or not re.search(r"[a-z]", new_password) \
                or not re.search(r"[0-9]", new_password) \
                or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
                return Response({
                    'error': 'New password must be at least 8 characters long and include uppercase, lowercase, number, and special character.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch current password from remote DB
            with connections['remote'].cursor() as cursor:
                cursor.execute("SELECT pwd FROM usermaster WHERE uname = %s AND working_status = 1", [username])
                row = cursor.fetchone()

                if not row:
                    return Response({'error': 'User not found or Inactive'}, status=status.HTTP_404_NOT_FOUND)

                current_password = row[0]

                if current_password != old_password:
                    return Response({'error': 'Old password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

                # Update the password
                cursor.execute("EXEC update_user_password @username=%s, @new_password=%s", [username, new_password])

            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):                   
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            username = data['username']
            
            cursor_default = connections['default'].cursor()  # local db
            cursor_default.execute("EXEC fetch_user_details_profile_info %s", [username])
            columns = [col[0] for col in cursor_default.description]
            profile_info = [dict(zip(columns, row)) for row in cursor_default.fetchall()]
            
            if not profile_info:
                # Fetch from remote database
                cursor_remote = connections['remote'].cursor()
                cursor_remote.execute("SELECT name, uname,roleid FROM usermaster WHERE uname = %s", [username])
                admin_data = cursor_remote.fetchone()
                if admin_data:
                    profile_info = [{
                        'name': admin_data[0],
                        'username': admin_data[1],
                        'roleid': admin_data[2],
                        'RoleName': 'Admin'
                    }]
                else:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({'profile_info_data': profile_info}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# generate barcodes
# working code
# def calculate_check_digit(number: str) -> str:
#     total = 0
#     reverse_digits = number[::-1]
#     for i, digit in enumerate(reverse_digits):
#         n = int(digit)
#         total += n * 3 if i % 2 == 0 else n
#     return str((10 - (total % 10)) % 10)

# class GenerateSSCCBarcode(APIView):
#     """
#     Generate, store, and return a GS1-compliant SSCC barcode and image URL.
#     """

#     def post(self, request):
#         extension_digit = request.data.get("extension_digit")
#         company_prefix = request.data.get("company_prefix")

#         if not (extension_digit and extension_digit.isdigit() and len(extension_digit) == 1):
#             return Response({"error": "Invalid extension digit"}, status=status.HTTP_400_BAD_REQUEST)
#         if not (company_prefix and company_prefix.isdigit()):
#             return Response({"error": "Invalid company prefix"}, status=status.HTTP_400_BAD_REQUEST)

#         # Total 17 digits before check digit
#         max_base_length = 17
#         fixed_part_length = len(extension_digit) + len(company_prefix)
#         serial_length = max_base_length - fixed_part_length

#         if serial_length <= 0:
#             return Response({"error": "Company prefix too long"}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate random serial reference of required length
#         serial_reference = ''.join(random.choices('0123456789', k=serial_length))

#         base_sscc = extension_digit + company_prefix + serial_reference
#         check_digit = calculate_check_digit(base_sscc)
#         full_sscc = base_sscc + check_digit
#         gs1_data = f"(00){full_sscc}"

#         writer_options = {
#         "font_size": 3,             # Very small text
#         "text_distance": 3.0,       # Text very close to bars
#         "quiet_zone": 0.2,          # Minimal whitespace around barcode
#         "module_width": 0.1,       # Thinnest possible bars while maintaining scan-ability
#         "module_height": 8.0,       # Very short barcode height
#         "write_text": True
#           }

#         ean = barcode.get_barcode_class('code128')
#         buffer = io.BytesIO()
#         ean(gs1_data, writer=ImageWriter()).write(buffer, options=writer_options)
#         buffer.seek(0)

#         filename = f"sscc_{full_sscc}.png"
#         content_file = ContentFile(buffer.read(), name=filename)

#         barcode_record, created = SSCCBarcode.objects.get_or_create(
#             full_sscc=full_sscc,
#             defaults={
#                 'extension_digit': extension_digit,
#                 'company_prefix': company_prefix,
#                 'serial_reference': serial_reference,
#                 'check_digit': check_digit,
#                 'barcode_image': content_file,
#             }
#         )

#         if not created and not barcode_record.barcode_image:
#             barcode_record.barcode_image.save(filename, content_file, save=True)

#         image_url = barcode_record.barcode_image.url

#         return Response({
#             "sscc": full_sscc,
#             "image_url": image_url
#         }, status=status.HTTP_201_CREATED)

# def calculate_check_digit(number: str) -> str:
#     total = 0
#     reverse_digits = number[::-1]
#     for i, digit in enumerate(reverse_digits):
#         n = int(digit)
#         total += n * 3 if i % 2 == 0 else n
#     return str((10 - (total % 10)) % 10)




@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
class ServeQRGenerate(APIView):
    """
    Serve the QR/barcode image file from static/bin_ids/<filename>.
    """

    def get(self, request, filename):
        file_path = os.path.join('media', 'sscc_barcodes', filename)
        print("Serving image from:", file_path)  

        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='image/png')
        else:
            raise Http404("Image not found")


#sgtin barcode generation
import calendar
from datetime import datetime
# class GenerateSGTINBarcode(APIView):
#     def post(self, request):
#         gtin = request.data.get("gtin")     # 14 digits
#         expiry = request.data.get("expiry") # YYMMDD format (6 digits)
#         print("---expiry---",expiry)
#         if not re.match(r"^\d{4}-\d{2}$", expiry or ""):
#             return Response({"error": "Expiry must be in 'YYYY-MM' format"}, status=status.HTTP_400_BAD_REQUEST)
#         serial = request.data.get("serial") # Alphanumeric

#         if not gtin or not expiry or not serial:
#             return Response(
#                 {"error": "Missing one or more required fields: gtin, expiry, serial"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if len(gtin) != 14 or not gtin.isdigit():
#             return Response({"error": "GTIN must be a 14-digit number"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Parse the date assuming YYYY-MM format
#             year, month = map(int, expiry.split('-'))
#             # last_day = calendar.monthrange(year, month)[1]# Get last day of the month
#             last_day="00"
#             print("--last day--",last_day)
#             expiry_date = datetime(year, month, last_day)
#             print("--expiry date--",expiry_date)
#             expiry_gs1 = expiry_date.strftime("%y%m%d")  # Format as YYMMDD (GS1)
#             print("--expiry gs1--",expiry_gs1)
#         except Exception as e:
#             return Response({"error": "Expiry must be in 'YYYY-MM' format"}, status=status.HTTP_400_BAD_REQUEST)

#         gs1_sgtin = f"(01){gtin}(17){expiry_gs1}(10){serial}"
#         print("--gs1_sgtin--",gs1_sgtin)

#         writer_options = {
#         "font_size": 3,            
#         "text_distance": 3.0,       
#         "quiet_zone": 0.2,          
#         "module_width": 0.1,       
#         "module_height": 8.0,       
#         "write_text": True
#           }

#         # Generate barcode
#         ean = barcode.get_barcode_class('code128')
#         buffer = io.BytesIO()
#         ean(gs1_sgtin, writer=ImageWriter()).write(buffer, options=writer_options)
#         buffer.seek(0)

#         # Save to media
#         filename = f"sgtin_{gtin}_{serial}.png"
#         content_file = ContentFile(buffer.read(), name=filename)

#         # Create or get the database record (optional model example: SGTINBarcode)
#         barcode_record, created = SGTINBarcode.objects.get_or_create(
#             gtin=gtin,
#             serial=serial,
#             expiry=expiry,
#             defaults={'barcode_image': content_file}
#         )

#         if not created and not barcode_record.barcode_image:
#             barcode_record.barcode_image.save(filename, content_file, save=True)

#         image_url=barcode_record.barcode_image.url 
        
#         # image_url = request.build_absolute_uri(barcode_record.barcode_image.url)

#         return Response({
#             "gtin": gtin,
#             "serial": serial,
#             "expiry": expiry,
#             "image_url": image_url
#         }, status=status.HTTP_201_CREATED)


# class GenerateSGTINBarcode(APIView):
#     def post(self, request):
#         gtin = request.data.get("gtin")     # 14 digits
#         expiry = request.data.get("expiry") # Expecting 'YYYY-MM'
#         serial = request.data.get("serial") # Alphanumeric

#         # Validate expiry format first
#         if not re.match(r"^\d{4}-\d{2}$", expiry or ""):
#             return Response({"error": "Expiry must be in 'YYYY-MM' format"}, status=status.HTTP_400_BAD_REQUEST)

#         # Check required fields
#         if not gtin or not expiry or not serial:
#             return Response(
#                 {"error": "Missing one or more required fields: gtin, expiry, serial"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if len(gtin) != 14 or not gtin.isdigit():
#             return Response({"error": "GTIN must be a 14-digit number"}, status=status.HTTP_400_BAD_REQUEST)

#         # Format expiry as YYMM00 for GS1
#         try:
#             year, month = map(int, expiry.split('-'))
#             expiry_gs1 = f"{str(year)[2:]}{month:02}00"  # Format: YYMM00
#         except Exception:
#             return Response({"error": "Expiry must be in 'YYYY-MM' format"}, status=status.HTTP_400_BAD_REQUEST)

#         # Construct GS1 barcode string
#         gs1_sgtin = f"(01){gtin}(17){expiry_gs1}(10){serial}"

#         writer_options = {
#             "font_size": 3,
#             "text_distance": 3.0,
#             "quiet_zone": 0.2,
#             "module_width": 0.1,
#             "module_height": 8.0,
#             "write_text": True
#         }

#         # Generate barcode
#         ean = barcode.get_barcode_class('code128')
#         buffer = io.BytesIO()
#         ean(gs1_sgtin, writer=ImageWriter()).write(buffer, options=writer_options)
#         buffer.seek(0)

#         # Create filename (truncate serial to 30 chars to avoid DB issues)
#         safe_serial = serial[:30]
#         filename = f"sgtin_{gtin}_{safe_serial}.png"
#         content_file = ContentFile(buffer.read(), name=filename)

#         # Save to DB or retrieve existing record
#         barcode_record, created = SGTINBarcode.objects.get_or_create(
#             gtin=gtin,
#             serial=serial,
#             expiry=expiry,
#             defaults={'barcode_image': content_file}
#         )

#         if not created and not barcode_record.barcode_image:
#             barcode_record.barcode_image.save(filename, content_file, save=True)

#         image_url = barcode_record.barcode_image.url

#         return Response({
#             "gtin": gtin,
#             "serial": serial,
#             "expiry": expiry,
#             "gs1_formatted_expiry": expiry_gs1,
#             "image_url": image_url
#         }, status=status.HTTP_201_CREATED)
        
import treepoem


# Add Ghostscript path manually so treepoem can find it
os.environ["PATH"] += os.pathsep + r"C:\Program Files\gs\gs10.05.1\bin"

#pip install treepoem        
# class GenerateSGTINBarcode(APIView):
#     def post(self, request):
#         gtin = request.data.get("gtin")     # 14 digits
#         expiry = request.data.get("expiry") # Expecting 'YYYY-MM'
#         serial = request.data.get("serial") # Alphanumeric

#         # Validate expiry format
#         if not re.match(r"^\d{4}-\d{2}$", expiry or ""):
#             return Response({"error": "Expiry must be in 'YYYY-MM' format"}, status=status.HTTP_400_BAD_REQUEST)

#         if not gtin or not expiry or not serial:
#             return Response(
#                 {"error": "Missing one or more required fields: gtin, expiry, serial"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if len(gtin) != 14 or not gtin.isdigit():
#             return Response({"error": "GTIN must be a 14-digit number"}, status=status.HTTP_400_BAD_REQUEST)

#         # Format expiry as YYMM00 (GS1 format uses day but here fixed as '00')
#         try:
#             year, month = map(int, expiry.split('-'))
#             expiry_gs1 = f"{str(year)[2:]}{month:02}00"
#         except Exception:
#             return Response({"error": "Expiry must be in 'YYYY-MM' format"}, status=status.HTTP_400_BAD_REQUEST)

#         # Construct GS1 barcode string
#         gs1_sgtin = f"(01){gtin}(17){expiry_gs1}(10){serial}"

#         # try:
#         # Generate barcode using GS1-128
#         image = treepoem.generate_barcode(
#             barcode_type="gs1-128",  # Very important to use gs1-128 here
#             data=gs1_sgtin
#         )

#         # Save barcode image to memory buffer
#         buffer = io.BytesIO()
#         image.convert("1").save(buffer, format="PNG")
#         buffer.seek(0)

#         # Save barcode file
#         safe_serial = serial[:30]
#         filename = f"sgtin_{gtin}_{safe_serial}.png"
#         content_file = ContentFile(buffer.read(), name=filename)

#         barcode_record, created = SGTINBarcode.objects.get_or_create(
#             gtin=gtin,
#             serial=serial,
#             expiry=expiry,
#             defaults={'barcode_image': content_file}
#         )

#         # If it existed but no image stored, update it
#         if not created and not barcode_record.barcode_image:
#             barcode_record.barcode_image.save(filename, content_file, save=True)

#         image_url = barcode_record.barcode_image.url

#         return Response({
#             "gtin": gtin,
#             "serial": serial,
#             "expiry": expiry,
#             "gs1_formatted_expiry": expiry_gs1,
#             "image_url": image_url
#         }, status=status.HTTP_201_CREATED)

        # except Exception as e:
        #     return Response({"error": f"Barcode generation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class GenerateSGTINBarcode(APIView):
#     def post(self, request):
#         gtin = request.data.get("gtin")     # 14 digits
#         expiry = request.data.get("expiry") # 'YYYY-MM'
#         serial = request.data.get("serial") # Alphanumeric

#         # Validate fields
#         if not gtin or not expiry or not serial:
#             return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

#         if len(gtin) != 14 or not gtin.isdigit():
#             return Response({"error": "GTIN must be a 14-digit number"}, status=status.HTTP_400_BAD_REQUEST)

#         if not re.match(r"^\d{4}-\d{2}$", expiry):
#             return Response({"error": "Expiry must be in 'YYYY-MM' format"}, status=status.HTTP_400_BAD_REQUEST)

#         # Format expiry to GS1
#         year, month = map(int, expiry.split('-'))
#         expiry_gs1 = f"{str(year)[2:]}{month:02}00"

#         # GS1 readable text
#         gs1_data = f"(01){gtin}(17){expiry_gs1}(10){serial}"

#         # Raw barcode content (with FNC1 for GS1-128)
#         raw_data = f"{chr(29)}01{gtin}17{expiry_gs1}10{serial}"  # ASCII 29 = FNC1

#         # Generate barcode image
#         ean = get_barcode_class('code128')
#         # writer_options = {
#         #     'write_text': False,          # We'll draw our own text
#         #     'quiet_zone': 2.0,
#         #     'module_height': 10.0,
#         #     'module_width': 0.2,
#         # }
        
#         writer_options = {
#             'write_text': False,          # We'll draw our own text
#             'quiet_zone': 0.2,
#             'module_height': 0.1,
#             'module_width': 8.0,
#         }
        
#         # writer_options = {
#         # "font_size": 3,             # Very small text
#         # "text_distance": 3.0,       # Text very close to bars
#         # "quiet_zone": 0.2,          # Minimal whitespace around barcode
#         # "module_width": 0.1,       # Thinnest possible bars while maintaining scan-ability
#         # "module_height": 8.0,       # Very short barcode height
#         # "write_text": True
#         # }

#         barcode_obj = ean(raw_data, writer=ImageWriter())
#         buffer = io.BytesIO()
#         barcode_obj.write(buffer, options=writer_options)
#         buffer.seek(0)

#         # Open image
#         barcode_img = Image.open(buffer)

#         # Prepare to add text
#         # font = ImageFont.load_default()
#         font = ImageFont.truetype("arial.ttf", size=18)
#         draw = ImageDraw.Draw(barcode_img)
#         bbox = draw.textbbox((0, 0), gs1_data, font=font)
#         text_width = bbox[2] - bbox[0]
#         text_height = bbox[3] - bbox[1]

#         # Create new image with space for text
#         new_img = Image.new('RGB', (barcode_img.width, barcode_img.height + text_height + 10), "white")
#         new_img.paste(barcode_img, (0, 0))

#         draw = ImageDraw.Draw(new_img)
#         draw.text(((new_img.width - text_width) // 2, barcode_img.height + 5), gs1_data, fill="black", font=font)

#         # Save to final buffer
#         final_buffer = io.BytesIO()
#         new_img.save(final_buffer, format="PNG")
#         final_buffer.seek(0)

#         filename = f"sgtin_{gtin}_{serial[:30]}.png"
#         content_file = ContentFile(final_buffer.read(), name=filename)

#         # Save or update DB entry
#         barcode_record, created = SGTINBarcode.objects.get_or_create(
#             gtin=gtin,
#             serial=serial,
#             expiry=expiry,
#             defaults={'barcode_image': content_file}
#         )

#         if not created and not barcode_record.barcode_image:
#             barcode_record.barcode_image.save(filename, content_file, save=True)

#         return Response({
#             "gtin": gtin,
#             "serial": serial,
#             "expiry": expiry,
#             "gs1_formatted_expiry": expiry_gs1,
#             "image_url": barcode_record.barcode_image.url
#         }, status=status.HTTP_201_CREATED)

class GenerateSGTINBarcode(APIView):
    def post(self, request):
        gtin = request.data.get("gtin")     # 14 digits
        expiry = request.data.get("expiry") # 'YYYY-MM'
        serial = request.data.get("serial") # Alphanumeric

        # Validate fields
        if not gtin or not expiry or not serial:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        if len(gtin) != 14 or not gtin.isdigit():
            return Response({"error": "GTIN must be a 14-digit number"}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r"^\d{4}-\d{2}$", expiry):
            return Response({"error": "Expiry must be in 'YYYY-MM' format"}, status=status.HTTP_400_BAD_REQUEST)

        # Format expiry to GS1
        year, month = map(int, expiry.split('-'))
        expiry_gs1 = f"{str(year)[2:]}{month:02}00"

        # GS1 readable text
        gs1_data = f"(01){gtin}(17){expiry_gs1}(10){serial}"

        # Raw barcode content (with FNC1 for GS1-128)
        raw_data = f"{chr(29)}01{gtin}17{expiry_gs1}10{serial}"  # ASCII 29 = FNC1

        # Generate barcode image
        ean = get_barcode_class('code128')
        writer_options = {
            'write_text': False,          # We'll draw our own text
            'quiet_zone': 1.0,
            'module_height': 8.0,
            'module_width': 0.15,
        }
        
        # writer_options = {
        #     'write_text': False,          # We'll draw our own text
        #     'quiet_zone': 0.2,
        #     'module_height': 0.1,
        #     'module_width': 8.0,
        # }
        
        # writer_options = {
        # "font_size": 3,             # Very small text
        # "text_distance": 3.0,       # Text very close to bars
        # "quiet_zone": 0.2,          # Minimal whitespace around barcode
        # "module_width": 0.1,       # Thinnest possible bars while maintaining scan-ability
        # "module_height": 8.0,       # Very short barcode height
        # "write_text": True
        # }

        barcode_obj = ean(raw_data, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer, options=writer_options)
        buffer.seek(0)

        # Open image
        barcode_img = Image.open(buffer)

        # Prepare to add text
        # font = ImageFont.load_default()
        font = ImageFont.truetype("arial.ttf", size=18)
        draw = ImageDraw.Draw(barcode_img)
        bbox = draw.textbbox((0, 0), gs1_data, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Create new image with space for text
        new_img = Image.new('RGB', (barcode_img.width, barcode_img.height + text_height + 10), "white")
        new_img.paste(barcode_img, (0, 0))

        draw = ImageDraw.Draw(new_img)
        draw.text(((new_img.width - text_width) // 2, barcode_img.height + 5), gs1_data, fill="black", font=font)

        # Save to final buffer
        final_buffer = io.BytesIO()
        new_img.save(final_buffer, format="PNG")
        final_buffer.seek(0)

        filename = f"sgtin_{gtin}_{serial[:30]}.png"
        content_file = ContentFile(final_buffer.read(), name=filename)

        # Save or update DB entry
        barcode_record, created = SGTINBarcode.objects.get_or_create(
            gtin=gtin,
            serial=serial,
            expiry=expiry,
            defaults={'barcode_image': content_file}
        )

        if not created and not barcode_record.barcode_image:
            barcode_record.barcode_image.save(filename, content_file, save=True)

        return Response({
            "gtin": gtin,
            "serial": serial,
            "expiry": expiry,
            "gs1_formatted_expiry": expiry_gs1,
            "image_url": barcode_record.barcode_image.url
        }, status=status.HTTP_201_CREATED)

        
        
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
class ServeBarcodeSGTINGenerate(APIView):
    """
    Serve the QR/barcode image file from media/sgtin_barcodes/<filename>.
    """

    def get(self, request, filename):
        file_path = os.path.join('media', 'sgtin_barcodes', filename)
        print("Serving image from:", file_path)  

        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='image/png')
        else:
            raise Http404("Image not found")


#pip install python-barcode pillow

# class GenerateSSCCBarcode(APIView):
#     def post(self, request):
#         sscc = request.data.get("sscc")  # e.g., 189012130024004573
#         if not sscc or len(sscc) != 18:
#             return Response({"error": "Invalid SSCC. Must be 18 digits."}, status=status.HTTP_400_BAD_REQUEST)

#         gs1_sscc = f"(00){sscc}"

#         ean = barcode.get_barcode_class('code128')
#         buffer = io.BytesIO()
#         ean(gs1_sscc, writer=ImageWriter()).write(buffer)

#         buffer.seek(0)
#         return FileResponse(buffer, content_type='image/png')


# class GenerateSGTINBarcode(APIView):
#     def post(self, request):
#         gtin = request.data.get("gtin")     # e.g., 58901213080292 (14 digits)
#         expiry = request.data.get("expiry") # e.g., 261000
#         serial = request.data.get("serial") # e.g., 0374MA054

#         if not gtin or not expiry or not serial:
#             return Response({"error": "Missing one or more required fields: gtin, expiry, serial"}, status=status.HTTP_400_BAD_REQUEST)

#         gs1_sgtin = f"(01){gtin}(17){expiry}(10){serial}"

#         ean = barcode.get_barcode_class('code128')
#         buffer = io.BytesIO()
#         ean(gs1_sgtin, writer=ImageWriter()).write(buffer)

#         buffer.seek(0)
#         return FileResponse(buffer, content_type='image/png')


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
        gs1_data = f"(00){full_sscc}"

        # Generate GS1-128 barcode using treepoem
        barcode_image = treepoem.generate_barcode(
            barcode_type="gs1-128",
            data=gs1_data,
            options={"includetext": True}
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


########################### DASHBOARD BEGIN ##############################

#count of the total products(from product_master table)
class GtinCountAPIView(APIView):
    def get(self, request):
        try:
            # Count distinct GTINs from ProductMaster table
            gtin_count = ProductMaster.objects.using('default').values('gtin').distinct().count()
            
            if gtin_count == 0:
                return Response({
                    'status': 0,
                    'message': 'No products found in the system'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'status': 1,
                'total_product': gtin_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 0,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#count of the business partners(from user_details table)
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


class CustomerCountAPIView(APIView):
    def get(self, request):
        try:
            # Count total customers from user_details table
            customer_count = customer_master.objects.using('default').count()
            
            if customer_count == 0:
                return Response({
                    'status': 0,
                    'message': 'No customers found in the system'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'status': 1,
                'total_customers': customer_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 0,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsersCountAPIView(APIView):
    def get(self, request):
        try:
            # Count total users from user_details table
            user_count = user_details.objects.using('default').count()
            
            if user_count == 0:
                return Response({
                    'status': 0,
                    'message': 'No users found in the system'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'status': 1,
                'total_users': user_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 0,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SupplierCountAPIView(APIView):
    def get(self, request):
        try:
            # Count total users from user_details table
            supplier_count = vendor_master.objects.using('default').count()
            
            if supplier_count == 0:
                return Response({
                    'status': 0,
                    'message': 'No Supplier found in the system'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'status': 1,
                'total_suppliers': supplier_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 0,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




class DashSupplierListAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC dash_ven_list")
            columns = [col[0] for col in cursor.description]
            dash_ven_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'dash_ven_data': dash_ven_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class TotalCommissionCountSGTIN(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            vend_id = data['vend_id']

            cursor = connection.cursor()
            cursor.execute("EXEC dash_totalcommissionsgtincount %s", [vend_id])
            columns = [col[0] for col in cursor.description]
            total_com_count = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'total_com_count': total_com_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommissionedSGTINCountAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC dash_commissionsgtincount")
            columns = [col[0] for col in cursor.description]
            com_gtin_coount = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'com_gtin_coount': com_gtin_coount}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DashCustomerListAPIView(APIView):
    def get(self, request):
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC dash_cust_list")
            columns = [col[0] for col in cursor.description]
            dash_cus_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'dash_cus_data': dash_cus_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TotalShippingCountSSCC(APIView):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            cus_id = data['cus_id'] 

            cursor = connection.cursor()
            cursor.execute("EXEC dash_shipping_count %s", [cus_id])
            # cursor.execute("EXEC dash_shipping_count")
            columns = [col[0] for col in cursor.description]
            total_ship_count = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'total_ship_count': total_ship_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TotalReceivedCountSSCC(APIView):
    def post(self, request):
        try:
            # body_unicode = request.body.decode('utf-8')
            # data = json.loads(body_unicode)

            # ven_id = data['ven_id'] 

            cursor = connection.cursor()
            # cursor.execute("EXEC dash_received_count %s", [ven_id])
            cursor.execute("EXEC dash_received_count")
            columns = [col[0] for col in cursor.description]
            total_receive_count = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({'total_receive_count': total_receive_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


######### DASHBOARD END ##########



#add company details

class AddCompanyDetailsAPIView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Extract all fields (required + optional)
            business_type=data.get("business_type","").strip()
            sub_type=data.get("sub_type","").strip()
            company_name = data.get("company_name", "").strip()
            gln = data.get("GLN", "").strip()
            company_prefix = data.get("company_prefix", "").strip()
            contact_no = data.get("ContactNo", "").strip()
            location_type = data.get("LocationType", "").strip()
            location_name = data.get("LocationName", "").strip()
            account_alias = data.get("account_alias", "").strip()
            email = data.get("email", "").strip()
            postal_code = data.get("postal_code", "").strip()
            street = data.get("street", "").strip()
            country_code = data.get("country_code", "").strip()
            city = data.get("city", "").strip()
            region = data.get("region", "").strip()
            gps_coordinates = data.get("gps_coordinates", "").strip()
            area = data.get("area", "").strip()

            # Validate required fields
            required_fields = {
                "Business Type":business_type,
                "Company Name": company_name,
                "GLN": gln,
                "Company Prefix": company_prefix,
                "Contact Number": contact_no,
                "Location Type": location_type,
                "Location Name": location_name
            }
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                return Response(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check duplicate
            if CompanyDetails.objects.filter(company_name=company_name, GLN=gln, status=1).exists():
                return Response({"error": "Company already exists"}, status=status.HTTP_400_BAD_REQUEST)

            # Call stored procedure with all fields
            with connection.cursor() as cursor:
                cursor.execute("""
                    EXEC add_company_details 
                        @business_type=%s,
                        @sub_type=%s,
                        @company_name=%s,
                        @account_alias=%s,
                        @GLN=%s,
                        @company_prefix=%s,
                        @email=%s,
                        @ContactNo=%s,
                        @LocationName=%s,
                        @LocationType=%s,
                        @postal_code=%s,
                        @street=%s,
                        @country_code=%s,
                        @city=%s,
                        @region=%s,
                        @gps_coordinates=%s,
                        @area=%s
                """, [
                    business_type,sub_type,company_name, account_alias, gln, company_prefix, email, contact_no,
                    location_name, location_type, postal_code, street,
                    country_code, city, region, gps_coordinates, area
                ])

            return Response({"message": "Company details added successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanyDetailsListAPIView(APIView):
    def get(self, request):
        try:
            # Fetch active company records
            companies = CompanyDetails.objects.using('default').filter(status=1).values(
                'business_type', 'sub_type', 'company_name', 'GLN', 'company_prefix', 'ContactNo',
                'LocationType', 'LocationName', 'account_alias',
                'email', 'postal_code', 'street', 'country_code',
                'city', 'region', 'gps_coordinates', 'area',
            )

            if not companies:
                return Response({
                    "status": 0,
                    "message": "No company details found"
                }, status=status.HTTP_404_NOT_FOUND)

            processed_companies = []
            for company in companies:
                cleaned = {}
                for key, value in company.items():
                    # Format business_type as "business_type - sub_type"
                    if key == "business_type":
                        business = value or "N/A"
                        sub = company.get("sub_type") or "N/A"
                        cleaned["business_type"] = f"{business} - {sub}"
                    elif key == "sub_type":
                        continue  # Already handled above
                    else:
                        cleaned[key] = value if value not in [None, ""] else "N/A"
                processed_companies.append(cleaned)

            return Response({
                "status": 1,
                "companies": processed_companies
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UpdateCompanyDetailsAPIView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Required ID for update
            company_id = data.get("company_id")
            if not company_id:
                return Response({"error": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the record exists and is active
            if not CompanyDetails.objects.using('default').filter(id=company_id, status=1).exists():
                return Response({"error": "Company not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

            # Extract all fields with default empty strings if not provided
            company_name = data.get("company_name", "")
            account_alias = data.get("account_alias", "")
            gln = data.get("GLN", "")
            company_prefix   = data.get("company_prefix", "")
            email            = data.get("email", "")
            contact_no       = data.get("ContactNo", "")
            location_name    = data.get("LocationName", "")
            location_type    = data.get("LocationType", "")
            postal_code      = data.get("postal_code", "")
            street           = data.get("street", "")
            country_code     = data.get("country_code", "")
            city             = data.get("city", "")
            region           = data.get("region", "")
            gps_coordinates  = data.get("gps_coordinates", "")
            area             = data.get("area", "")

            # Call stored procedure to update
            with connection.cursor() as cursor:
                cursor.execute("""
                    EXEC update_company_details 
                        @company_id=%s,
                        @company_name=%s,
                        @account_alias=%s,
                        @GLN=%s,
                        @company_prefix=%s,
                        @email=%s,
                        @ContactNo=%s,
                        @LocationName=%s,
                        @LocationType=%s,
                        @postal_code=%s,
                        @street=%s,
                        @country_code=%s,
                        @city=%s,
                        @region=%s,
                        @gps_coordinates=%s,
                        @area=%s
                """, [
                    company_id,
                    company_name,
                    account_alias,
                    gln,
                    company_prefix,
                    email,
                    contact_no,
                    location_name,
                    location_type,
                    postal_code,
                    street,
                    country_code,
                    city,
                    region,
                    gps_coordinates,
                    area
                ])

            return Response({"message": "Company details updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteCompanyDataAPIView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            company_id = data.get("company_id")

            if not company_id:
                return Response({"error": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the record exists and is active
            if not CompanyDetails.objects.using('default').filter(id=company_id, status=1).exists():
                return Response({"error": "Company not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

            # Call stored procedure to delete
            with connection.cursor() as cursor:
                cursor.execute("EXEC delete_company_details @company_id=%s", [company_id])

            return Response({"message": "Company details deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        


class ActivateCompanyDataAPIView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            company_id = data.get("company_id")

            if not company_id:
                return Response({"error": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the record exists and is inactive
            if not CompanyDetails.objects.using('default').filter(id=company_id, status=0).exists():
                return Response({"error": "Company not found or already active"}, status=status.HTTP_404_NOT_FOUND)

            # Call stored procedure to activate
            with connection.cursor() as cursor:
                cursor.execute("EXEC activate_company @company_id=%s", [company_id])

            return Response({"message": "Company details activated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)