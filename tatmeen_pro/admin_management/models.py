from django.db import models

# Create your models here.

class TatmeenLocalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using("default")

class user_details(models.Model):
    id = models.AutoField(primary_key=True)
    business_partner_name = models.CharField(max_length=200)
    login_creation_date = models.DateField()
    login_validity_date = models.DateField()
    email = models.CharField(max_length=50)
    phone1 = models.CharField(max_length=20)
    phone2 = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=15)
    street = models.CharField(max_length=50)
    country_code = models.CharField(max_length=50)
    house_number = models.CharField(max_length=20)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    area = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    logged_in_status = models.IntegerField()
    status = models.IntegerField()
    created_date = models.DateTimeField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        super(user_details, self).save(using="default", *args, **kwargs)
    def delete(self, *args, **kwargs):
        super(user_details, self).delete(using="default", *args, **kwargs)
        
    class Meta:
        db_table = "user_details"
        
class UserRoleMapping(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=250)
    role_id = models.IntegerField()
    created_date = models.DateTimeField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(UserRoleMapping, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(UserRoleMapping, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = "UserRoleMapping"
        
        
class SSCCBarcode(models.Model):
    id= models.AutoField(primary_key=True)
    extension_digit = models.CharField(max_length=1)
    company_prefix = models.CharField(max_length=12)
    serial_reference = models.CharField(max_length=12)
    check_digit = models.CharField(max_length=1)
    full_sscc = models.CharField(max_length=18, unique=True)
    barcode_image = models.ImageField(upload_to='sscc_barcodes/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(SSCCBarcode, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(SSCCBarcode, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'SSCCBarcode'
        
        
class SGTINBarcode(models.Model):
    id= models.AutoField(primary_key=True)
    gtin = models.CharField(max_length=18)
    expiry = models.CharField(max_length=10)
    serial = models.CharField(max_length=100)
    barcode_image = models.ImageField(upload_to='sgtin_barcodes/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(SGTINBarcode, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('using', 'default')
        super(SGTINBarcode, self).delete(*args, **kwargs)
        
    class Meta:
        db_table = 'SGTINBarcode'


class CompanyDetails(models.Model):
    id = models.AutoField(primary_key=True)
    business_type = models.CharField(max_length=50)
    sub_type=models.CharField(max_length=50)
    company_name = models.CharField(max_length=200)
    account_alias = models.CharField(max_length=50)
    GLN = models.CharField(max_length=13)
    company_prefix = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    ContactNo = models.CharField(max_length=20)
    LocationName = models.CharField(max_length=50)
    LocationType = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=15)
    street = models.CharField(max_length=50)
    country_code = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    gps_coordinates = models.CharField(max_length=200)
    area = models.CharField(max_length=50)
    status = models.IntegerField()
    created_date = models.DateTimeField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        super(CompanyDetails, self).save(using="default", *args, **kwargs)
    def delete(self, *args, **kwargs):
        super(CompanyDetails, self).delete(using="default", *args, **kwargs)
        
    class Meta:
        db_table = "CompanyDetails"