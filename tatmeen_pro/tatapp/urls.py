from django.urls import path
from .views import *

urlpatterns = [
    # path("token-info", token_info_view),
    
    # path("send-epcis", send_epcis_view),
    # path("dispensation", dispensation_view),
    # path("verify-product", verify_product_view),
    # path("msg-status", msg_status_query_view),
    
    #################################################
    # http://127.0.0.1:8000/test/get-token/
    path("get-token",get_tatmeen_token, name='get_tatmeen_token'),
    path('token-info', token_info_view),
    path('call_send_epcis',call_send_epcis),
    path('verify_product',verify_product),
    path('msg_status_query',msg_status_query),
    
    
    path('EventTimeTestView', EventTimeTestView.as_view(), name='event_time_test'),
    
    path('GenerateSSCCBarcode', GenerateSSCCBarcode.as_view(), name='generate_sscc_barcode'),

    path('InvoiceUploadAPIView',InvoiceUploadAPIView.as_view(),name='InvoiceUploadAPIView'),
    path('InvoiceUploadingAPIView',InvoiceUploadingAPIView.as_view(),name='InvoiceUploadingAPIView'),

    path('upload_invoice',upload_invoice,name='upload_invoice'),
 
]
