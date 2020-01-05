from django.http import HttpResponse
from django.shortcuts import render
import requests
from decimal import *
from datetime import datetime

from django.conf import settings


def str_to_datetime(ans):
    if ans:
        d = datetime.strptime(ans, "%Y-%m-%d-%H-%M-%S")
        return d
    return None


def datetime_to_str(ans):
    if ans:
        d = ans.strftime("%Y-%m-%d-%H-%M-%S")
        return d
    return None


def dashboard(request):
    # get samples from data server
    r = requests.get(f'{settings.DATASERVER_HOST}/zones')
    if requests.codes.ok != r.status_code:
        # error
        return HttpResponse(status=r.status_code)
    data = r.json()
    zones = data['data']
    zones.sort(key=lambda x: x['id'])

    return render(request, 'heating/heating-dashboard.html', {'host': settings.DATASERVER_HOST, 'zones': zones})


def zone(request, zone_name):
    r = requests.get(f'{settings.DATASERVER_HOST}/zones')
    if requests.codes.ok != r.status_code:
        # error
        return HttpResponse(status=r.status_code)
    data = r.json()
    zones = data['data']
    zones.sort(key=lambda x: x['id'])
    return render(request, 'heating/heating-zone.html', {'host': settings.DATASERVER_HOST, 'zone': zone_name, 'zones': zones})


def all(request):
    # get data for all zones
    datapts = request.GET.get('datapts', '100')
    # look for zone names
    r = requests.get(f'{settings.DATASERVER_HOST}/zones')
    if requests.codes.ok != r.status_code:
        # error
        return HttpResponse(status=r.status_code)
    data = r.json()
    zones = data['data']
    zones.sort(key=lambda x: x['id'])
    dzones = []
    if 'ALL' in request.GET:
        dzones = zones
    else:
        for zone in zones:
            if zone['id'] in request.GET:
                dzones.append(zone)

    return render(request, 'heating/heating-all.html', {'host': settings.DATASERVER_HOST,
                                                        'datapts': datapts,
                                                        'allzones': zones,
                                                        'zones': dzones})


def overlay(request):
    # get data for all zones
    datapts = request.GET.get('datapts', '100')
    # look for zone names
    r = requests.get(f'{settings.DATASERVER_HOST}/zones')
    if requests.codes.ok != r.status_code:
        # error
        return HttpResponse(status=r.status_code)
    data = r.json()
    zones = data['data']
    zones.sort(key=lambda x: x['id'])
    dzones = []
    if 'ALL' in request.GET:
        dzones = zones
    else:
        for zone in zones:
            if zone['id'] in request.GET:
                dzones.append(zone)
    osensors = []
    for zone in dzones:
        r = requests.get(f"{settings.DATASERVER_HOST}/sensors/zone/{zone['id']}")
        data = r.json()
        sensors = data['data']
        for sensor in sensors:
            osensors.append(sensor)
    return render(request, 'heating/heating-overlay.html', {'host': settings.DATASERVER_HOST,
                                                            'datapts': datapts,
                                                            'allzones': zones,
                                                            'zones': dzones,
                                                            'sensors': osensors})


def test(request):
    return render(request, 'heating/heating-test.html', {'host': settings.DATASERVER_HOST}

