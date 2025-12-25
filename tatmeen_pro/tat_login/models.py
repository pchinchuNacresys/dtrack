from django.db import models


class TatmeenRemoteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using("remote") 
    
class TatmeenLocalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using("default")

# Create your models here.
class usermaster(models.Model):
    id = models.IntegerField(primary_key=True)
    uname = models.CharField(max_length=100)
    name = models.CharField(max_length=250)
    pwd = models.CharField(max_length=100)
    roleid = models.IntegerField()
    working_status = models.IntegerField()
    logged_in_status=models.IntegerField()
    
    objects = TatmeenRemoteManager()

    def save(self, *args, **kwargs):
        super(usermaster, self).save(using="remote", *args, **kwargs)
    def delete(self, *args, **kwargs):
        super(usermaster, self).delete(using="remote", *args, **kwargs)
        
    class Meta:
        db_table = "usermaster"
        
class RoleMaster(models.Model):
    id = models.IntegerField(primary_key=True)
    RoleName = models.CharField(max_length=100)
    created_date = models.DateTimeField()
    status = models.IntegerField()
    
    objects = TatmeenLocalManager()

    def save(self, *args, **kwargs):
        super(RoleMaster, self).save(using="default", *args, **kwargs)
    def delete(self, *args, **kwargs):
        super(RoleMaster, self).delete(using="default", *args, **kwargs)
        
    class Meta:
        db_table = "RoleMaster"