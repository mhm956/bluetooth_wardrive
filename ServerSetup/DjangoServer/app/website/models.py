from uuid import uuid4

from django.db import models


class Bluetooth(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    datetime_rx = models.DateTimeField(auto_now_add=True, blank=True)
    capture_time = models.CharField(default=None, null=True, blank=True, max_length=64)
    location = models.CharField(default=None, null=True, blank=True, max_length=64)
    ip_address = models.CharField(default=None, null=True, blank=True, max_length=64)
    mac_addr = models.CharField(default=None, null=True, blank=True, max_length=64)
    ssid = models.CharField(default=None, null=True, blank=True, max_length=64)

    class Meta:
        ordering = ['-datetime_rx']

    def __unicode__(self):
        return self.mac_addr

    def __string__(self):
        return self.mac_addr
