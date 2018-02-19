import csv
import pprint

import os
cpath = os.path.dirname(os.path.abspath(__file__))

def read_question_types():
    floc = cpath + '/piano_components/Question_Types.csv'
    question_types = []
    with open(floc,'r') as ft:
        rd = csv.DictReader(ft)
        for row in rd:
            question_types.append(row)

    return question_types

def read_filter_types():
    floc = cpath + '/piano_components/Filters.csv'
    filters = []
    with open(floc,'r') as ft:
        rd = csv.DictReader(ft)
        for row in rd:
            filters.append(row)

    return filters

def read_subject_types():
    floc = cpath + '/piano_components/Subject_List.csv'
    subs = []
    with open(floc,'r') as ft:
        rd = csv.DictReader(ft)
        for row in rd:
            subs.append(row)

    return subs