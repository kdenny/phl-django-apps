# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView

import os
from pprint import pprint
import json
import csv
from pprint import pprint
import os
import uuid
import geocode as gcd
from sheets_write import write_data

# Create your views here.

class MappingByCity(APIView):

    def post(self, request):
        datum = request.data['results']
        outp = []
        for row in datum:
            loc = gcd.geocode(row)
            if loc:
                no = {'lat': loc['lat'], 'lng': loc['lng']}
                for fn in row:
                    no[fn] = row[fn]
                outp.append(no)

        body = {'geoData': outp}

        return Response(json.dumps(body))


class GoogleSheetsExport(APIView):

    def post(self, request):
        datum = request.data['results']
        headers = request.data['headers']
        fname = 'random_export'
        g = [write_data(datum, headers, fname)]
        print(g)

        # for row in datum:
        #     loc = gcd.geocode(row)
        #     if loc:
        #         no = {'lat': loc['lat'], 'lng': loc['lng']}
        #         for fn in row:
        #             no[fn] = row[fn]
        #         outp.append(no)

        # body = {'geoData': outp}

        return Response(json.dumps(g))