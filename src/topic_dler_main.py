from urllib import request, error, parse
from lxml import etree
from socket import timeout
import sys, os, unidecode, re


global verbose, no_stick, path


#------- Utilitaires -------
def display(s):
    global verbose
    if verbose:
        print(s)
        
def print_risitas():
    print("                               ░░░░░░░░░████░               ")
    print("                   ░░░░ ░░▒      ░░░░░░▒████▒               ")
    print("                  ░▓▓▓▓░▓▓▓▒ ░▓▒ ░░░░░░░█████               ")
    print("                   ▓▒▒▓░▓▓▒░ ▓▓▒ ░░░░░░░██████              ")
    print("                   █▓▓░░▒▓▓░▒▓▓▒░░░░░░░░███████             ")
    print("                  ░▓░▓▒▒▓▒▓░▓▓▓▒░░░░░░░▒███████░            ")
    print("                  ░▒░░░░▒▒░▒▒▒▓░░░░░░░░████████▒            ")
    print("               ░░▓▓▓▓█▓▓▓░░░░░▒░░░░░░░░█████████            ")
    print("              ▓██████████████▒░░░░░░░░▒█████████░           ")
    print("            ░▓██████████████████▒░░░░░▓█████████░           ")
    print("          ░▓██████████████████████▓▒░▒▓█████████░           ")
    print("         ████▓▒▒▒▒▓█████████████████████████████░           ")
    print("      ░██████▓▒▒▒▒▒▒▒▒▓█████████████████████████▓           ")
    print("      █████▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓███████████████████████           ")
    print("      ██▒░   ▒▒▒▒▒▒▒▒▒▒▒▒░▒▓███████████▓▓▓███████           ")
    print("            ░▓▒▒▒░░▒▒▒▒▒░░░░░▒▓█████▓▒▒▓▓▓██████░           ")
    print("            ░▓▓▒▒░░░░▒░░▒▒▒▒▒▒▓▓▓▒▒▒▒▒▒▒▓███████░           ")
    print("            ░████▓▓▒▒░░▒▒▓▓███▓▓▓▒▒▒▒▒▒▒▓▓██████▒           ")
    print("            ▒█▓▓██▓▓▒▒▒░▒▓▓▓▒▒▒▒▒▒▓▓▓▒▒▒▓▓█████▓▒           ")
    print("            ▓▓▒▒▒▒▒▓▓▒░░▒▒▓▒▓▓▓▒▒▒▓▓▓▒▒▒▓▓▓███▓▓▓           ")
    print("            ▓▓██▓▓▓▓▓▒░░▒▒▒▒▓▓██▓▓▓▒▒▒▒▒▒▓▓██▓▓▓▓░          ")
    print("            ▒█▓▓▓▒▒▓▒▒▒░▒▒▒▒▓▓▓▓▓▓▒▒▒▒▒▒▒▓▓██▓▓▓▓▒          ")
    print("      ░▓░   ▒▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▓▓▓▓▓▒▒▒▒▒▒▒▒▓▓██▓▓▓▓▒          ")
    print("   ▓▒▒▒░░▒▓▒▒▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▓▓▒▒▒▒▒▒▒▒▒▒▓████▓▓▒▒          ")
    print("  ░▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒░▒▒▒▒▒░▒▒░░░░▒▒▒▒▒▒▓████▓▓▒           ")
    print("  ▓██▓▓▓▓▒▓▓▓▓▓▒▒▒▒▒▒░░▒▒▒▒▒▒░░░░░░▒▒▒▒▒▓▓███▓▓▒▒           ")
    print(" ▒▓█▓▓▓▒▒▓██████▒▒▒▓▓▒▒▓▓▒▒▒░░░░░▒▒▒▒▒▒▒▓▓███▓▒▒            ")
    print(" ▒▓██▓▓▒▒▓▓▓▓███▒▒▒▓██▓▓▓▓▓▓▒▒▒░▒▒▒▒▒▒▒▒▓▓▓▓█▒▒▒            ")
    print(" ▒██▓█▓▓▓▒▓▓████▒▒▓█████████▓▒▒▒░▒▒▒▒▒▒▓▓▓▓▓▓▒▒             ")
    print(" ▓██▓█▒▒▓█▓▓████▓█████████████▓▒▒▒▒▒▒▒▒▓▓▓▓▓▓▒░             ")
    print(" ▓██▓▓▓░▓████████████▓▒▓▓█▓▓███▓▒▒▒▒▒▒▓▓▓▓▓▓▓               ")
    print("▓▒▒░░░░▓▓█▓▒█████████▓▓▓██▓▓▓███▒▒▒▒▒▒▓▓▓▓▓▓█               ")
    print("▒░▒▓█▓░▓▒▒░████▓██▓██████████▓▓█▓▒▓▓▓▓▓▓▓▓▓▓█▒▒░            ")
    print("▒▓████░  ░▒░▓░▓▓█▓▓▓▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓████▓           ")
    print("▓▓█▓▒░░▓████▓░█▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▓▓▒▓▓▓▓▓▓▓▓▓█████▓▓▒         ")
    print("██▒█▓▓░░█▓▒██▓█▓▓▓▓▒▒▒▓▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓█▓▓▓░█▓▓▒░        ")
    print("█████▓▒▒▓▒█▓███▓▓▓▓▒▓▓▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓█▓▓▒░░       ")
    print("████▓▒▓░▓▓▓████▓▓▓▓▓▓▒▒▒▒▒▓▒▒▓▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓█▓▓▒░▒▒░      ")
    print("████▓░ ░▓▓██████▓▓▓▓▓▓▓▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓█▓▓▓░▒▒░░░░░   ")
    print("█████░▓░▓▓████▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████▓▓▓▓▓▓▓▓▓▒▒▒▒░░░▒░   ")
    print("████▒  ░▓▓█████▓███▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓███▓▓▓▓▓▓▓▓▓▒▒▒▒░░▒▒░░   ")
    print("████▓▓  ▓█████▓█████▓▓██▓▓█▓▓▓▓▓▓▓███▓▓▓▓▓▓▓▓▓▒▒▒▒▒░▒▒▒░░░░ ")
    print("████  ▒█▓▓████▓▓▓███▓▓▓▓▓▓▓▓▓▓▓▓███▓▓▓▓▓▓▓▓▓▓▒▒▓▓▒░▒▒▒░░░░░░")
    print("████    ▓█████▓▓▓▓████▓▓▓▓▓▓▓████▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓▒▒▒▒▓▒░░░░░░")
    print("███░   ░░█████▓▓▓█▓██████▓▓████▓▓▓▓▓▓▓▓▓▓▓▒▒▓▒▒▒▒▒▒▓▒▒░░░░░░")
    print("Script écrit par Kyprinite, en collaboration avec l'élite")
    
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
    all_found = expr.findall(page.decode('utf-8'))
    all_found = set([webm_url[2:] for webm_url in all_found])
    return all_found

