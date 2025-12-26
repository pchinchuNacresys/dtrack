from django.db import models

# Create your models here.

class TatmeenLocalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using("default") # to get the default database


class UniqueIdentifier(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(UniqueIdentifier, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(UniqueIdentifier, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'UniqueIdentifier'

        
        
class vendor_master(models.Model):
    id = models.IntegerField(primary_key=True)
    vendor_name = models.CharField(max_length=200)
    GLN=models.CharField(max_length=13)
    CompanyPrefix = models.CharField(max_length=20)
    SGLN=models.CharField(max_length=100)
    shipmentpermit=models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    contact_no = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    created_date = models.DateTimeField()
    status = models.IntegerField()
    updated_date = models.DateTimeField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(vendor_master, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(vendor_master, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'vendor_master'
        

class ProductMaster(models.Model):
    product_id = models.AutoField(primary_key=True)  
    product_name = models.CharField(max_length=250)
    gtin = models.CharField(max_length=14)
    sgtin=models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=13)
    country_origin = models.CharField(max_length=200)
    product_form = models.CharField(max_length=100)
    uom = models.CharField(max_length=50)
    created_date = models.DateTimeField()
    status = models.IntegerField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ProductMaster, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ProductMaster, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'product_master'


class serail_id(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-increment ID
    sequence = models.IntegerField()  # Stores  sequence (00, 01, 02, ...)
    status = models.IntegerField(default=0) 
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(serail_id, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(serail_id, self).delete(*args, **kwargs)
    
    class Meta:
        db_table='serail_id'


class CommissioningSGTINProducts(models.Model):
    id = models.AutoField(primary_key=True)  
    sender_gln = models.CharField(max_length=13)
    receiver_gln = models.CharField(max_length=13)
    product_gtin = models.CharField(max_length=255)
    instance_id = models.CharField(max_length=40)
    lot_number = models.CharField(max_length=64)
    expiration_date = models.DateField()
    manufacturing_date = models.DateField()
    shipment_permit = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    sgln = models.CharField(max_length=128)
    sgtin = models.CharField(max_length=100)  # one per row
    created_date = models.DateTimeField(auto_now_add=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(CommissioningSGTINProducts, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(CommissioningSGTINProducts, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'CommissioningSGTINProducts'
        

class CommissioningShipperCases(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=13)
    receiver_gln = models.CharField(max_length=13)
    product_gtin = models.CharField(max_length=255)
    instance_id = models.CharField(max_length=40)
    lot_number = models.CharField(max_length=64)
    expiration_date = models.DateField()
    manufacturing_date = models.DateField()
    shipment_permit = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    sgln = models.CharField(max_length=128)
    sgtin = models.CharField(max_length=100)  # one per row
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(CommissioningShipperCases, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(CommissioningShipperCases, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'CommissioningShipperCases'
        


class CommissioningSSCCProducts(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=13)  
    receiver_gln = models.CharField(max_length=13)
    instance_id = models.CharField(max_length=300)
    event_time = models.DateTimeField()  
    scanned_sscc = models.CharField(max_length=50) 
    sscc_urn = models.CharField(max_length=100) 
    sgln = models.CharField(max_length=40) 
    supplier_gln = models.CharField(max_length=13) 
    status = models.IntegerField()  
    created_date = models.DateTimeField(auto_now_add=True)
  
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(CommissioningSSCCProducts, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(CommissioningSSCCProducts, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'CommissioningSSCCProducts'


class ReceivingSSCCEvent(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=13)
    receiver_gln = models.CharField(max_length=13)
    instance_id = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=50)
    sscc_urn = models.CharField(max_length=100)
    sgln = models.CharField(max_length=100)
    supplier_gln = models.CharField(max_length=13)
    status=models.IntegerField() 
    created_at=models.DateTimeField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReceivingSSCCEvent, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReceivingSSCCEvent, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'ReceivingSSCCEvent'
        
        
class DecommissioningSSCCProducts(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    supplier_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=50)
    sscc_urn = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=20)
    sgln = models.CharField(max_length=100)
    reason_code = models.CharField(max_length=100)
    status = models.IntegerField()  
    created_date = models.DateTimeField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DecommissioningSSCCProducts, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DecommissioningSSCCProducts, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'DecommissioningSSCCProducts'
        
        
class ShippingSSCCProducts(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=18)
    supplier_gln = models.CharField(max_length=20)
    destination_gln = models.CharField(max_length=20)
    sscc_urn = models.CharField(max_length=100)
    sender_sgln = models.CharField(max_length=100)
    destination_sgln = models.CharField(max_length=100)
    status= models.IntegerField()  
    created_date = models.DateTimeField(auto_now_add=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ShippingSSCCProducts, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ShippingSSCCProducts, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'ShippingSSCCProducts'
            

class PackingSSCCProducts(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    supplier_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    parent_sscc = models.CharField(max_length=18)
    parent_urn = models.CharField(max_length=100)
    sgln = models.CharField(max_length=100)
    gtin= models.CharField(max_length=50)
    sgtin = models.CharField(max_length=100) 
    status = models.IntegerField() 
    created_at = models.DateTimeField()
    
    objects = TatmeenLocalManager()
    
    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(PackingSSCCProducts, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(PackingSSCCProducts, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'PackingSSCCProducts'
    

class DisaggregationCS_SSCC_Event(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    company_prefix = models.CharField(max_length=20)
    scanned_gtin = models.CharField(max_length=100)  
    scanned_sscc = models.CharField(max_length=18)  
    parent_sscc_urn = models.CharField(max_length=100) 
    sgln_urn = models.CharField(max_length=100)  
    child_sgtin_urn = models.CharField(max_length=100)  
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()
    
    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DisaggregationCS_SSCC_Event, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DisaggregationCS_SSCC_Event, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'DisaggregationCS_SSCC_Event'
        
        
class DisaggregationBE_Case_Event(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    company_prefix = models.CharField(max_length=20)
    scanned_parent_gtin = models.CharField(max_length=100)  
    scanned_gtin = models.CharField(max_length=100)  
    parent_gtin_urn = models.CharField(max_length=100) 
    sgln_urn = models.CharField(max_length=100)  
    child_sgtin_urn = models.CharField(max_length=100)  
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()
    
    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DisaggregationBE_Case_Event, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DisaggregationBE_Case_Event, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'DisaggregationBE_Case_Event'
        
    
class DisaggregationEA_BE_Event(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    company_prefix = models.CharField(max_length=20)
    scanned_parent_gtin = models.CharField(max_length=100)  
    scanned_gtin = models.CharField(max_length=100)  
    parent_gtin_urn = models.CharField(max_length=100) 
    sgln_urn = models.CharField(max_length=100)  
    child_sgtin_urn = models.CharField(max_length=100)  
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()
    
    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DisaggregationEA_BE_Event, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DisaggregationEA_BE_Event, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'DisaggregationEA_BE_Event'
        
        
class AggregationEachesIntoCase(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    company_prefix = models.CharField(max_length=20)
    scanned_parent_gtin = models.CharField(max_length=100)  
    scanned_gtin = models.CharField(max_length=100)  
    parent_gtin_urn = models.CharField(max_length=100) 
    sgln_urn = models.CharField(max_length=100)  
    child_sgtin_urn = models.CharField(max_length=100)  
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()
    
    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(AggregationEachesIntoCase, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(AggregationEachesIntoCase, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'AggregationEachesIntoCase'
        

class AggregationCaseIntoPallet(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    company_prefix = models.CharField(max_length=20)
    scanned_gtin = models.CharField(max_length=100)  
    scanned_sscc = models.CharField(max_length=18)  
    parent_sscc_urn = models.CharField(max_length=100) 
    sgln_urn = models.CharField(max_length=100)  
    child_sgtin_urn = models.CharField(max_length=100)  
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()
    
    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(AggregationCaseIntoPallet, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(AggregationCaseIntoPallet, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'AggregationCaseIntoPallet'
        
        
class StolenSSCC(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    supplier_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=20)
    sscc_urn = models.CharField(max_length=100)
    sgln = models.CharField(max_length=100)
    status = models.IntegerField() 
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(StolenSSCC, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(StolenSSCC, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'StolenSSCC'
        

class ExportedSSCC(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    supplier_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=20)
    sscc_urn = models.CharField(max_length=100)
    sgln = models.CharField(max_length=100)
    status = models.IntegerField()
    created_date = models.DateTimeField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ExportedSSCC, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ExportedSSCC, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'ExportedSSCC'
        
class LostSSCC(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    supplier_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=20)
    sscc_urn = models.CharField(max_length=100)
    sgln = models.CharField(max_length=100)
    status= models.IntegerField()
    created_date = models.DateTimeField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(LostSSCC, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(LostSSCC, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'LostSSCC'
        
        
class SampleSSCC(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    supplier_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=20)
    sscc_urn = models.CharField(max_length=100)
    sgln = models.CharField(max_length=100)
    reason_code=models.CharField(max_length=100)
    status = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(SampleSSCC, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(SampleSSCC, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'SampleSSCC'
        

class ReturnReceivingSSCC(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=20)
    sscc_urn = models.CharField(max_length=100)
    sgln = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReturnReceivingSSCC, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReturnReceivingSSCC, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'ReturnReceivingSSCC'
        
        
class DispensedSSCC(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=20)
    sscc_urn = models.CharField(max_length=100)
    sgln = models.CharField(max_length=100)
    lot_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    created_date = models.DateTimeField(auto_now=True)
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DispensedSSCC, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DispensedSSCC, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'DispensedSSCC'
        

class DispensedSGTIN(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    parent_gtin= models.CharField(max_length=20)
    parent_sgtin_urn = models.CharField(max_length=100)
    sgln = models.CharField(max_length=100)
    lot_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    created_date = models.DateTimeField(auto_now=True)
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DispensedSGTIN, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(DispensedSGTIN, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'DispensedSGTIN'
        
        
class ReturnShipping(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    company_prefix = models.CharField(max_length=20)
    scanned_sscc = models.CharField(max_length=18)
    destination_gln = models.CharField(max_length=20)
    sscc_urn = models.CharField(max_length=100)
    sender_sgln = models.CharField(max_length=100)
    destination_sgln = models.CharField(max_length=100)
    reason_code = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReturnShipping, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReturnShipping, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'ReturnShipping'
        
        
class ReturnShippingCancellation(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=18)
    sscc_urn = models.CharField(max_length=100)
    sender_sgln = models.CharField(max_length=100)
    instance_identifier_reference= models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReturnShippingCancellation, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReturnShippingCancellation, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'ReturnShippingCancellation'
        
        
class ReturnReceivingCancellation(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=18)
    sscc_urn = models.CharField(max_length=100)
    sender_sgln = models.CharField(max_length=100)
    instance_identifier_reference= models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReturnReceivingCancellation, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ReturnReceivingCancellation, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'ReturnReceivingCancellation'
        

class ShippingCancellation(models.Model):
    id = models.AutoField(primary_key=True)
    sender_gln = models.CharField(max_length=20)
    receiver_gln = models.CharField(max_length=20)
    instance_id = models.CharField(max_length=100)
    event_time = models.DateTimeField()
    scanned_sscc = models.CharField(max_length=18)
    sscc_urn = models.CharField(max_length=100)
    sender_sgln = models.CharField(max_length=100)
    instance_identifier_reference= models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ShippingCancellation, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(ShippingCancellation, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'ShippingCancellation'



class customer_master(models.Model):
    id = models.IntegerField(primary_key=True)
    customer_name = models.CharField(max_length=200)
    customerGLN=models.CharField(max_length=13)
    customerCompanyPrefix = models.CharField(max_length=20)
    customerSGLN=models.CharField(max_length=100)
    customershipmentpermit=models.CharField(max_length=100)
    customeraddress = models.CharField(max_length=300)
    customercity = models.CharField(max_length=50)
    customerprovince = models.CharField(max_length=50)
    customercountry = models.CharField(max_length=50)
    customercontact_no = models.CharField(max_length=50)
    customeremail = models.CharField(max_length=100)
    status = models.IntegerField(default=1)  # 1 for active, 0 for inactive
    created_date = models.DateTimeField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(customer_master, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(customer_master, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'customer_master'
        
        
class VerifiedProductMapping(models.Model):
    id = models.IntegerField(primary_key=True)
    scanned_sscc = models.CharField(max_length=50)
    sscc_urn = models.CharField(max_length=100)
    product_id = models.CharField(max_length=100)
    gln = models.CharField(max_length=100)
    location_name = models.CharField(max_length=255)
    regulation_authority = models.CharField(max_length=255)
    regulation_license = models.CharField(max_length=255)
    geo_latitude = models.CharField(max_length=50)
    geo_longitude = models.CharField(max_length=50)
    product_description = models.TextField()
    lot_number = models.CharField(max_length=100)
    date_of_manufacture = models.DateField()
    date_of_expiry = models.DateField()
    product_status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(VerifiedProductMapping, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(VerifiedProductMapping, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'VerifiedProductMapping'


class TempReceiveScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)  
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReceiveScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReceiveScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempReceiveScanDetails'


class receiving_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'receiving_guid_map'



class TatmeenLogs(models.Model):
    id = models.AutoField(primary_key=True)
    InstanceIdentifier = models.CharField(max_length=255)
    MessageStatus = models.CharField(max_length=100)
    LogType = models.CharField(max_length=1)
    LogMessage = models.TextField()
    CreatedAt = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'TatmeenLogs'


class TempCommSSCCScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempCommSSCCScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempCommSSCCScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempCommSSCCScanDetails'


class commision_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    cm_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'commision_guid_map'


class TempShippingScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    DestinationGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    destination_sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempShippingScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempShippingScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempShippingScanDetails'


class shipping_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    sh_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'shipping_guid_map'


class pack_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    pk_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'pack_guid_map'


class TempDeCommSSCCScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    ReasonCode= models.CharField(max_length=100)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)       
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempDeCommSSCCScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempDeCommSSCCScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempDeCommSSCCScanDetails'


class decommission_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    dcom_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'decommission_guid_map'





class TempStolenScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempStolenScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempStolenScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempStolenScanDetails'



class stolen_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    st_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'stolen_guid_map'



class TempExportedScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempExportedScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempExportedScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempExportedScanDetails'


class exported_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    ex_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'exported_guid_map'


class TempLostScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempLostScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempLostScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempLostScanDetails'


class lost_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    lt_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'lost_guid_map'


class TempSampleScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempSampleScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempSampleScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempSampleScanDetails'


class sample_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    sa_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'sample_guid_map'



class TempSampleScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    reason_code=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempSampleScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempSampleScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempSampleScanDetails'



class return_rec_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    rr_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python
    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)
    class Meta:
        db_table = 'return_rec_guid_map'
        
        
class TempDispenseSSCCScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)  
    sgln=models.CharField(max_length=100)
    lot_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempDispenseSSCCScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempDispenseSSCCScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempDispenseSSCCScanDetails'


        
class dispense_guid_sscc(models.Model):
    id = models.AutoField(primary_key=True)
    dsscc_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'dispense_guid_sscc'


class TempDispenseSGTINScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    gtin=models.CharField(max_length=20)
    sgtin=models.CharField(max_length=200)  
    sgln=models.CharField(max_length=100)
    lot_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempDispenseSGTINScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempDispenseSGTINScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempDispenseSGTINScanDetails'


class dispense_guid_sgtin(models.Model):
    id = models.AutoField(primary_key=True)
    dsgtin_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'dispense_guid_sgtin'


class TempReturnShippingScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    DestinationGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    destination_sgln=models.CharField(max_length=100)
    reason_code=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReturnShippingScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReturnShippingScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempReturnShippingScanDetails'


class return_shipping_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    rs_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'return_shipping_guid_map'


# unpacking 

class unpack_guid_sscc(models.Model):
    id = models.AutoField(primary_key=True)
    usscc_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'unpack_guid_sscc'
        
        

class commision_guid_sgtin(models.Model):
    id = models.AutoField(primary_key=True)
    cmsgtin_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'commision_guid_sgtin'
        

class commision_guid_aggregation(models.Model):
    id = models.AutoField(primary_key=True)
    cma_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'commision_guid_aggregation'



class shipping_cancel_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    sc_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'shipping_cancel_guid_map'



class return_shipping_cancel_guid(models.Model):
    id = models.AutoField(primary_key=True)
    rsc_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'return_shipping_cancel_guid'
        
        
class return_rec_cancel_guid_map(models.Model):
    id = models.AutoField(primary_key=True)
    rrc_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'return_rec_cancel_guid_map'


class unpack_guid_case(models.Model):
    id = models.AutoField(primary_key=True)
    ucase_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'unpack_guid_case'



class TempReturnReceiveScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReturnReceiveScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReturnReceiveScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempReturnReceiveScanDetails'
        
        
class commision_guid_shippercase(models.Model):
    id = models.AutoField(primary_key=True)
    cmsh_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures deletion in default DB
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'commision_guid_shippercase'


class unpack_guid_ba(models.Model):
    id = models.AutoField(primary_key=True)
    uba_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'unpack_guid_ba'



class TempShippingCancellationScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    ShippingReference=models.CharField(max_length=255)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempShippingCancellationScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempShippingCancellationScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempShippingCancellationScanDetails'
        
        
class TempReturnShippingCancelScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    ReferenceIdentifier=models.CharField(max_length=255)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReturnShippingCancelScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReturnShippingCancelScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempReturnShippingCancelScanDetails'
        
class TempReturnReceiveCancellationScanDetails(models.Model):
    ScanID = models.AutoField(primary_key=True)
    UUID=models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20)
    ReceiverGLN = models.CharField(max_length=20)
    SupplierGLN = models.CharField(max_length=20)
    ShippingReference=models.CharField(max_length=255)
    EventTime = models.DateTimeField()
    sscc_urn=models.CharField(max_length=100)
    sgln=models.CharField(max_length=100)
    rec_status=models.IntegerField() 
    created_at = models.DateTimeField()

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReturnReceiveCancellationScanDetails, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(TempReturnReceiveCancellationScanDetails, self).delete(*args, **kwargs)
    
    class Meta:
        db_table = 'TempReturnReceiveCancellationScanDetails'
        

class TempParentSSCCCommAggregationCPScanDetails(models.Model):
    ParentID = models.AutoField(primary_key=True)
    UUID = models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20, null=True, blank=True)
    ReceiverGLN = models.CharField(max_length=20, null=True, blank=True)
    SupplierGLN = models.CharField(max_length=20, null=True, blank=True)
    status = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TempParentSSCCCommAggregationCPScanDetails'

class TempAggEachesIntoCaseParentSGTIN(models.Model):
    ParentID = models.AutoField(primary_key=True)
    UUID = models.CharField(max_length=255)
    SenderGLN = models.CharField(max_length=20, null=True, blank=True)
    ReceiverGLN = models.CharField(max_length=20, null=True, blank=True)
    SupplierGLN = models.CharField(max_length=20, null=True, blank=True)
    parent_sgtin = models.CharField(max_length=200, null=True, blank=True)
    status = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TempAggEachesIntoCaseParentSGTIN'


class commision_guid_eaches(models.Model):
    id = models.AutoField(primary_key=True)
    cmeach_guid = models.CharField(max_length=300, null=True, blank=True)
    created_date = models.DateTimeField()
    status = models.IntegerField(null=True, blank=True)

    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')  # Ensures writing to default DB
        super().save(*args, **kwargs)          # Can use super() directly in modern Python

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'commision_guid_eaches'



class TempParentSSCCPackingScanDetails(models.Model):
    ParentID = models.AutoField(primary_key=True)
    UUID = models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20, null=True, blank=True)
    ReceiverGLN = models.CharField(max_length=20, null=True, blank=True)
    SupplierGLN = models.CharField(max_length=20, null=True, blank=True)
    status = models.IntegerField(default=0,null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TempParentSSCCPackingScanDetails'



class TempParentDisAggCSfromSSCCScanDetails(models.Model):
    ParentID = models.AutoField(primary_key=True)
    UUID = models.CharField(max_length=255)
    SSCC = models.CharField(max_length=18)
    SenderGLN = models.CharField(max_length=20, null=True, blank=True)
    ReceiverGLN = models.CharField(max_length=20, null=True, blank=True)
    SupplierGLN = models.CharField(max_length=20, null=True, blank=True)
    status = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TempParentDisAggCSfromSSCCScanDetails'


class TempParentDisAggBEfromCASEScan(models.Model):
    ParentID = models.AutoField(primary_key=True)
    UUID = models.CharField(max_length=255)
    SenderGLN = models.CharField(max_length=20, null=True, blank=True)
    ReceiverGLN = models.CharField(max_length=20, null=True, blank=True)
    SupplierGLN = models.CharField(max_length=20, null=True, blank=True)
    parent_sgtin = models.CharField(max_length=200, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'TempParentDisAggBEfromCASEScan'


class TempParentDisAggEAfromBEAScan(models.Model):
    parent_id = models.AutoField(primary_key=True,db_column='ParentID')
    uuid = models.CharField(max_length=255, db_column='UUID')
    sender_gln = models.CharField(max_length=20, null=True, blank=True, db_column='SenderGLN')
    receiver_gln = models.CharField(max_length=20, null=True, blank=True, db_column='ReceiverGLN')
    parent_sgtin = models.CharField(max_length=200, null=True, blank=True, db_column='parent_sgtin')
    status = models.IntegerField(default=0, null=True, db_column='status')
    created_date = models.DateTimeField(auto_now_add=True, db_column='created_date')

    class Meta:
        db_table = 'TempParentDisAggEAfromBEAScan'