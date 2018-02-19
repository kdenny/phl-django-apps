import requests
import json
from pprint import pprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from google_nlp_functions import *
from read_files import read_question_types, read_filter_types, read_subject_types

now = datetime.datetime.now()
scope = ['https://spreadsheets.google.com/feeds']

import os
cpath = os.path.dirname(os.path.abspath(__file__))

credentials = ServiceAccountCredentials.from_json_keyfile_name(cpath + '/nimbus-charts-00bde45ffdb8.json', scope)

gc = gspread.authorize(credentials)

url = 'https://docs.google.com/spreadsheets/d/1-BjRoenzCXYGltIM-K5NjeaqPdyEan6BUVHhj_wSjG0/'




def parse_query(query, user):
    new_reply = ''

    query_row = {'Sentence': query}
    query_row = process_sentence(query.lower(), query_row)
    pprint(query_row)
    question_structures = read_question_types()
    qf = get_question_format(query_row, question_structures)
    pprint(qf)
    filter_list = read_filter_types()
    q_split = query.replace("?","").replace(".","").replace(",","").split()
    buzz = get_entities(query)
    buzz = get_numeric_buzzwords(query_row, buzz)
    fil = get_filters(q_split, filter_list, buzz)
    all_subjs = read_subject_types()
    subjs = get_subject_words(q_split, all_subjs)
    if subjs:
        subjs = subjs.split(",")
    else:
        subjs = []
    ### If question format identified
    if qf:
        response = generate_response(query_row, qf, fil, subjs)
    else:
        response = 'https://i.pinimg.com/originals/88/a4/03/88a403d3407ae9fc9354cd9d318ff731.jpg'


    return response

def unnest_and_check(nested, check_str):
    is_same = False
    if type(nested) is list:
        for r in nested:
            if r == check_str:
                is_same = True
    else:
        if nested == check_str:
            is_same = True

    return is_same

def get_question_format(query, qtypes):
    q_type = None
    for q in qtypes:
        is_q = False
        w1_loc = q['Word_1_Obj']
        w1 = q['Word_1']
        w2_loc = q['Word_2_Obj']
        w2 = q['Word_2']
        w3_loc = q['Word_3_Obj']
        w3 = q['Word_3']
        if w1_loc in query:

            if unnest_and_check(query[w1_loc], w1):
                if w2_loc in query:
                    if unnest_and_check(query[w2_loc], w2):
                        if w3_loc in query:
                            if unnest_and_check(query[w3_loc], w3):
                                is_q = True

                        else:
                            if w3_loc.strip() == '':
                                is_q = True

                else:
                    if w2_loc.strip() == '':
                        is_q = True


        if is_q:
            q_type = q

    return q_type

def get_filters(query, filters, buzz):
    sel_filter = None
    possible_filters = []
    this_filter = None
    for ph in filters:
        if ph['Options'].strip() == '-':
            if ph['Word_1'] in query:
                if ph['Word_2'] == '-':
                    sel_filter = ph['Type']
                else:
                    if ph['Word_2'] in query:
                        if ph['Word_3'] == '-':
                            sel_filter = ph['Type']
                        else:
                            if ph['Word_3'] in query:
                                sel_filter = ph['Type']

        elif '{' in ph['Options']:
            if '{' not in ph['Word_1']:
                if (ph['Word_1'] in query):
                    if '{' not in ph['Word_2']:
                        if (ph['Word_2'] in query):
                            if ph['Word_2'].strip() == '-' or '{' in ph['Word_3']:
                                possible_filters.append(ph['Type'])
                    elif '{' in ph['Word_2']:
                        possible_filters.append(ph['Type'])

            elif '{' in ph['Word_1']:
                if (ph['Word_2'] in query):
                    possible_filters.append(ph['Type'])

        else:
            opts = ph['Options'].split(",")
            for o in opts:
                if (ph['Word_1'] in query) and (o in query):
                    sel_filter = ph['Word_1'] + ' ' + o

    if sel_filter:
        if sel_filter == 'Time':
            for bz3 in buzz:
                if 'type' in bz3:
                    if bz3['type'] == 'Number':
                        sel_filter = bz3['name']
                else:
                    print(bz3)
        return sel_filter
    else:
        filtz = []
        for pf in possible_filters:
            if pf == 'Geography':
                for bz in buzz:
                    if 'type' in bz:
                        if bz['type'] == 'LOCATION':
                            filtz.append(pf)
            if pf == 'Segment':
                for bz2 in buzz:
                    if 'type' in bz2:
                        if bz2['type'] == 'Segment':
                            filtz.append(pf)
            if pf == 'Time':
                for bz3 in buzz:
                    if 'type' in bz3:
                        if bz3['type'] == 'Number':
                            filtz.append(bz3['name'])
            if pf not in ['Geography', 'Segment', 'Time']:
                filtz.append(pf)
        for bu in buzz:
            if 'type' in bu:
                if bu['type'] == 'Number':
                    filtz.append(bu['name'])

        return (", ").join(filtz)

