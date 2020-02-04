from datetime import datetime
from decimal import *
from http import HTTPStatus

from django.http import JsonResponse, HttpResponse

from heating.models import *

MAX_TEMP_MOVE = 25
MIN_TEMP = 30


class JsonResponseNoContent(HttpResponse):
    # this is actually an HttpResponse since JsonResponse has payload by definition
    def __init__(self):
        super().__init__(status=HTTPStatus.NO_CONTENT)


class JsonResponseCreated(JsonResponse):
    def __init__(self, reason="created"):
        super().__init__(status=HTTPStatus.CREATED, data={'error': reason})


class JsonResponseNotFound(JsonResponse):
    def __init__(self, reason="not found"):
        super().__init__(status=HTTPStatus.NOT_FOUND, data={'error': reason})


class JsonResponseServerError(JsonResponse):
    def __init__(self, reason="server error"):
        super().__init__(status=HTTPStatus.INTERNAL_SERVER_ERROR, data={'error': reason})


class JsonResponseBadRequest(JsonResponse):
    def __init__(self, reason="bad request"):
        super().__init__(status=HTTPStatus.BAD_REQUEST, data={'error': reason})


def zones(request):
    if request.method == 'POST':
        try:
            zone_name = request.POST['name']
        except KeyError:
            return JsonResponseBadRequest(reason="No name parameter supplied.")
        # if POST add new zone
        try:
            Zone.objects.get(pk=zone_name)
            return JsonResponseBadRequest(reason="Zone with supplied name already exists.")
        except Zone.DoesNotExist:
            description = request.POST.get('description', default=None)
            z = Zone(name=zone_name, description=description)
            z.save()
            return JsonResponseCreated()
    else:
        # if GET return list of zones
        zns = Zone.objects.all().order_by('name')
        rzones = {'count': len(zns), 'data': [z.as_json() for z in zns]}
        return JsonResponse(data=rzones)


def zone(request, zone_name):
    try:
        z = Zone.objects.get(pk=zone_name)
    except Zone.DoesNotExist:
        return JsonResponseNotFound(reason="No Zone with the specified id was found.")
    if request.method == 'PATCH':
        # if PATCH add data for zone
        # can't change pk (name)
        try:
            z.description = request.POST['description']
            z.save()
        except KeyError:
            pass
        z.save()
        return JsonResponseNoContent()
    elif request.method == 'DELETE':
        # if DELETE delete sensor
        z.delete()
        return JsonResponseNoContent()
    else:
        # if GET get zone meta data
        rzone = {'count': 1, 'data': [z.as_json()]}
        return JsonResponse(data=rzone)


def sensors_for_zone(zone_name):
    # if GET get zone meta data
    try:
        z = Zone.objects.get(pk=zone_name)
    except Zone.DoesNotExist:
        return JsonResponseNotFound(reason="No Zone with the specified id was found.")
    # sensors for zone
    rsensors = {'count': len(z.sensors), 'data': [s.as_json for s in z.sensors]}
    return JsonResponse(data=rsensors)


def sensors(request):
    if request.method == 'POST':
        # if POST add new sensor
        z = None
        try:
            zone_name = request.POST['zone']
            try:
                z = Zone.objects.get(pk=zone_name)
            except Zone.DoesNotExist:
                return JsonResponseNotFound(reason="No Zone with the specified id was found.")
        except KeyError:
            pass
        try:
            sensor_name = request.POST['name']
        except KeyError:
            return JsonResponseBadRequest(reason="No name parameter supplied.")
        try:
            t = request.POST['type']
        except KeyError:
            return JsonResponseBadRequest(reason="No type parameter supplied.")
        address = request.POST.get('address', default=None)
        description = request.POST.get('description', default=None)

        try:
            TempSensor.objects.get(pk=sensor_name)
            return JsonResponseBadRequest(reason="TempSensor with supplied name already exists.")
        except TempSensor.DoesNotExist:
            s = TempSensor(name=sensor_name, type=t, address=address, description=description, zone=z)
            s.save()
            return JsonResponseCreated()
    else:
        # if GET return list of sensors
        snsrs = TempSensor.objects.all().order_by('name')
        rsensors = {'count': len(snsrs), 'data': [s.as_json() for s in snsrs]}
        return JsonResponse(data=rsensors)


