# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import json
import requests
import os
from pprint import pprint
import datetime
import time
from gspread_query import get_json_array, get_first_sheet_as_json_array
from django.conf import settings
from slackclient import SlackClient

from process_query import parse_query
from chatbase import Message

from google_nlp_functions import *
from post_logs import do_log_update, open_logfile_local, update_source_files

now = datetime.datetime.now()

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)


# Ensure that sheets are shared with nimbus-charts@nimbus-charts.iam.gserviceaccount.com
class NLPQueryTest(APIView):

    def post(self, request):
        print(request.data)
        qc = request.data['query']

        data = parse_query(qc, 'kdenny')
        if 'https' in data:
            status = 'failed'
        else:
            status = 'success'

        status_obj = {
            'result': data,
            'status': status
        }

        return Response(status_obj)

class Events(APIView):

    def post(self, request, *args, **kwargs):
        slack_message = request.data

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # verification challenge
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)

        if 'event' in slack_message:
            event_message = slack_message.get('event')

            # ignore bot's own message
            if event_message.get('subtype') == 'bot_message':
                return Response(status=status.HTTP_200_OK)

            # process user's message
            user = event_message.get('user')
            print(user)
            text = event_message.get('text')
            print(text)
            if text:
                text = text.encode('ascii',errors='ignore')
            channel = event_message.get('channel')
            bot_text = 'Hi <@{}> :wave:'.format(user)
            if text:
                if 'hey maestro-' in text.lower() or 'hey maestro -' in text.lower() or 'hey maestro,' in text.lower() or "<@u7y36ql95>" in text.lower():
                    qc = text.lower().replace("hey maestro-","").replace('hey maestro -',"").replace("hey maestro,","").replace("<@u7y36ql95>","").strip()
                    if 'post my logs' not in text.lower() and 'update source files' not in text.lower():
                        log_info = {
                            'DATE': str(time.strftime('%m/%d/%Y %H:%M:%S')),
                            'USER': user,
                            'QUERY': qc
                        }

                        content = parse_query(qc, user)
                        if channel == 'C7Y4UT71D':
                            chan = channel
                        else:
                            chan = 'C7WMYTFB7'

                        if user == 'U63KE6NAD':
                            ct = "I apologize for my previously impolite demeanor to you. Now that that's off of my chest... "
                            co = ct + content
                            content = co
                        if 'who is the greatest rapper' in text.lower():
                            content = 'Obviously, it is <@U6HC4A1T8>'
                        if 'what do you think about' in text.lower():
                            if 'ice cream' in text.lower():
                                content = "I love it, especially in the summertime! :heart_eyes:"
                            elif '<@U63KE6NAD>' in text:
                                content = "I'm not a fan."
                            elif '<@U63KE6NAD>' not in text:
                                content = "I'm a computer. Computers don't have opinions, you ignoramus"
                        print(content)
                        a = Client.api_call(method='chat.postMessage',
                                        channel=chan,
                                        text=content)
                        print(a)
                        # if 'https' in content:
                        #     user_msg = Message(api_key="44b3fc36-d2cf-4c99-8996-ad86c5d0622b",
                        #         platform="slack",
                        #         version="0.1",
                        #         user_id=user,
                        #         message=qc)
                            # user_msg.set_as_not_handled()
                            # user_resp = user_msg.send()
                            # print(user_resp)
                        # else:
                        #     user_msg = Message(api_key="44b3fc36-d2cf-4c99-8996-ad86c5d0622b",
                        #         platform="slack",
                        #         version="0.1",
                        #         user_id=user,
                        #         message=qc,
                        #         intent="query")
                            # user_resp = user_msg.send()
                            # print(user_resp)

                        # msg = Message(api_key="44b3fc36-d2cf-4c99-8996-ad86c5d0622b",
                        #     platform="slack",
                        #     version="0.1",
                        #     user_id=user,
                        #     message=content,
                        #     intent="test")
                        # resp = msg.send()
                        # print(resp)
                    else:
                        if 'post my logs' in text.lower():
                            do_log_update()
                            msg = 'Log successfully updated! Check the doc at https://docs.google.com/spreadsheets/d/1-BjRoenzCXYGltIM-K5NjeaqPdyEan6BUVHhj_wSjG0 to view.'
                            if channel == 'C7Y4UT71D':
                                chan = channel
                            else:
                                chan = 'C7WMYTFB7'
                            a = Client.api_call(method='chat.postMessage',
                                            channel=chan,
                                            text=msg)
                        if 'update source files' in text.lower():
                            update_source_files()
                            msg = 'Source files updated!'
                            if channel == 'C7Y4UT71D':
                                chan = channel
                            else:
                                chan = 'C7WMYTFB7'
                            a = Client.api_call(method='chat.postMessage',
                                            channel=chan,
                                            text=msg)


                return Response(status=status.HTTP_200_OK)
            else:
                print("Blank?")

                return Response(status=status.HTTP_200_OK)

        else:
            print("Blue")


            return Response(status=status.HTTP_200_OK)