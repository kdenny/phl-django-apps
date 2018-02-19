from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from pprint import pprint
import csv

import os
cpath = os.path.dirname(os.path.abspath(__file__))
key_file = cpath + '/bigquery-a8788a27e0d6.json'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=key_file
client = language.LanguageServiceClient()

# credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file, scope)

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=key_file
# client = language.LanguageServiceClient()

token_sources = []
with open("/Users/kevindenny/Documents/django_nimbus/nimbus/piano_components/nlp_keys.csv", "rb") as sourcing:
    source_reader = csv.reader(sourcing)
    for sr in source_reader:
        token_sources.append(sr[0])

all_token_types = ['entity_1','entity_2','entity_3']

aggregation_list = []
with open("/Users/kevindenny/Documents/django_nimbus/nimbus/piano_components/Aggs.csv", 'rb') as afile:
    preader = csv.DictReader(afile)
    for prow in preader:
        aggregation_list.append(prow)

subject_list = []
with open("/Users/kevindenny/Documents/django_nimbus/nimbus/piano_components/Subjects.csv", 'rb') as pfile:
    preader = csv.DictReader(pfile)
    for prow in preader:
        subject_list.append(prow)

buzzwords = []
with open("/Users/kevindenny/Documents/django_nimbus/nimbus/piano_components/buzzwords.csv", 'rb') as afile:
    preader = csv.reader(afile)
    for prow in preader:
        buzzwords.append(prow[0])


def process_sentence(sentence, row):

    text = sentence
    
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    entities = client.analyze_entities(document=document, encoding_type='UTF32').entities

    # # pprint(entities)

    # for i, entity in enumerate(entities):
    #     item = 'entity_' + str(i+1)
    #     row[item] = entity.name

    syntax_obj = client.analyze_syntax(document=document, encoding_type='UTF32')
    
    for token in syntax_obj.tokens:
        # pprint(token)
        dep_type = token_sources[token.dependency_edge.label]
        if dep_type not in all_token_types:
            all_token_types.append(dep_type)
        # else:
        #     print(token.lemma)
        if dep_type not in row:
            row[dep_type] = token.lemma
        else:
            if type(row[dep_type]) is list:
                tlist = row[dep_type]
            else:
                tlist = [row[dep_type]]
                tlist.append(token.lemma)
                row[dep_type] = tlist
                print("Duplicate for type " + dep_type)
    # pprint(row)

    return row


def get_buzzwords(et):

    dumb_words = ['list', 'site', 'best', 'user', 'audience', 'users', 'number', 'fraction', 'subscriber', 'subscribers']

    buzz = []
    for e in et:
        if e['name'] in buzzwords:
            buzz.append(e['name'])
        elif e['type'] == 'LOCATION' or e['type'] == 'OTHER' or e['type'] == 'ORGANIZATION' or e['type'] == 'PERSON' or e['type'] == 'CONSUMER_GOOD' or e['type'] == 'EVENT':
            if e['name'] not in dumb_words:
                buzz.append(e['name'])
        else:
            print(e['name'] + " of type " + e['type'] + " not included.")

    pprint(buzz)
    return buzz


def get_entities(sentence):
    text = sentence
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    entities = client.analyze_entities(document=document, encoding_type='UTF32').entities
        
    
    et = []
    for entity in entities:
        ef = {
            'type': entity_type[entity.type],
            'name': entity.name
        }
        et.append(ef)

    return et 

def check_row(query_content, subject_row):
    subj = None
    subj_loc = subject_row['Column']
    if subj_loc in query_content:
        stype = []
        if type(query_content[subj_loc]) is list:
            for lt in query_content[subj_loc]:
                stype.append(lt)
        else:
            stype.append(query_content[subj_loc])
        for query_item in stype:
            if query_item == subject_row['Subject']:
                subj_loc2 = subject_row['Column 2']
                if subj_loc2 == '': 
                    subj = subject_row['Subject']

                if subj_loc2 in query_content:
                    stype2 = []
                    if type(query_content[subj_loc2]) is list:
                        for lt2 in query_content[subj_loc2]:
                            stype2.append(lt2)
                    else:
                        stype2.append(query_content[subj_loc2])
                    for query_item2 in stype2:
                        if query_item2 == subject_row['Sub-Subject']:
                            subj = subject_row['Subject'] + '-' + subject_row['Sub-Subject']
                if subj_loc2 != '' and subj_loc2 not in query_content:
                    subj = None
    return subj

def get_query_aggregator(query_content):
    this_agg = None
    for item in query_content:
        stype = []
        if type(query_content[item]) is list:
            for lt in query_content[item]:
                stype.append(lt)
        else:
            stype.append(query_content[item])
        for agg in aggregation_list:
            for st in stype:
                if st == str(agg['Word']).lower():
                    this_agg = agg['Type']

    return this_agg


def get_query_subjects(query):
    possible_subjects = []
    max_length = 1
    for subj in subject_list:
        c_subj = check_row(query, subj)
        # pprint(c_subj)
        if c_subj:
            possible_subjects.append(c_subj)
            comb_subj = c_subj.split("-")
            if len(comb_subj) > 1:
                max_length = len(comb_subj)
    # pprint(possible_subjects)
    if len(possible_subjects) == 0:
        pprint(query)
        print("Whats up with "+ query['Sentence'] + "?")
        possible_subjects = None
    subjects = []
    if max_length > 1:
        for po2 in possible_subjects:
            cs = po2.split("-")
            if len(cs) >= max_length:
                subjects.append(po2)
    else:
        subjects = possible_subjects
    return subjects


def get_numeric_buzzwords(query_row, buzzwords):
    numeric_fields = ['age', 'hour', 'hours', 'day', 'days', 'month', 'months', 'week', 'weeks']
    number_words = ['twice', 'last']
    
    nf = ''
    numb = False
    for it in query_row:
        if type(query_row[it]) is list:
            for f in query_row[it]:
                if f in numeric_fields:
                    numb = True
                    nf = f
        else:
            if query_row[it] in numeric_fields:
                numb = True
                nf = query_row[it]
    if numb:
        if 'NUM' in query_row:
            if type(query_row['NUM']) is list:
                nb = query_row['NUM'][0]
            else:
                nb = query_row['NUM']
        
            new_buzz = "{0}-{1}".format(nf,nb)
            buzzwords.append(new_buzz)
        else:
            nw = None
            for of in query_row:
                if type(query_row[of]) is list:
                    for ff in query_row[of]:
                        if ff in number_words:
                            nw = ff
                else:
                    ff = query_row[of]
                    if ff in number_words:
                        nw = ff
            if nw:
                new_buzz = "{0}-{1}".format(nw,nf)
                buzzwords.append(new_buzz)
            
            

            


    return buzzwords