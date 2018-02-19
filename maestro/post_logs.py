import csv


import requests
import json
from pprint import pprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os

now = datetime.datetime.now()
scope = ['https://spreadsheets.google.com/feeds']

cpath = os.path.dirname(os.path.abspath(__file__))
key_file = cpath + '/nimbus-charts-00bde45ffdb8.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file, scope)

gc = gspread.authorize(credentials)

url = 'https://docs.google.com/spreadsheets/d/1-BjRoenzCXYGltIM-K5NjeaqPdyEan6BUVHhj_wSjG0/'


def open_logfile_local(log_data):
    new_rows_list = []
    fname = '/Users/kevindenny/Documents/data-lab-prototypes/logs/query_log.csv'
    with open(fname, 'rb') as file1:
        reader = csv.DictReader(file1)
        for row in reader:
            new_rows_list.append(row)

    headers = ['ID', 'DATE', 'USER', 'QUERY', 'SUBJECT', 'AGGS', 'TAGS']
    
    log_data['ID'] = len(new_rows_list) + 2
    for h in headers:
        if h not in log_data:
            log_data[h] = ''
    new_rows_list.append(log_data)
    # # Do the writing
    with open(fname, 'wb') as file2:
        writer = csv.DictWriter(file2, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows_list)

    return len(new_rows_list)


def open_logfile2(log_data):
    if credentials.access_token_expired:
        gc.login()
    sheet_file = gc.open_by_url(url)
    sheet = sheet_file.get_worksheet(0)
    new_json = []
    list_of_lists = sheet.get_all_values()
    all_queries = []
    query_versions = {}
    for rd in list_of_lists:
        if rd[3] != 'QUERY':
            if rd[3] not in all_queries:
                all_queries.append(rd[3])
                query_versions[rd[3]] = 1
            else:
                query_versions[rd[3]] += 1
            
    headers = ['ID', 'DATE', 'USER', 'QUERY', 'VERSION', 'SUBJECT', 'AGGS', 'TAGS']

    start_row = len(list_of_lists) + 1
    log_data['ID'] = start_row
    if log_data['QUERY'] in query_versions:
        print("Found")
        log_data['VERSION'] = query_versions[log_data['QUERY']] + 1
    else:
        log_data['VERSION'] = 1
    for i, header in enumerate(headers):
        if header in log_data:
            sheet.update_cell(start_row, (i+1), log_data[header])
        else:
            sheet.update_cell(start_row, (i+1), "")

    return new_json


def do_log_update():

    llist = []
    with open('/Users/kevindenny/Documents/data-lab-prototypes/logs/query_log.csv', 'rb') as fn2:
        rea = csv.DictReader(fn2)

        for re in rea:
            llist.append(re)

    with open('/Users/kevindenny/Documents/data-lab-prototypes/logs/query_log.csv', 'wb') as fn3:
        rea = csv.writer(fn3)

        rea.writerow(['ID','DATE','USER','QUERY','SUBJECT','AGGS','TAGS'])

    for ll in llist:

        users = {
            'U6HC4A1T8': 'Kevin',
            'U6GFBQRS6': 'Alex'
        }
        if ll['USER'] in users:
            ll['USER'] = users[ll['USER']]

        data = open_logfile2(ll)

def update_source_files():

    sheet_map = [
        'Question_Types',
        'Subject_List',
        'Filters'
    ]

    sh = gc.open('Query Library')
    for sheet_name in sheet_map:
        sheet = sh.worksheet(sheet_name)
        list_of_lists = sheet.get_all_values()
        cfile = '/Users/kevindenny/Documents/data-lab-prototypes/dj-app/report_query/piano_components/' + sheet_name + '.csv'
        with open(cfile, 'wb') as outputr:
            owrite = csv.writer(outputr)
            for row in list_of_lists:
                owrite.writerow(row)
        print("Updated " + sheet_name)
