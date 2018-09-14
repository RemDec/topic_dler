# -*- coding: utf-8 -*
from web_utils import *
import sys


def http_request(url, u_a = None, keep = False):
    """
    Fait une requete pour l'url donnée et en retourne l'objet obtenu qui est
    la réponse HTTP headers+data
    """
    if u_a is None:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'
    else:
        user_agent = u_a
    my_headers={'User-Agent': user_agent, 'Referer':'http://www.jeuxvideo.com/'}
    if keep:
        my_headers['Connection'] = "Keep-Alive"
    try:
        req = request.Request(url, data=None, headers=my_headers)
        print(req.header_items())
        return request.urlopen(req, timeout=1)
    except error.HTTPError as err:
        print("Error HTTP", err.code)
        return (err.code, err)
    except (error.URLError, ValueError):
        print("URL incorrect")
        return (0, "URL incorrect")
    except timeout:
        print("Timeout")
        return (0, "Timeout")
    except ssl.SSLWantReadError as e:
        print("Unknown error : " + str(e))
        return (0, "Erreur SSL")
        
def open_page(url, is_local_url=False, sv_html=False, filename='page.html'):
    """
    A partir d'un url (ou chemin local) fait la requete et retourne les données du champs data
    de la réponse à cette requête, ou None si elle n'a pas abouti
    """
    if is_local_url:
        import os
        if os.path.isfile(url):
            page = request.urlopen("file:"+url)
        else:
            return None
    else:
        page = http_request(url)
    if page is None or type(page) is tuple:
        return page
    str_page = page.read().decode('UTF-8')
    if sv_html:
        with open(filename, 'w') as p:
            p.write(str_page)
    return str_page
    
if len(sys.argv) > 1:
    url = sys.argv[1] 
else:
    url = "http://www.jeuxvideo.com"
print(open_page(url, is_local_url=False, sv_html=True, filename='403result.html')[1])