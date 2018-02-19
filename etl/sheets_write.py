import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import json
from datetime import datetime
from googleapiclient import discovery
import httplib2

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

scope = ['https://spreadsheets.google.com/feeds']

import os
cpath = os.path.dirname(os.path.abspath(__file__))

credentials = ServiceAccountCredentials.from_json_keyfile_name(cpath + '/nimbus-charts-00bde45ffdb8.json', scope)

gc = gspread.authorize(credentials)


def write_data(data_list, headers, fname):
    new_json = []
    fname_s = fname + str(datetime.now())
    spreadsheet_body = {
        # TODO: Add desired entries to the request body.
    }

    resource = {
      'properties': {
        'title': fname
      },
      'sheets': [
        {
          'properties': {
            'title': 'data'
          }
        }
      ]
    }

    # dservice = discovery.build('drive', 'v3', credentials=credentials)
    http = credentials.authorize(httplib2.Http())
    dservice = discovery.build('drive', 'v3', http=http)

    service = discovery.build('sheets', 'v4', credentials=credentials)

    request = service.spreadsheets().create(body=resource)
    response = request.execute()
    pprint(response['spreadsheetId'])
    file_id = response['spreadsheetId']
    # sht1 = gc.open_by_key(file_id)
    # ws = sht1.get_worksheet(0)
    def callback(request_id, response, exception):
        if exception:
            # Handle error
            print exception
        else:
            print "Permission Id: %s" % response.get('id')

    batch = service.new_batch_http_request(callback=callback)
    user_permission = {
        'type': 'user',
        'role': 'owner',
        'emailAddress': 'kevin.denny@piano.io'
    }

    batch.add(dservice.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
    ))
    domain_permission = {
        'type': 'domain',
        'role': 'writer',
        'domain': 'piano.io'
    }
    batch.add(dservice.permissions().create(
            fileId=file_id,
            body=domain_permission,
            fields='id',
    ))
    batch.execute()

    results = dservice.files().list(
        pageSize=10,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))


    # print(file_id)
    # sh = gc.open_by_key(response['spreadsheetId'])
    # # sh.share('kevin.denny@piano.io', perm_type='user', role='writer')

    # ws = sh.get_worksheet(0)

    # for f, h in enumerate(headers):
    #     ws.update_cell(1, (f+1), h)
    # for i, row in enumerate(data_list):
    #     j = i + 2
    #     for u, h in enumerate(row):
    #         ws.update_cell(j, (u+1), row[h])
    return file_id