def is_img_relevant(response, content, tol = 0):
    #Les stickers suivent une taille de ratio hauteur = largeur*4/3
    from PIL import Image
    import io
    image = Image.open(io.BytesIO(content))
    (width, height) = image.size
    is_sticker_size = abs(width - (height*4)/3) <= 1
    return not(is_sticker_size)


#------- Web --------
def http_request(url):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'
    try:
        req = request.Request(url, data=None, headers={'User-Agent': user_agent})
        return request.urlopen(req, timeout=2)
    except error.HTTPError as err:
        print("Error HTTP", err.code)
        return (err.code, err)
    except (error.URLError, ValueError):
        print("URL incorrect")
    except timeout:
        print("Timeout")
        
def xpath_request(url, req):
    response = http_request(url)
    if response is not None:
        tree = tree_from_page(response.read())
        return tree.xpath(req)
    
def open_page(url, sv_html=False, filename='page.html'):
    page = http_request(url)
    if page is None:
        return None
    str_page = page.read().decode('UTF-8')
    if sv_html:
        with open(filename, 'w') as p:
            p.write(str_page)
    return str_page
    
def save_page(url, filename=None, force_newline=False):
    page = http_request(url)
    str_page = page.read().decode('utf-8')
    if force_newline:
        str_page = str_page.replace('>', '>\n')
    re_to_url_webm(str_page)
    fname = url if filename is None else filename
    with open(fname, 'w') as fp:
        fp.write(str_page)
    return str_page
    
def save_raw_elmt(url, name="file"):
    response = http_request(url)
    if response is not None:
        with open(name, "wb+") as file:
            file.write(response.read())
        
    
def tree_from_page(str_page):
    parser = etree.HTMLParser()
    tree = etree.fromstring(str_page, parser)
    return tree

