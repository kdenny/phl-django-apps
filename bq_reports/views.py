# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView

# from gspread_query import get_json_array, get_first_sheet_as_json_array

import os
from pprint import pprint
import json
import csv
from datetime import datetime, timedelta
from google.cloud import bigquery
from pprint import pprint
import os
import uuid

# from bigquery import get_client
# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/kevindenny/Documents/automated-reports/nimbus-charts-782fdc5a724d.json"



client = bigquery.Client(project='piano-production')
# tables = list(dataset.list_tables())
# pprint(tables)
job_config = bigquery.QueryJobConfig()

# Set use_legacy_sql to False to use standard SQL syntax.
# Note that queries are treated as standard SQL by default.
job_config.use_legacy_sql = True



class AdblockRevenue(APIView):

    def post(self, request):
        start_date = datetime.strptime(str(request.data['startDate']), '%Y-%m-%d')
        end_date_delta = datetime.strptime(str(request.data['endDate']), '%Y-%m-%d') - timedelta(days=183)
        aid = str(request.data['aid'])
        vpp = str(request.data['vpp'])
        cpm = str(request.data['cpm'])
        if start_date > end_date_delta:
            max_date = start_date
        else:
            max_date = end_date_delta

        start_date = str(request.data['startDate'])
        end_date = str(request.data['endDate'])

        max_date = max_date.strftime('%Y-%m-%d')

        print(max_date)

        with open("/Users/kevindenny/Documents/automated-reports/dj_app/bq_api/query.txt","rb") as f:
            query = f.read()
            qtext = query.replace("{0}",aid).replace("{1}",cpm).replace("{2}",vpp).replace("{3}",start_date).replace("{4}",end_date)
            print(qtext)

            with open("query.sql",'wb') as ofile:
                ofile.write(qtext)

        query_job = client.query(qtext, job_config=job_config)  # API request
        # job = client.run_async_query('fullname-age-query-job', query)
        rows = query_job.result()  # Waits for query to finish
        sc = query_job
        rd = []
        keys = ['Month', '#_of_Converters', '#_of_Pageviews', '#_of_Ad_Impressions', 'Revenue based on CPM', 'Revenue based on PVs']
        for row in rows:
            print(row)
            l = {}
            i = 0
            for g in row:
                print(g)
                l[keys[i]] = g
                i += 1
            rd.append(l)


        body = {'data': rd, 'headers': keys}

        return Response(json.dumps(body))


class TrafficBreakdown(APIView):

    def post(self, request):
        start_date = str(request.data['startDate'])
        end_date = str(request.data['endDate'])
        aid = str(request.data['aid'])
        aggregator = str(request.data['agg'])

        print(aid)
        with open("/Users/kevindenny/Documents/automated-reports/dj_app/bq_api/traffic_breakdown_query.txt","rb") as f:
            query = f.read()
            qtext = query.replace("{0}",aid).replace("{1}",aggregator).replace("{2}",start_date).replace("{3}",end_date)
            print(qtext)

        if aggregator in ['city, region, country', 'url']:
            qtext += ' ORDER BY NbrPageviews Desc LIMIT 100'

        query_job = client.query(qtext, job_config=job_config)  # API request
        # job = client.run_async_query('fullname-age-query-job', query)
        rows = query_job.result()  # Waits for query to finish
        sc = query_job
        rd = []

        kkeys = ['# of Pageviews', 'Unique Browsers', 'Unique Sessions']
        keys = []
        for u in kkeys:
            keys.append(u)
        if "," not in aggregator:
            keys.append(aggregator)
        else:
            for j in aggregator.split(", "):
                keys.append(j)
        for row in rows:
            l = {}
            i = 0
            for g in row:
                l[keys[i]] = g
                if keys[i] in kkeys:
                    l[keys[i]] = int(g)
                i += 1
            l['AvgPageviews'] = float(l['# of Pageviews']) / float(l['Unique Browsers'])
            l['AvgSessions'] = float(l['Unique Sessions']) / float(l['Unique Browsers'])
            rd.append(l)
        lkeys = []
        if "," not in aggregator:
            lkeys.append(aggregator)
        else:
            for j in aggregator.split(", "):
                lkeys.append(j)
        ekeys = ['Unique Browsers', '# of Pageviews', 'AvgPageviews', 'Unique Sessions', 'AvgSessions']
        for e in ekeys:
            lkeys.append(e)

        ko = {}

        body = {'data': rd, 'headers': lkeys, 'agg': aggregator}

        return Response(json.dumps(body))

class ContentAnalytics(APIView):

    def post(self, request):
        start_date = str(request.data['startDate'])
        end_date = str(request.data['endDate'])
        aid = str(request.data['aid'])

        print(aid)
        with open("/Users/kevindenny/Documents/automated-reports/dj_app/bq_api/content_query.txt","rb") as f:
            query = f.read()
            qtext = query.replace("{0}",aid).replace("{2}",start_date).replace("{3}",end_date)
            print(qtext)

        # if aggregator in ['city, region, country', 'url']:
        #     qtext += ' ORDER BY NbrPageviews Desc LIMIT 100'

        query_job = client.query(qtext, job_config=job_config)  # API request
        # job = client.run_async_query('fullname-age-query-job', query)
        rows = query_job.result()  # Waits for query to finish
        sc = query_job
        rd = []

        numeric_keys = ['# of Pageviews', 'Unique Browsers', 'Unique Sessions']
        text_keys = ['url', 'contentSection', 'contentAuthor']
        date_keys = ['contentCreated']
        all_keys = []
        for u in numeric_keys:
            all_keys.append(u)
        for t in text_keys:
            all_keys.append(t)
        for d in date_keys:
            all_keys.append(d)
        for row in rows:
            real = True
            l = {}
            i = 0
            for g in row:
                this_key = all_keys[i]
                l[this_key] = g
                if this_key in numeric_keys:
                    l[this_key] = int(g)
                if this_key in date_keys:
                    if g:
                        l[this_key] = g.strftime('%Y-%m-%d')
                    else:
                        real = False
                i += 1
            if real:
                l['AvgPageviews'] = float(l['# of Pageviews']) / float(l['Unique Browsers'])
                l['AvgSessions'] = float(l['Unique Sessions']) / float(l['Unique Browsers'])
                rd.append(l)
        all_keys.append('AvgPageviews')
        all_keys.append('AvgSessions')

        ko = {}
        print(len(rd))

        body = {'data': rd, 'headers': all_keys}

        return Response(json.dumps(body))

