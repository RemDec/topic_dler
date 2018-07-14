#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, unidecode


def reduce_name(url, sep_list=['/', '-'], ext=None):
    max_ind = -1
    for sep in sep_list:
        max_ind = max(url.rfind(sep), max_ind)
    name = url[max_ind+1:]
    if ext is not None and not '.' in name:
        if ',' in ext:
            ext = ext[:ext.index(',')]
        if not(name.endswith('.'+ext)):
            name += '.'+ext
    return name
    
    
def to_folder_name(title):
    ind_cut = title.rfind("sur le forum")
    if ind_cut > 1:
        cut_title = title[:ind_cut-1]
    else:
        cut_title = title
    clean = ""
    for letter in cut_title:
        letter = unidecode.unidecode(letter)
        if letter == " ":
            letter = "_"
        elif letter == "/":
            letter = "%"
        elif not letter.isalnum():
            letter = ""
        clean += letter 
    return clean
    
def verify_folder_path(path):
    return os.path.isdir(path) and os.access(path, os.W_OK)
    

def re_to_url_webm(page):
    expr = re.compile('=[^\s]+\.webm')
    try:
        all_found = expr.findall(page.decode('utf-8'))
    except UnicodeDecodeError:
        return None
    all_found = set([webm_url[2:] for webm_url in all_found])
    return all_found
    
    
