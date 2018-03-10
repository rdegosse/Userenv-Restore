import os
import datetime
import re
from API import API
from CeleryPy import log
from CeleryPy import set_user_env
from Botstate import get_bot_state
import json

class MyFarmware():

    def get_input_env(self):
        prefix = self.farmwarename.lower().replace('-','_')
        
        self.input_title = os.environ.get(prefix+"_title", '-')
        self.input_tool = os.environ.get(prefix+"_tool", 'BACKUP_USERENV')
        self.input_debug = int(os.environ.get(prefix+"_debug", 1))

        if self.input_debug >= 1:
            log('title: {}'.format(self.input_title), message_type='debug', title=self.farmwarename)
            log('tool: {}'.format(self.input_tool), message_type='debug', title=self.farmwarename)
            log('debug: {}'.format(self.input_debug), message_type='debug', title=self.farmwarename)
        
    def __init__(self,farmwarename):
        self.farmwarename = farmwarename
        self.get_input_env()
        self.api = API(self)
        self.points = []

    def check_celerypy(self,ret):
        try:
            status_code = ret.status_code
        except:
            status_code = -1
        try:
            text = ret.text[:100]
        except expression as identifier:
            text = ret
        if status_code == -1 or status_code == 200:
            if self.input_debug >= 1: log("{} -> {}".format(status_code,text), message_type='debug', title=self.farmwarename + ' check_celerypy')
        else:
            log("{} -> {}".format(status_code,text), message_type='error', title=self.farmwarename + ' check_celerypy')
            raise

    def get_toolslot(self, points, tools, tool_name='', pointer_type='ToolSlot'):
        for t in tools:
            if t['name'].lower() == tool_name.lower():
                for p in points:
                    if p['pointer_type'].lower() == pointer_type.lower():
                        if p['tool_id'] == t['id']:               
                            return p.copy()
        
        return

    def backup_bot_state(self):
        self.botstate = get_bot_state()
        if self.input_debug >= 1: log('botstate: {}'.format(self.botstate), message_type='debug', title=self.farmwarename)
        self.toolslot = self.get_toolslot(
            points = self.api.api_get('points'),
            tools = self.api.api_get('tools'),
            tool_name = self.input_tool)
        if self.input_debug >= 1: log('toolslot Before: {}'.format(self.toolslot), message_type='debug', title=self.farmwarename)
        self.toolslot['meta'] = self.botstate["user_env"]
        if self.input_debug < 2 :
            endpoint = 'points/{}'.format(self.toolslot['id'])
            self.api.api_put(endpoint=endpoint, data=self.toolslot)
        self.toolslot = self.get_toolslot(
            points = self.api.api_get('points'),
            tools = self.api.api_get('tools'),
            tool_name = self.input_tool)
        if self.input_debug >= 1: log('toolslot After: {}'.format(self.toolslot), message_type='debug', title=self.farmwarename)

    def restore_bot_state(self):
        self.botstate = get_bot_state()
        if self.input_debug >= 1: log('botstate Before: {}'.format(self.botstate), message_type='debug', title=self.farmwarename)
        self.toolslot = self.get_toolslot(
            points = self.api.api_get('points'),
            tools = self.api.api_get('tools'),
            tool_name = self.input_tool)
        if self.input_debug >= 1: log('toolslot: {}'.format(self.toolslot), message_type='debug', title=self.farmwarename)
        for e in self.toolslot['meta']:
            if self.input_debug >= 1: log('set_user_env: {} => {}'.format(e,self.toolslot['meta'][e]), message_type='debug', title=self.farmwarename)
            if self.input_debug < 2 : self.check_celerypy(set_user_env(e, self.toolslot['meta'][e]))

    def run(self):
        if "restore" in self.farmwarename.lower() : self.restore_bot_state()
        if "backup" in self.farmwarename.lower() : self.backup_bot_state()
        
        