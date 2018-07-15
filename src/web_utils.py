#!/usr/bin/env python
# -*- coding: utf-8 -*-


from urllib import request, error, parse
from lxml import etree
from socket import timeout


def http_request(url, u_a = None, keep = False):
    """
    Fait une requete pour l'url donnée et en retourne l'objet obtenu qui est
    la réponse HTTP headers+data
    """
    if u_a is None:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'
    else:
        user_agent = u_a
    my_headers={'User-Agent': user_agent}
    if keep:
        my_headers['Connection'] = "Keep-Alive"
    try:
        req = request.Request(url, data=None, headers=my_headers)
        return request.urlopen(req, timeout=1)
    except error.HTTPError as err:
        print("Error HTTP", err.code)
        return (err.code, err)
    except (error.URLError, ValueError):
        print("URL incorrect")
    except timeout:
        print("Timeout")
        
def open_page(url, sv_html=False, filename='page.html'):
    """
    A partir d'un url fait la requete et retourne les données du champs data
    de la réponse à cette requête, ou None si elle n'a pas abouti
    """
    page = http_request(url)
    if page is None or type(page) is tuple:
        return page
    str_page = page.read().decode('UTF-8')
    if sv_html:
        with open(filename, 'w') as p:
            p.write(str_page)
    return str_page
    
def tree_from_page(str_page):
    """
    Retourne un arbre a partir de la page HTML str_page pour les requetes XPath
    """
    parser = etree.HTMLParser()
    tree = etree.fromstring(str_page, parser)
    return tree
    
def is_url_raw_elmt(response, elmt_type):
    """
    Determine si le champs data d'une response HTTP est bien du type elmt_type
    voulu et retourne un tuple (type_ok, format_données) en respect du header
    Content-Type dans la réponse HTTP
    """
    content_type = response.getheader('Content-Type').split('/')
    if len(content_type) > 1:
        is_right_type = content_type[0] == elmt_type
        return (is_right_type, content_type[1])

def name_from_php(url, varname, extension=""):
    """
    Pour une requete php retourne la valeur de la variable varname déclarée dedans
    postfixée de la string extension, ou l'url si varname n'est pas définie
    """
    try:
        return parse.parse_qs(parse.urlparse(url).query)[varname][0] + extension
    except:
        return url


def find_all_url(url_list):
    return sorted(list(set([url for url in url_list if "http" in url])))

def find_webm_url(url_list):
    return url_list
    
def find_vocaroo_url(url_list):
    return [voca_url for voca_url in url_list if "vocaroo.com" in voca_url]
    

        
        
        
        
