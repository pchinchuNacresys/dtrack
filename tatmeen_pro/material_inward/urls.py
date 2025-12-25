from django.urls import path
from .views import *

urlpatterns = [
    path('GenerateIdentifierView', GenerateIdentifierView.as_view(), name='GenerateIdentifierView'),
    
    #add vendor details
    path('AddVendorAPIView', AddVendorAPIView.as_view(), name='AddVendorAPIView'),
    path('VendorListAPIView', VendorListAPIView.as_view(), name='VendorListAPIView'),

    path('ManufacturerListAPIView', ManufacturerListAPIView.as_view(), name='ManufacturerListAPIView'),
    path('SupplierListAPIView', SupplierListAPIView.as_view(), name='SupplierListAPIView'),

    #add product details
    path('AddProductAPIView',AddProductAPIView.as_view(),name='AddProductAPIView'),
    path('ProductListAPIView',ProductListAPIView.as_view(),name='ProductListAPIView'),
    path('CompanyPrefixAPIView',CompanyPrefixAPIView.as_view(),name='CompanyPrefixAPIView'),
    path('GtinAPIView',GtinAPIView.as_view(),name='GtinAPIView'),
    path('GtinCountAPIView',GtinCountAPIView.as_view(),name='GtinCountAPIView'),
    path('PartnerCountAPIView',PartnerCountAPIView.as_view(),name='PartnerCountAPIView'),
    path('GlnAPIView',GlnAPIView.as_view(),name='GlnAPIView'),
    path('ShipmentPermitAPIView',ShipmentPermitAPIView.as_view(),name='ShipmentPermitAPIView'),
    path('ShipmentPermitDropdownAPIView',ShipmentPermitDropdownAPIView.as_view(),name='ShipmentPermitDropdownAPIView'),
    
    path('QueryMessageStatusAPIView',QueryMessageStatusAPIView.as_view(),name='QueryMessageStatusAPIView'),
    
   
    
    
    #reason codes
    path('FetchReasonCodesAPIView',FetchReasonCodesAPIView.as_view(),name='FetchReasonCodesAPIView'),
    
    
    #### destination ####

   path('DestinationGlnAPIView',DestinationGlnAPIView.as_view(),name='DestinationGlnAPIView'),
    
    #scanning
    path('ScanSGTINView',ScanSGTINView.as_view(),name='ScanSGTINView'),
    path('ScanSSCCView',ScanSSCCView.as_view(),name='ScanSSCCView'),
     

    #get instance details
    path('GetInstanceIdAPIView',GetInstanceIdAPIView.as_view(),name='GetInstanceIdAPIView'),
    
    
    #product verification
    path('ProductVerificationAPIView',ProductVerificationAPIView.as_view(),name='ProductVerificationAPIView'),
    path('SSCCProductVerificationAPIView', SSCCProductVerificationAPIView.as_view(), name='SSCCProductVerificationAPIView'),
  

    path('AddCustomerDataAPIView', AddCustomerDataAPIView.as_view(), name='AddCustomerDataAPIView'),
    path('FetchCustomerDataAPIView', FetchCustomerDataAPIView.as_view(), name='FetchCustomerDataAPIView'),
    path('UpdateCustomerDataAPIView', UpdateCustomerDataAPIView.as_view(), name='UpdateCustomerDataAPIView'),
    path('DeleteCustomerDataAPIView', DeleteCustomerDataAPIView.as_view(), name='DeleteCustomerDataAPIView'),

    path('UpdateProductDataAPIView', UpdateProductDataAPIView.as_view(), name='UpdateProductDataAPIView'),
    path('DeleteProductDataAPIView', DeleteProductDataAPIView.as_view(), name='DeleteProductDataAPIView'),

    path('UpdateVendorListAPIView', UpdateVendorListAPIView.as_view(), name='UpdateVendorListAPIView'),
    path('DeleteVendorListAPIView', DeleteVendorListAPIView.as_view(), name='DeleteVendorListAPIView'),
 
    #Receiving 
    path('REC_GenerateIdentifierView', REC_GenerateIdentifierView.as_view(), name='REC_GenerateIdentifierView'),
    path('RecScanSSCCView', RecScanSSCCView.as_view(), name='RecScanSSCCView'),
    path('RecFetchDataAPIView', RecFetchDataAPIView.as_view(), name='RecFetchDataAPIView'),
    path('ReceiveSSCCAPIView',ReceiveSSCCAPIView.as_view(),name='ReceiveSSCCAPIView'),

    # Test Functions
    path('TestFunction', TestFunction.as_view(), name='TestFunction'),
    path('TatmeenInstanceStatusAPIView', TatmeenInstanceStatusAPIView.as_view(), name='TatmeenInstanceStatusAPIView'),

    #Commissioning
    path('COM_GenerateIdentifierView', COM_GenerateIdentifierView.as_view(), name='COM_GenerateIdentifierView'),
    path('SubmitSSCCorPalletAPIView',SubmitSSCCorPalletAPIView.as_view(),name='SubmitSSCCorPalletAPIView'),
    path('CommFetchDataAPIView', CommFetchDataAPIView.as_view(), name='CommFetchDataAPIView'),
    path('CommScanSSCCView', CommScanSSCCView.as_view(), name='CommScanSSCCView'),

    #shipping sscc
    path('SHIP_GenerateIdentifierView', SHIP_GenerateIdentifierView.as_view(), name='SHIP_GenerateIdentifierView'),
    path('ShippingScanSSCCView', ShippingScanSSCCView.as_view(), name='ShippingScanSSCCView'),
    path('ShipppingFetchDataAPIView', ShipppingFetchDataAPIView.as_view(), name='ShipppingFetchDataAPIView'),
    path('ShippingSSCCAPIView',ShippingSSCCAPIView.as_view(),name='ShippingSSCCAPIView'),

    #packing
    path('Pack_GenerateIdentifierView', Pack_GenerateIdentifierView.as_view(), name='Pack_GenerateIdentifierView'),
    path('packingParentSSCCScanView',packingParentSSCCScanView.as_view(),name='packingParentSSCCScanView'),
    path('PackScanSSCCView', PackScanSSCCView.as_view(), name='PackScanSSCCView'),
    path('PackFetchDataAPIView', PackFetchDataAPIView.as_view(), name='PackFetchDataAPIView'),
    path('PackingSSCCAPIView',PackingSSCCAPIView.as_view(),name='PackingSSCCAPIView'),
    path('PackClearDataAPIView',PackClearDataAPIView.as_view(),name='PackClearDataAPIView'),

    #decommission
    path('Decommission_GenerateIdentifierView', Decommission_GenerateIdentifierView.as_view(), name='Decommission_GenerateIdentifierView'),
    path('DecommScanSSCCView', DecommScanSSCCView.as_view(), name='DecommScanSSCCView'),
    path('DecommFetchDataAPIView', DecommFetchDataAPIView.as_view(), name='DecommFetchDataAPIView'),
    path('DecommissionSSCCAPIView',DecommissionSSCCAPIView.as_view(),name='DecommissionSSCCAPIView'),

    #stolen sscc
    path('Stolen_GenerateIdentifierView', Stolen_GenerateIdentifierView.as_view(), name='Stolen_GenerateIdentifierView'),
    path('StolenScanSSCCView', StolenScanSSCCView.as_view(), name='StolenScanSSCCView'),
    path('StolenFetchDataAPIView', StolenFetchDataAPIView.as_view(), name='StolenFetchDataAPIView'),
    path('StolenSSCCAPIView',StolenSSCCAPIView.as_view(),name='StolenSSCCAPIView'),

    #exported sscc
    path('Exported_GenerateIdentifierView', Exported_GenerateIdentifierView.as_view(), name='Exported_GenerateIdentifierView'),
    path('ExportedScanSSCCView', ExportedScanSSCCView.as_view(), name='ExportedScanSSCCView'),
    path('ExportedFetchDataAPIView', ExportedFetchDataAPIView.as_view(), name='ExportedFetchDataAPIView'),
    path('ExportedSSCCAPIView',ExportedSSCCAPIView.as_view(),name='ExportedSSCCAPIView'),


    #lost sscc
    path('Lost_GenerateIdentifierView', Lost_GenerateIdentifierView.as_view(), name='Lost_GenerateIdentifierView'),
    path('LostScanSSCCView', LostScanSSCCView.as_view(), name='LostScanSSCCView'),
    path('LostFetchDataAPIView', LostFetchDataAPIView.as_view(), name='LostFetchDataAPIView'),
    path('LostSSCCAPIView',LostSSCCAPIView.as_view(),name='LostSSCCAPIView'),

    #sample sscc
    path('Sample_GenerateIdentifierView', Sample_GenerateIdentifierView.as_view(), name='Sample_GenerateIdentifierView'),
    path('SampleScanSSCCView',SampleScanSSCCView.as_view(),name='SampleScanSSCCView'),
    path('SampleFetchDataAPIView', SampleFetchDataAPIView.as_view(), name='SampleFetchDataAPIView'),
    path('SampleSSCCAPIView',SampleSSCCAPIView.as_view(),name='SampleSSCCAPIView'),

    #return receiving
    path('ReturnRec_GenerateIdentifierView', ReturnRec_GenerateIdentifierView.as_view(), name='ReturnRec_GenerateIdentifierView'),
    path('ReturnReceivingFetchDataAPIView', ReturnReceivingFetchDataAPIView.as_view(), name='ReturnReceivingFetchDataAPIView'),
    path('RetRecScanSSCCView', RetRecScanSSCCView.as_view(), name='RetRecScanSSCCView'),
    path('ReturnReceivingAPIView',ReturnReceivingAPIView.as_view(),name='ReturnReceivingAPIView'),


    #return shipping
    path('ReturnShip_GenerateIdentifierView', ReturnShip_GenerateIdentifierView.as_view(), name='ReturnShip_GenerateIdentifierView'),
    path('ReturnShippingScanSSCCView', ReturnShippingScanSSCCView.as_view(), name='ReturnShippingScanSSCCView'),
    path('ReturnShipppingFetchDataAPIView', ReturnShipppingFetchDataAPIView.as_view(), name='ReturnShipppingFetchDataAPIView'),
    path('ReturnShippingAPIView',ReturnShippingAPIView.as_view(),name='ReturnShippingAPIView'),

    # commissioning sgtin
    path('Commission_SSGTIN_GenerateIdentifierView', Commission_SSGTIN_GenerateIdentifierView.as_view(), name='Commission_SSGTIN_GenerateIdentifierView'),
    path('CommScanSGTINView', CommScanSGTINView.as_view(), name='CommScanSGTINView'),
    
    # dispense sscc
    path('Dispense_GenerateIdentifierView_SSCC', Dispense_GenerateIdentifierView_SSCC.as_view(), name='Dispense_GenerateIdentifierView_SSCC'),
    path('DispenseScanSSCCView', DispenseScanSSCCView.as_view(), name='DispenseScanSSCCView'),
    path('DispenseFetchDataAPIView', DispenseFetchDataAPIView.as_view(), name='DispenseFetchDataAPIView'),
    path('DispenseSSCCAPIView',DispenseSSCCAPIView.as_view(),name='DispenseSSCCAPIView'),
    
    #dispense sgtin
    path('Dispense_GenerateIdentifierView_SGTIN', Dispense_GenerateIdentifierView_SGTIN.as_view(), name='Dispense_GenerateIdentifierView_SGTIN'),
    path('DispenseScanSGTINView',DispenseScanSGTINView.as_view(),name='DispenseScanSGTINView'),
    path('DispenseSGTINFetchDataAPIView',DispenseSGTINFetchDataAPIView.as_view(),name='DispenseSGTINFetchDataAPIView'),
    path('DispenseSGTINAPIView',DispenseSGTINAPIView.as_view(),name='DispenseSGTINAPIView'),
    
    
    # shipping cancellation
    path('ShippingCancel_GenerateIdentifierView',ShippingCancel_GenerateIdentifierView.as_view(),name='ShippingCancel_GenerateIdentifierView'),
    path('ShippingCancelScanSSCCView',ShippingCancelScanSSCCView.as_view(),name='ShippingCancelScanSSCCView'),
    path('ShipppingCancelFetchDataAPIView',ShipppingCancelFetchDataAPIView.as_view(),name='ShipppingCancelFetchDataAPIView'),
    path('ShippingCancellationAPIView',ShippingCancellationAPIView.as_view(),name='ShippingCancellationAPIView'),
    
    #return shipping cancellation ssccc
    path('ReturnShippingCancellation_GenerateIdentifierView', ReturnShippingCancellation_GenerateIdentifierView.as_view(), name='ReturnShippingCancellation_GenerateIdentifierView'),
    path('ReturnShippingCancelScanSSCCView',ReturnShippingCancelScanSSCCView.as_view(),name='ReturnShippingCancelScanSSCCView'),
    path('ReturnShipppingCancelFetchDataAPIView',ReturnShipppingCancelFetchDataAPIView.as_view(),name='ReturnShipppingCancelFetchDataAPIView'),
    path('ReturnShippingCancellationAPIView',ReturnShippingCancellationAPIView.as_view(),name='ReturnShippingCancellationAPIView'),
    
    #return receiving cancellation
    path('ReturnRecCancel_GenerateIdentifierView', ReturnRecCancel_GenerateIdentifierView.as_view(), name='ReturnRecCancel_GenerateIdentifierView'),
    path('ReturnReceiveCancelScanSSCCView',ReturnReceiveCancelScanSSCCView.as_view(),name='ReturnReceiveCancelScanSSCCView'),
    path('ReturnReceiveCancelFetchDataAPIView',ReturnReceiveCancelFetchDataAPIView.as_view(),name='ReturnReceiveCancelFetchDataAPIView'),
    path('ReturnReceivingCancellationAPIView',ReturnReceivingCancellationAPIView.as_view(),name='ReturnReceivingCancellationAPIView'),

    # commissioning SGTIN products
    path('Commission_SSGTIN_GenerateIdentifierView',Commission_SSGTIN_GenerateIdentifierView.as_view(),name='Commission_SSGTIN_GenerateIdentifierView'),
    path('CommScanSGTINView',CommScanSGTINView.as_view(),name='CommScanSGTINView'),
    path('CommSGTINFetchDataAPIView',CommSGTINFetchDataAPIView.as_view(),name='CommSGTINFetchDataAPIView'),
    path('SubmitEPCISAPIView',SubmitEPCISAPIView.as_view(),name='SubmitEPCISAPIView'),
    
    #commissioning Shipper cases
    path('Commission_shippercase_GenerateIdentifierView',Commission_shippercase_GenerateIdentifierView.as_view(),name='Commission_shippercase_GenerateIdentifierView'),
    path('CommScanShippercasesView',CommScanShippercasesView.as_view(),name='CommScanShippercasesView'),
    path('CommShippercasesFetchDataAPIView',CommShippercasesFetchDataAPIView.as_view(),name='CommShippercasesFetchDataAPIView'),
    path('ShipperCasesAPIView',ShipperCasesAPIView.as_view(),name='ShipperCasesAPIView'),
    
    #unpacking 
    path('Unpack_SSCC_GenerateIdentifierView', Unpack_SSCC_GenerateIdentifierView.as_view(), name='Unpack_SSCC_GenerateIdentifierView'),
    path('DisAggCSfromSSCCParentSSCCScanView',DisAggCSfromSSCCParentSSCCScanView.as_view(),name='DisAggCSfromSSCCParentSSCCScanView'),
    path('DisAggCSfromSSCCScanSSCCView',DisAggCSfromSSCCScanSSCCView.as_view(),name='DisAggCSfromSSCCScanSSCCView'),
    path('DisAggCSfromSSCCFetchDataAPIView',DisAggCSfromSSCCFetchDataAPIView.as_view(),name='DisAggCSfromSSCCFetchDataAPIView'),
    path('DisaggregationCSfromSSCCAPIView',DisaggregationCSfromSSCCAPIView.as_view(),name='DisaggregationCSfromSSCCAPIView'),
    path('DisAggCSfromSSCCClearDataAPIView',DisAggCSfromSSCCClearDataAPIView.as_view(),name='DisAggCSfromSSCCClearDataAPIView'),
    
    # unpack - DisAggregation BE from CASE
    path('Unpack_Case_GenerateIdentifierView', Unpack_Case_GenerateIdentifierView.as_view(), name='Unpack_Case_GenerateIdentifierView'),
    path('DisAggBEfromCASEScanParentSGTINView',DisAggBEfromCASEScanParentSGTINView.as_view(),name='DisAggBEfromCASEScanParentSGTINView'),
    path('DisAggBEfromCASEScanSGTINView',DisAggBEfromCASEScanSGTINView.as_view(),name='DisAggBEfromCASEScanSGTINView'),
    path('DisAggCASEFetchDataAPIView',DisAggCASEFetchDataAPIView.as_view(),name='DisAggCASEFetchDataAPIView'),
    path('DisAggCASEClearDataAPIView',DisAggCASEClearDataAPIView.as_view(),name='DisAggCASEClearDataAPIView'),
    path('DisaggregationBEfromCaseAPIView',DisaggregationBEfromCaseAPIView.as_view(),name='DisaggregationBEfromCaseAPIView'),

    
    # unpack - DIS-AGGREGATION OF 1 EA FROM BE
    path('Unpack_BA_GenerateIdentifierView', Unpack_BA_GenerateIdentifierView.as_view(), name='Unpack_BA_GenerateIdentifierView'),
    path('DisAggEAfromBEAScanParentSGTINView',DisAggEAfromBEAScanParentSGTINView.as_view(),name='DisAggEAfromBEAScanParentSGTINView'),
    path('DisAggEAfromBEAScanSGTINView',DisAggEAfromBEAScanSGTINView.as_view(),name='DisAggEAfromBEAScanSGTINView'),
    path('DisAggEAfromBEFetchDataAPIView',DisAggEAfromBEFetchDataAPIView.as_view(),name='DisAggEAfromBEFetchDataAPIView'),
    path('DisAggEAfromBEClearDataAPIView',DisAggEAfromBEClearDataAPIView.as_view(),name='DisAggEAfromBEClearDataAPIView'),
    path('DisaggregationEAfromBEAPIView',DisaggregationEAfromBEAPIView.as_view(),name='DisaggregationEAfromBEAPIView'),



    #commissioning SSCC -- SGTIN(Aggregation) case into pallet
    path('Commission_aggregation_GenerateIdentifierView',Commission_aggregation_GenerateIdentifierView.as_view(),name='Commission_aggregation_GenerateIdentifierView'),
    path('CommAggregationScanSSCCView',CommAggregationScanSSCCView.as_view(),name='CommAggregationScanSSCCView'),
    path('CommAggregationFetchDataAPIView',CommAggregationFetchDataAPIView.as_view(),name='CommAggregationFetchDataAPIView'),
    path('AggregationCaseIntoPalletAPIView',AggregationCaseIntoPalletAPIView.as_view(),name='AggregationCaseIntoPalletAPIView'),
    path('CommAggParentSSCCScanView',CommAggParentSSCCScanView.as_view(),name='CommAggParentSSCCScanView'),
    path('CommAggregationClearDataAPIView',CommAggregationClearDataAPIView.as_view(),name='CommAggregationClearDataAPIView'),

    # eaches into case 
    path('Commission_EachesIntoCase_GenerateIdentifierView',Commission_EachesIntoCase_GenerateIdentifierView.as_view(),name='Commission_EachesIntoCase_GenerateIdentifierView'),
    path('AggEachesIntoCaseScanParentSGTINView',AggEachesIntoCaseScanParentSGTINView.as_view(),name='AggEachesIntoCaseScanParentSGTINView'),
    path('AggEachesIntoCaseScanChildSGTINView',AggEachesIntoCaseScanChildSGTINView.as_view(),name='AggEachesIntoCaseScanChildSGTINView'),
    path('AggEachesIntoCaseFetchDataAPIView',AggEachesIntoCaseFetchDataAPIView.as_view(),name='AggEachesIntoCaseFetchDataAPIView'),
    path('AggEachesIntoCaseClearDataAPIView',AggEachesIntoCaseClearDataAPIView.as_view(),name='AggEachesIntoCaseClearDataAPIView'),
    path('AggregationEachesIntoCaseAPIView',AggregationEachesIntoCaseAPIView.as_view(),name='AggregationEachesIntoCaseAPIView'),

####### CLEAR

path('RecClearDataAPIView',RecClearDataAPIView.as_view(),name='RecClearDataAPIView'),
path('CommSGTINClearDataAPIView',CommSGTINClearDataAPIView.as_view(),name='CommSGTINClearDataAPIView'),
path('CommClearDataAPIView',CommClearDataAPIView.as_view(),name='CommClearDataAPIView'),
path('CommShippercasesClearDataAPIView',CommShippercasesClearDataAPIView.as_view(),name='CommShippercasesClearDataAPIView'),
path('CommAggregationClearDataAPIView',CommAggregationClearDataAPIView.as_view(),name='CommAggregationClearDataAPIView'),
path('AggEachesIntoCaseClearDataAPIView',AggEachesIntoCaseClearDataAPIView.as_view(),name='AggEachesIntoCaseClearDataAPIView'),

path('ShipppingCancelClearDataAPIView',ShipppingCancelClearDataAPIView.as_view(),name='ShipppingCancelClearDataAPIView'),
path('ReturnShipppingCancelClearDataAPIView',ReturnShipppingCancelClearDataAPIView.as_view(),name='ReturnShipppingCancelClearDataAPIView'),
path('ReturnReceiveCancelClearDataAPIView',ReturnReceiveCancelClearDataAPIView.as_view(),name='ReturnReceiveCancelClearDataAPIView'),

path('ReturnReceivingClearDataAPIView',ReturnReceivingClearDataAPIView.as_view(),name='ReturnReceivingClearDataAPIView'),
path('StolenClearDataAPIView',StolenClearDataAPIView.as_view(),name='StolenClearDataAPIView'),
path('DecommClearDataAPIView',DecommClearDataAPIView.as_view(),name='DecommClearDataAPIView'),
path('ShipppingClearDataAPIView',ShipppingClearDataAPIView.as_view(),name='ShipppingClearDataAPIView'),
path('ExportedClearDataAPIView',ExportedClearDataAPIView.as_view(),name='ExportedClearDataAPIView'),
path('LostClearDataAPIView',LostClearDataAPIView.as_view(),name='LostClearDataAPIView'),
path('DispenseClearDataAPIView',DispenseClearDataAPIView.as_view(),name='DispenseClearDataAPIView'),
path('DispenseSGTINClearDataAPIView',DispenseSGTINClearDataAPIView.as_view(),name='DispenseSGTINClearDataAPIView'),
path('SampleClearDataAPIView',SampleClearDataAPIView.as_view(),name='SampleClearDataAPIView'),
path('ReturnShipppingClearDataAPIView',ReturnShipppingClearDataAPIView.as_view(),name='ReturnShipppingClearDataAPIView'),

############# Excel uploads ##############
path('CommissionSGTINExcelUploadView',CommissionSGTINExcelUploadView.as_view(),name='CommissionSGTINExcelUploadView'),
path('ShipperCasesExcelUploadView',ShipperCasesExcelUploadView.as_view(),name='ShipperCasesExcelUploadView'),


]