def fetch_elmt_oftype(url, oftype, alt_fct, dir, slct_fct=None):
    response = http_request(url)
    if response is None:
        return None
    if is_url_raw_elmt(response, oftype)[0]:       
        content = response.read()
        elmt_name = reduce_name(url, ["/", "-"])
        display("       " + elmt_name)
        accept = True
        if slct_fct is not None:
            accept = slct_fct(response, content)
        if accept:
            with open(dir + "/" + elmt_name, 'wb+') as elmt_file:
                elmt_file.write(content)
        else:
            display("        |_ rejected")
        return True
    else:
        alt_fct(response, dir) 

def is_url_raw_elmt(response, elmt_type):
    content_type = response.getheader('Content-Type').split('/')
    if len(content_type) > 1:
        is_right_type = content_type[0] == elmt_type
        return (is_right_type, content_type[1])
        
def name_from_php(url, varname, extension=""):
    try:
        print(parse.parse_qs(parse.urlparse(url).query)[varname])
        return parse.parse_qs(parse.urlparse(url).query)[varname][0] + extension
    except:
        return url

def find_all_url(url_list):
    return sorted(list(set([url for url in url_list if "http" in url])))

def find_webm_url(url_list):
    return url_list
    
def find_vocaroo_url(url_list):
    return [voca_url for voca_url in url_list if "vocaroo.com" in voca_url]
    
    
#-------- jvc --------  
def img_from_noel(response, dir):
    tree = tree_from_page(response.read())
    img_url = tree.xpath('/html/head/meta[@property="og:image"]/@content')[0]
    fetch_elmt_oftype(img_url, "image", img_from_noel, dir)
    
def webm_from_site(response, dir):
    page = response.read()
    webm_url = None
    link_webm = re_to_url_webm(page)
    for webm_url_totry in link_webm:
        page_url_parts = parse.urlparse(response.geturl())
        if webm_url_totry[:2] == "//":
            new_prefix = page_url_parts.scheme + ":"
            webm_url_totry = new_prefix + webm_url_totry
        elif webm_url_totry[0] == '/':
            new_prefix = page_url_parts.scheme + "://" + page_url_parts.netloc
            webm_url_totry = new_prefix + webm_url_totry
        res = fetch_elmt_oftype(webm_url_totry, "video", webm_from_site, dir)
        if res is not None:
            return webm_url

def fetch_elmts_from_url(url, dir=None):
    str_page = open_page(url)
    tree = tree_from_page(str_page)
    # Recherche et dl des images
    display("   <---- Images ---->")
    global no_stick
    slct_img_fct = is_img_relevant if no_stick else None
    for img_url in tree.xpath('//img[@class="img-shack"]/@alt'):
        try:
            fetch_elmt_oftype(img_url, "image", img_from_noel, dir, slct_img_fct)
        except timeout:
            pass
    # Recherche et dl des webm
    display("   <---- Videos ---->")
    all_webm_url = find_all_url(tree.xpath('//div[@class="bloc-contenu"]//span/text()'))
    for webm_url in all_webm_url:
        try:
            fetch_elmt_oftype(webm_url, "video", webm_from_site, dir)
        except timeout:
            pass
        
def others_pages_jvc(curr_page_tree):
    other_p = curr_page_tree.xpath('//div[@class="bloc-liste-num-page"]//@href')
    no_doubles = set(["http://www.jeuxvideo.com"+cut_link for cut_link in other_p])
    return list(no_doubles)
    
def fetch_all_pages(url, dir=None):
    str_page = open_page(url)
    tree = tree_from_page(str_page)
    if dir is None:
        topic_title = tree.xpath('//title/text()')[0]
        dir = to_folder_name(topic_title)
    os.makedirs(dir, exist_ok=True)
    all_pages = sorted([url] + others_pages_jvc(tree))
    for num, page in enumerate(all_pages):
        display("<==== Page " + str(num+1) + " ====>")
        try:
            fetch_elmts_from_url(page, dir=dir)
        except timeout:
            pass
    display("\n*** fin, fichiers dl dans /" + dir + " ***")

        
#------ main ------
if __name__ == "__main__":
    global verbose, no_stick, path
    verbose = False
    no_stick = False
    path = None
    print_risitas()
    while 1:
        try:
            com = input("|>>")
            if com == "v":
                verbose = not(verbose)
            elif com == "s":
                no_stick = not(no_stick)
            elif len(com) > 3 and com[0] == "p" and com[1] == " ":
                p = com[2:]
                if verify_folder_path(p):
                    path = p
                else:
                    print("Le chemin du dossier n'existe pas ou vous n'avez pas les droits")
            elif com == "q":
                exit(0)
            else:
                fetch_all_pages(com, path)
        except Exception as e:
            print(e)
            print("Commande ou URL invalide")
                