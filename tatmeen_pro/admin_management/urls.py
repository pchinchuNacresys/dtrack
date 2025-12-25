from django.urls import path
from .views import *


urlpatterns = [
    path('RegisterUserView', RegisterUserView.as_view(), name='RegisterUserView'),
    path('UserProfileView', UserProfileView.as_view(), name='UserProfileView'),
    
    #generate barcodes
    path('GenerateSSCCBarcode', GenerateSSCCBarcode.as_view(), name='GenerateSSCCBarcode'),
    path('GenerateSGTINBarcode', GenerateSGTINBarcode.as_view(), name='GenerateSGTINBarcode'),
    path('ServeQRGenerate/<str:filename>/', ServeQRGenerate.as_view(), name='serve_qrgenerate'),
    path('ServeBarcodeSGTINGenerate/<str:filename>/', ServeBarcodeSGTINGenerate.as_view(), name='serve_barcodesgtingenerate'),

    path('GtinCountAPIView', GtinCountAPIView.as_view(), name='GtinCountAPIView'),
    path('PartnerCountAPIView', PartnerCountAPIView.as_view(), name='PartnerCountAPIView'),
    path('CustomerCountAPIView', CustomerCountAPIView.as_view(), name='CustomerCountAPIView'),
    path('UsersCountAPIView', UsersCountAPIView.as_view(), name='UsersCountAPIView'),
    path('SupplierCountAPIView',SupplierCountAPIView.as_view(),name='SupplierCountAPIView'),



    path('AddCompanyDetailsAPIView', AddCompanyDetailsAPIView.as_view(), name='AddCompanyDetailsAPIView'),
    path('CompanyDetailsListAPIView', CompanyDetailsListAPIView.as_view(), name='CompanyDetailsListAPIView'),
    path('UpdateCompanyDetailsAPIView', UpdateCompanyDetailsAPIView.as_view(), name='UpdateCompanyDetailsAPIView'),
    path('DeleteCompanyDataAPIView', DeleteCompanyDataAPIView.as_view(), name='DeleteCompanyDataAPIView'),

    path('UserDataAPIView', UserDataAPIView.as_view(), name='UserDataAPIView'),
   path('ActivateCompanyDataAPIView', ActivateCompanyDataAPIView.as_view(), name='ActivateCompanyDataAPIView'),

   path('UpdateUsernameAPIView', UpdateUsernameAPIView.as_view(), name='UpdateUsernameAPIView'),
   path('UpdatePasswordRemoteAPIView', UpdatePasswordRemoteAPIView.as_view(), name='UpdatePasswordRemoteAPIView'),

   path('DeleteUserDetailsAPIView', DeleteUserDetailsAPIView.as_view(), name='DeleteUserDetailsAPIView'),
   path('UpdateUserDetailsAPIView', UpdateUserDetailsAPIView.as_view(), name='UpdateUserDetailsAPIView'),

   path('CommissionedSGTINCountAPIView', CommissionedSGTINCountAPIView.as_view(), name='CommissionedSGTINCountAPIView'),

   #dashboard
   path('DashSupplierListAPIView', DashSupplierListAPIView.as_view(), name='DashSupplierListAPIView'),
   path('TotalCommissionCountSGTIN', TotalCommissionCountSGTIN.as_view(), name='TotalCommissionCountSGTIN'),

   path('DashCustomerListAPIView', DashCustomerListAPIView.as_view(), name='DashCustomerListAPIView'),
   path('TotalShippingCountSSCC', TotalShippingCountSSCC.as_view(), name='TotalShippingCountSSCC'),

   path('TotalReceivedCountSSCC', TotalReceivedCountSSCC.as_view(), name='TotalReceivedCountSSCC'),

 
] 