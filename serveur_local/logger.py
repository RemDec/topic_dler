#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Logger():

    def __init__(self, f_name="logs.txt"):
        self.f_name = name
        with open(f_name, 'w+') as newlog:
            newlog.write("----"+self.currdate(cut=False)+"----\n")
        
    def log(self, loginfo, stdout=True):
        loginfo = self.currdate() + " :" + loginfo
        if stdout:
            print("#log ", loginfo)
        with open(self.f_name, 'a') as logger:
            logger.write(loginfo+'\n')
            
    def currdate(self, cut=True):
        now = datetime.datetime.now()
        if cut:
            return str(now)[11:19]
        return str(now)
            
    def clean(self):
        with open(self.path, 'w'):
            pass
