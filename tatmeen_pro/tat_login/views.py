from django.shortcuts import render

# Create your views here.

####################### login using wms db and tatmeen token generation ###########################
# from django.views.decorators.csrf import csrf_exempt
# from services.tatmeen_auth import get_valid_token
# from django.http import JsonResponse
# import json

# @csrf_exempt
# def api_login(request):
#     if request.method == 'POST':
#         body_unicode = request.body.decode('utf-8')
#         data = json.loads(body_unicode)
#         username = str(data.get('username'))
#         password = str(data.get('password'))

#         try:
#             check_user = userreg.objects.get(uname=username, pwd=password)

#             # Set session
#             request.session['user'] = str(check_user.uname)
#             request.session['user_id'] = str(check_user.id)
#             request.session['role'] = str(check_user.roleid)

#             # Prepare response
#             response_data = {
#                 'data': 1,
#                 'username': request.session['user'],
#                 'userid': request.session['user_id'],
#                 'role': request.session['role'],
#             }

#             # Extra logic for role 6
#             if check_user.roleid == 6:
#                 obj = userRecords.objects.filter(userName=username).first()
#                 response_data['putlist_status'] = getattr(obj, 'putlist_status', None)
#                 response_data['picklist_status'] = getattr(obj, 'picklist_status', None)

#             # 🎯 Tatmeen Token Fetch
#             try:
#                 tatmeen_token = get_valid_token()
#                 response_data['access_token'] = tatmeen_token.get('access_token')
#                 response_data['refresh_token'] = tatmeen_token.get('refresh_token')
#                 response_data['expires_at'] = tatmeen_token.get('expires_at')
#             except Exception as e:
#                 response_data['tatmeen_error'] = str(e)

#             return JsonResponse(response_data)

#         except userreg.DoesNotExist:
#             return JsonResponse({'data': 0, 'error': 'Invalid username or password'})
#         except Exception as e:
#             return JsonResponse({'data': 0, 'error': str(e)})

#     return JsonResponse({'data': 'Invalid API method'})


############################ login using APIView ###############################
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from services.tatmeen_auth import get_valid_token
from django.contrib.sessions.backends.db import SessionStore
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import usermaster
# from material_inward.models import userRecords  # Adjust import path as necessary

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import usermaster, RoleMaster
import json
from admin_management.models import *
from django.utils import timezone
from datetime import date

# @method_decorator(csrf_exempt, name='dispatch')
# class APILoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         try:
#             body_unicode = request.body.decode('utf-8')
#             data = json.loads(body_unicode)

#             username = data.get('username')
#             password = data.get('password')

#             # Get user with matching uname and password
#             user = usermaster.objects.get(uname=username, pwd=password)

#             # Set session data
#             request.session['user'] = user.uname
#             request.session['user_id'] = user.id
#             request.session['role'] = user.roleid

#             # Get role name from RoleMaster
#             role_name = RoleMaster.objects.filter(id=user.roleid).values_list('RoleName', flat=True).first()

#             response_data = {
#                 'data': 1,
#                 'username': user.uname,
#                 'userid': user.id,
#                 'role_id': user.roleid,
#                 'role_name': role_name,
#             }

#             return Response(response_data)

#         except usermaster.DoesNotExist:
#             return Response({'data': 0, 'error': 'Invalid username or password'})
#         except Exception as e:
#             return Response({'data': 0, 'error': str(e)})

#     def get(self, request, *args, **kwargs):
#         return Response({'data': 'Invalid API method'})

from datetime import date

@method_decorator(csrf_exempt, name='dispatch')
class APILoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            username = data.get('username')
            password = data.get('password')

            # Check if user exists in usermaster
            try:
                user = usermaster.objects.get(uname=username, pwd=password)
            except usermaster.DoesNotExist:
                return Response({'data': 0, 'error': 'Invalid username or password'})

            # Get the role name
            role_name = RoleMaster.objects.filter(id=user.roleid).values_list('RoleName', flat=True).first()

            # If user is a normal user (roleid == 2), then check user_details
            if user.roleid == 2:
                try:
                    user_detail = user_details.objects.get(username=username)
                except user_details.DoesNotExist:
                    return Response({'data': 0, 'error': 'User details not found'})

                if date.today() >= user_detail.login_validity_date:
                    user.working_status = 0
                    user.save()
                    return Response({'data': 0, 'error': 'Login validity has expired. Please contact support.'})

                # Update login status in user_details
                user_detail.logged_in_status = 1
                user_detail.save()

            # Update login status in usermaster for everyone
            user.logged_in_status = 1
            user.save()

            # Set session data
            request.session['user'] = user.uname
            request.session['user_id'] = user.id
            request.session['role'] = user.roleid

            response_data = {
                'data': 1,
                'username': user.uname,
                'userid': user.id,
                'role_id': user.roleid,
                'role_name': role_name,
            }

            return Response({"message": "Login successful", "response_data": response_data})

        except Exception as e:
            return Response({'data': 0, 'error': str(e)})

    def get(self, request, *args, **kwargs):
        return Response({'data': 'Invalid API method'})




@method_decorator(csrf_exempt, name='dispatch')
class APILogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            username = request.session.get('user')

            # Update logged_in_status to 0 for both tables
            if username:
                usermaster.objects.filter(uname=username).update(logged_in_status=0)
                user_details.objects.filter(username=username).update(logged_in_status=0)

            # Clear session
            request.session.flush()

            return Response({'message': 'User logged out successfully'})
        except Exception as e:
            return Response({'error': str(e)})