def sensor(request, sensor_name):
    try:
        s = TempSensor.objects.get(pk=sensor_name)
    except TempSensor.DoesNotExist:
        return JsonResponseNotFound(reason="No TempSensor with the specified id was found.")
    if request.method == 'PATCH':
        # if PATCH add data for sensor
        # can't change pk (name)
        try:
            s.type = request.POST['type']
        except KeyError:
            pass
        try:
            s.address = request.POST['address']
        except KeyError:
            pass
        try:
            s.description = request.POST['description']
        except KeyError:
            pass
        try:
            zone_name = request.POST['zone']
            try:
                z = Zone.objects.get(pk=zone_name)
            except Zone.DoesNotExist:
                return JsonResponseNotFound(reason="No Zone with the specified id was found.")
            s.zone = z
        except KeyError:
            pass
        s.save()
        return JsonResponseNoContent()
    elif request.method == 'DELETE':
        # if DELETE delete sensor
        s.delete()
        return JsonResponseNoContent()
    else:
        # if GET get sensor meta data
        rsensor = {'count': 1, 'data': [s.as_json()]}
        return JsonResponse(data=rsensor)


def get_sensor_data(request, sensor):
    sdata = sensor.tempsensordata_set
    try:
        stime = request.GET['starttime']
        stime = datetime.fromisoformat(stime)
        sdata = sdata.filter(timestamp__gt=stime)
    except KeyError:
        pass
    try:
        etime = request.GET['endtime']
        etime = datetime.fromisoformat(etime)
    except KeyError:
        etime = datetime.today()
    sdata = sdata.filter(timestamp__lte=etime)
    try:
        datapts = request.GET['datapts']
        datapts = int(datapts)
    except KeyError:
        datapts = 1
    sdata = sdata.order_by('-timestamp')[:datapts]
    data = [s.as_json() for s in sdata]
    return {'count': len(data), 'data': data}



# url options for GET
# targettime=<datetime: targettime> get data <= <targettime>, default is now
# datapts=<int: datapts> get <datapts> sensor reading back from target time, default is 1
# default is to get latest sensor reading for sensor
def zone_data(request, zone_name):
    # if GET get zone meta data
    try:
        z = Zone.objects.get(pk=zone_name)
    except Zone.DoesNotExist:
        return JsonResponseNotFound(reason="No Zone with the specified id was found.")
    dseries = {}
    for s in z.tempsensor_set.all():
        dseries[s.name] = get_sensor_data(request, s)
    rsensordata = {'count': 1, 'data': dseries}
    return JsonResponse(data=rsensordata)


bool_values = {
    'on': True,
    'true': True,
    '1': True,
    'True': True,
    'off': False,
    'false': False,
    '0': False,
    'False': False
}


# url options for GET
# targettime=<datetime: targettime> get data <= <targettime>, default is now
# datapts=<int: datapts> get <datapts> sensor reading back from target time, default is 1
# default is to get latest sensor reading for sensor
def sensor_data(request, sensor_name):
    if request.method == 'POST':
        # if POST add data for sensor
        try:
            timestamp = request.POST['timestamp']
            timestamp = datetime.fromisoformat(timestamp)
        except KeyError:
            timestamp = datetime.today()
        try:
            value = request.POST['value']
            value = Decimal(value)
        except KeyError:
            return JsonResponseBadRequest(reason="Missing value parameter")
        try:
            s = TempSensor.objects.get(pk=sensor_name)
        except TempSensor.DoesNotExist:
            return JsonResponseNotFound("No Sensor with the specified id was found.")
        s = TempSensorData(sensor=s, timestamp=timestamp, value=value, original_value=value)
        s.save()
        return JsonResponseCreated()
    else:
        # if GET get data for sensor
        try:
            s = TempSensor.objects.get(pk=sensor_name)
        except TempSensor.DoesNotExist:
            return JsonResponseNotFound("No TempSensor with the specified id was found.")
        rsensordata = get_sensor_data(request, s)
        return JsonResponse(data=rsensordata)
