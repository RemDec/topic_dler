#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jvc_downloader import *
import sys

if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = "http://www.jeuxvideo.com/forums/42-51-56950742-1-0-1-0-mbappe-cette-video.htm"
if len(sys.argv) == 3:
    n_page = int(sys.argv[2])
else:
    n_page = 1
    
topic = Topic(url)
topic.set_page(n_page)
page = topic.get_all_post()
for msg in page:
    print("\n--------------------------------------")
    print(msg)
    print(msg.xml_disp(only_content=False))