def get_subject_words(query, subjects):
    sel_subject = None
    old_subject = None
    possible_subjects = []
    for ph in subjects:
        if ph['Word_1'] in query:
            pprint(ph)
            if ph['Word_2'] == '-':
                sel_subject = ph['Subject']

            else:
                if ph['Word_2'] in query:
                    if ph['Word_3'] == '-':
                        sel_subject = ph['Subject']
                    else:
                        if ph['Word_3'] in query:
                            sel_subject = ph['Subject']

        if sel_subject:
            old_subject = sel_subject
            sel_subject = None
            possible_subjects.append(old_subject)
    pprint(possible_subjects)
    if len(possible_subjects) > 1:
        max_length = 1
        cc = []
        final = []
        for fs in possible_subjects:
            f = fs.split()
            if len(f) > max_length:
                max_length = len(f)
            else:
                cc.append(fs)
        for fs2 in possible_subjects:
            f2 = fs2.split()
            keep = False
            for w in f2:
                if w in cc and len(f2) > 1:
                    print(w)
                    keep = True
                else:
                    if len(f2) == 1 and w not in cc:
                        keep = True
            if keep:
                final.append(fs2)

        return (",").join(final)
    else:
        if old_subject:
            sel_subject = old_subject
        return sel_subject

# def check_tags(query):


def get_qf_agg_response(qf, query_row):
    filstring = None
    if qf['Aggs'].strip() != '':
        filstring = ", aggregated by: `{0}`. ".format(qf['Aggs'])
    elif qf['Agg_Obj'].strip() != '':
        a_obj = qf['Agg_Obj']
        if a_obj in query_row:
            ag = query_row[a_obj]
            if isinstance(ag,basestring):
                filstring = ", aggregated by: `{0}`. ".format(ag)
            elif type(ag) is list:
                f2 = []
                for gg in ag:
                    filt = "`{0}`".format(gg)
                    f2.append(filt)
                filts = ", ".join(f2)

                filstring = ", aggregated by: {0}. ".format(filts)
    return filstring

def get_fil_response(fil):
    filstring = None
    if isinstance(fil,basestring):
        filstring = ", filtered by: `{0}`. ".format(fil)
    else:
        filstring = ", filtered by: "
        for f in fil:
            filstring += "`{0}`,".format(f)
        filstring = filstring[:-1]
        filstring += ". "
    return filstring

def get_res_types_response(qf):
    rtypes = []
    rtr = None
    if qf['Response_Type_1']:
        rtypes.append(qf['Response_Type_1'])
        if qf['Response_Type_2']:
            rtypes.append(qf['Response_Type_2'])
            if qf['Response_3']:
                rtypes.append(qf['Response_3'])
    if len(rtypes) > 0:
        rtr = "This question will produce the following result types: "
        for rt in rtypes:
            rtr += '`{0}`, '.format(rt)
        rtr = rtr[:-2]
    return rtr

def get_subject_response(subjects, qf_response, fil_response, agg_response, res_type_response):
    # pprint(subjects)
    filstring = None
    if isinstance(subjects,basestring):
        filstring = "You're asking about *{0}* as a subject".format(subjects)
    else:
        if len(subjects) == 2:
            filstring = "You're asking about *{0}* and *{1}* as subjects".format(subjects[0], subjects[1])
        elif len(subjects) == 1:
            filstring = "You're asking about *{0}* as a subject".format(subjects[0])
    if filstring == None:
        filstring = "I'm unable to parse subject from your query"
        if agg_response:
            filstring += ", but I can tell that you want your data " + agg_response[2:]
        if fil_response:
            filstring += ", but I can tell that you want your data " + fil_response[2:]
    else:
        if agg_response and fil_response:
            filstring += agg_response[:-2] + " and" + fil_response
        else:
            if fil_response:
                filstring += fil_response
            if agg_response:
                filstring += agg_response
            if not fil_response and not agg_response:
                filstring += '. '
    if qf_response:
        filstring += qf_response
    else:
        filstring += "I was unable to fit your question to a standard question format. I will yell at <@U6HC4A1T8> and make sure that doesn't happen again!"

    if res_type_response:
        filstring += res_type_response

    return filstring

def generate_response(query_row, qf, fil, subjects):
    qf_response = "Your question fits the format of *{0}*. ".format(qf['Name'])
    agg_response = None
    fil_response = None

    if qf['Aggs'].strip() != '' or qf['Agg_Obj'].strip() != '':
        agg_response = get_qf_agg_response(qf, query_row)
    if fil:
        fil_response = get_fil_response(fil)

    res_types_response = get_res_types_response(qf)

    response = get_subject_response(subjects, qf_response, fil_response, agg_response, res_types_response)



    return response