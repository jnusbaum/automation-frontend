from django.db import models
from sensors.models import TempSensor
from devices.models import Device

class Boiler(Device):
    sensor_in = models.OneToOneField(TempSensor, related_name='+', on_delete=models.RESTRICT)
    sensor_out = models.OneToOneField(TempSensor, related_name='+', on_delete=models.RESTRICT)
    sensor_burn = models.OneToOneField(TempSensor, related_name='+', on_delete=models.RESTRICT)

    class Meta:
        verbose_name = "Boiler"
        verbose_name_plural = "Boilers"

    def as_json(self):
        dself = {'attributes': {'description': self.description},
                 'id': self.name,
                 'type': 'Boiler',
                 'self': f"/boilers/{self.name}",
                 'relationships': {'sensor_in': f"/devices/{self.sensor_in.name}",
                                   'sensor_out': f"/devices/{self.sensor_out.name}",
                                   'sensor_burn': f"/devices/{self.sensor_burn.name}"},
                 }
        return dself


class MixingValve(Device):
    sensor_sys_in = models.OneToOneField(TempSensor, related_name='+', on_delete=models.RESTRICT)
    sensor_boiler_in = models.OneToOneField(TempSensor, related_name='+', on_delete=models.RESTRICT)
    sensor_out = models.OneToOneField(TempSensor, related_name='+', on_delete=models.RESTRICT)

    class Meta:
        verbose_name = "MixingValve"
        verbose_name_plural = "MixingValves"

    def as_json(self):
        dself = {'attributes': {'description': self.description},
                 'id': self.name,
                 'type': 'MixingValve',
                 'self': f"/mixingvalves/{self.name}",
                 'relationships': {'sensor_sys_in': f"/devices/{self.sensor_sys_in.name}",
                                   'sensor_out': f"/devices/{self.sensor_out.name}",
                                   'sensor_boiler_in': f"/devices/{self.sensor_boiler_in.name}"},
                 }
        return dself


class Zone(models.Model):
    sensor_in = models.OneToOneField(TempSensor, related_name='+', on_delete=models.RESTRICT)
    sensor_out = models.OneToOneField(TempSensor, related_name='+', on_delete=models.RESTRICT)

    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"

    def as_json(self):
        dself = {'attributes': {'description': self.description},
                 'id': self.name,
                 'type': 'Zone',
                 'self': f"/zones/{self.name}",
                 'relationships': {'sensor_in': f"/devices/{self.sensor_in.name}",
                                   'sensor_out': f"/devices/{self.sensor_out.name}",}
                 }
        return dself
