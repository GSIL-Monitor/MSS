# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render

from StreamSystem.FBV.relay_and_publish_func import start_relay_or_publish
from StreamSystem.FBV.streamlink_func import start_streamlink
from StreamSystem.FBV.stop_stream_func import stop_stream_process

from StreamSystem.read_log import read_file
from StreamSystem.models import StreamInfo

import datetime
import json
import logging

# Create your views here.

logger = logging.getLogger(__name__)


class JsonResponseMixin(object):

    @staticmethod
    def json_response(content):
        return HttpResponse(json.dumps(content))


def index(request):
    return render(request, 'index.html')


def page2(request):
    return render(request, 'readlog.html')


def show_stream(request):
    on_stream_list = list(StreamInfo.objects.all().values())
    if len(on_stream_list) > 0:
        time_delta = datetime.timedelta(hours=8)
        for i in range(len(on_stream_list)):
            on_stream_list[i]['create_time'] = \
                (on_stream_list[i]['create_time'] + time_delta).strftime('%Y-%m-%d_%H-%M-%S')
        on_stream_list.insert(0, 'Filled')
    else:
        on_stream_list.insert(0, 'Empty')
    return HttpResponse(json.dumps(on_stream_list))


def add_stream(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        channel_name = received_json_data['channel_name']
        stream_method = received_json_data['stream_method']
        src_path = received_json_data['src_path']
        dst_path = received_json_data['dst_path']

        stream_in_db = StreamInfo.objects.filter(src_path=src_path, dst_path=dst_path, stream_method=stream_method)
        channel_name_in_db = StreamInfo.objects.filter(channel_name=channel_name)
        if len(stream_in_db) > 0:
            return HttpResponse(json.dumps({'error': 'This Stream is existed !'}))
        elif len(channel_name_in_db) > 0:
            return HttpResponse(json.dumps({'error': 'Duplicate channel_name !'}))
        else:
            if stream_method == 'streamlink':
                reply = start_streamlink(src_path, dst_path, channel_name)
            else:
                reply = start_relay_or_publish(src_path, dst_path, stream_method, channel_name)

        if reply == 'success':
            return HttpResponse(json.dumps({'success': 'Create Done!'}))
        else:
            return HttpResponse(json.dumps({'error': 'Create Failed!'}))


def stop_stream(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        channel_name = received_json_data['channel_name']

        reply = stop_stream_process(channel_name)
        return HttpResponse(json.dumps(reply))


def show_log_file(request):
    if request.method == 'GET':
        return HttpResponse('the return string for test 1111 yahaha~\n' * 20)
        # channel_name = request.GET.get('channel_name')
        # if channel_name == '' or channel_name is None:
        #     return HttpResponse('channel_name is null, please check')
        # else:
        #     reply = read_file(channel_name)
        #     return HttpResponse(json.dumps(reply))
