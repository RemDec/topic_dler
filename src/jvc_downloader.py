#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import *
from web_utils import *
from sortedcontainers import SortedList
from PIL import Image
from io import BytesIO
        
class Page_not_foundError(Exception):
    def __init__(self, url):
        self.url = url
    def __str__(self):
        return "Error 404 - page " + self.url + " not found." 
        
class Image_selector():
    
    def __init__(self, stickers_control, bareme=[0, 0.3, 0.5, 0.8]):
        all_fct = [self.stick_by_size, self.stick_by_weight,
                    self.stick_by_name, self.stick_by_borders]
        self.used_fct = []
        for i, b_val in enumerate(bareme):
            if i >= len(all_fct) or b_val > stickers_control:
                break
            else:
                self.used_fct.append( (b_val, all_fct[i]) )
        
        self.stick_names = ["ris", "jes", "stick", "larry", "chancla", "issou", "reup"]
             
    def is_sticker(self, image, response, redirect):
        img_infos = ["        |"]
        if redirect:
            f = self.used_fct[1:]
        else:
            f = self.used_fct
        for (_, detect_fct) in f:
            if detect_fct(image, response, img_infos):
                return (True, ('').join(img_infos))
        return (False, ('').join(img_infos))
        
        
    def stick_by_size(self, image, response, infos):
        #Les stickers suivent une taille de ratio hauteur = largeur*4/3
        (width, height) = image.size
        is_sticker_size = abs(width - (height*4)/3) <= 1
        infos[0] += str(width) + "x" + str(height)
        return is_sticker_size
        
    def stick_by_weight(self, image, response, infos):
        weight = int(response.headers['content-length'])
        # En dessous de 15 Ko, considere sticker
        infos[0] += " ~ " + str(weight/1000) + " ko"
        return weight < 15000
        
    def stick_by_name(self, image, response, infos):
        name = response.geturl()
        infos[0] += " ~ " + name
        for n in self.stick_names:
            if n in name:
                # nom de l'image contient un nom de stickers
                return True
        return False
        
    def stick_by_borders(self, image, response, infos):
        # Detection des pixels blancs dans les coins
        (width, height) = image.size
        corners = [(0,0), (width-1, 0), (width-1,height-1), (0, height-1)]
        pixels = []
        for coord in corners:
            pixels.append(image.getpixel(coord))
        uni_corners = 0
        if len(image.getbands()) >= 3:
            for p in pixels:
                if (p[0], p[1], p[2]) == (255, 255, 255):
                    uni_corners += 1
        infos[0] += " ~ " + str(uni_corners) + " corners"
        return uni_corners>1
        

class Post():
    
    def __init__(self, post_tree):
        self.post_tree = post_tree
        self.req = self.init_req()
        self.op = self.xpath_post(self.req['author'])[0]
        self.date = self.xpath_post(self.req['date'])[0]
        self.content_tree = self.xpath_post(self.req['content_tree'])[0]
        self.ext_urls = self.get_ext_urls()
        
    def init_req(self):
        req = {}
        req['author'] = "(.//@alt)[1]"
        req['date'] = ".//div[@class='bloc-date-msg']/span/text()"
        req['content_tree'] = ".//div[@class='bloc-contenu']"
        req['imgs'] = ".//img[@class='img-shack']/@alt"
        req['ext_links'] = ".//span/@title | .//span[not(./img)][not(@title)][@class]/text()"
        return req
        
    def xpath_post(self, req):
        return self.post_tree.xpath(req)
        
    def get_ext_urls(self):
        return self.content_tree.xpath(self.req['ext_links'])
        
    def get_raw_content(self):
        return self.content_tree.xpath(".//p/text()")
        
    def get_images_url(self):
        return self.content_tree.xpath(self.req['imgs'])
        
    def get_webms_url(self):
        # a ameliorer -> lister tous les sites à webm?
        return self.ext_urls
        
    def get_vocas_url(self):
        return [voca_url for voca_url in self.ext_urls if "vocaroo.com" in voca_url]
        
    def __str__(self):
        return self.op + " le " + self.date + ":\n " + str(self.ext_urls)
        
    def xml_disp(self, only_content = True):
        import xml.etree.ElementTree as ET
        if only_content:
            s = ET.tostring(self.content_tree, encoding="utf-8")
        else:
            s = ET.tostring(self.post_tree, encoding="utf-8")
        return s.decode("utf-8").replace('    ', ' ').replace('>', '>\n')
    
    
class Topic():
    
    """elmt topic = //div[@id='forum-main-col'] -> indice 0"""
    """elmt titre = .//span[@id='bloc-title-forum']/text() sur topic -> indice 0"""
    """elmt max_page = .//div[@class='bloc-liste-num-page'])[1]/span[last()-1]/a/text() sur topic -> ind 0"""
    """elmt author = topic.xpath("(.//div[@class='inner-head-content']/div[@class='bloc-header']/span)[1]/text()")
                     faire gaffe a elminier \n et espaces dans réponse"""
                     
    def __init__(self, url):
        self.main_url = url
        main_page = open_page(url)
        if main_page is None or type(main_page) is tuple:
            raise Page_not_foundError(url)
        self.req = self.init_requests()
        self.tree = tree_from_page(main_page)
        self.topic_tree = self.tree.xpath(self.req['topic'])[0]
        self.title = self.xpath_topic(self.req['title'])[0]
        self.op = self.xpath_topic(self.req['op'])[0].strip(' \n')
        self.max_page = self.get_max_page()
        self.curr_page = int(self.xpath_topic(self.req['curr_p'])[0])
        
    def init_requests(self):
        req = {}
        req['topic'] = "//div[@id='forum-main-col']"
        req['title'] = ".//span[@id='bloc-title-forum']/text()"
        req['op'] = "(.//div[@class='inner-head-content']/div[@class='bloc-header']/span)[1]/text()"
        req['max_p'] = "(.//div[@class='bloc-liste-num-page'])[1]/span[position()=last() or position()=last()-1]//text()"
        req['curr_p'] = "(.//div[@class='bloc-liste-num-page'])[1]/span[@class='page-active']//text()"
        req['all_msg'] = ".//div[@class='bloc-message-forum ']"
        return req
        
    def xpath_topic(self, req):
        return self.topic_tree.xpath(req)
        
    def get_max_page(self):
        various_res = self.topic_tree.xpath(self.req['max_p'])
        if len(various_res) == 0:
            return 1
        else:
            try:
                p = int(various_res[1])
                return p
            except (ValueError, IndexError):
                return int(various_res[0]) 
        
    def get_nth_page_url(self, n):
        if n < 1 or n > self.max_page:
            return None
        split_url = self.main_url.split('-')
        split_url[3] = str(n)
        return '-'.join(split_url)
        
    def set_page(self, n):
        url_n = self.get_nth_page_url(n)
        if url_n is None:
            return None
        page_n = open_page(url_n)
        if page_n is None or type(page_n) is tuple:
            raise Page_not_foundError(url)
        self.tree = tree_from_page(page_n)
        self.main_url = url_n
        self.curr_page = n
        self.topic_tree = self.tree.xpath(self.req['topic'])[0]
        return True
        
    def get_all_post(self):
        return [Post(elmt_post) for elmt_post in self.xpath_topic(self.req['all_msg'])]

    def get_nth_post(self, n): 
        res = self.xpath_topic("(.//div[@class='bloc-message-forum '])[" + str(n) + "]")
        if len(res) == 0:
            return None
        return Post(res)
        
    def __str__(self):
        return self.title + "\n de " + self.op + " (" + str(self.curr_page) + " | " + str(self.max_page) + " pages)"
        
        
class Jvc_downloader():
    
    def __init__(self, params, logwidget=None):
        main_page = open_page(params['url'])
        if main_page is None or type(main_page) is tuple:
            raise Page_not_foundError(params['url'])
        self.init_params(params, main_page)
        self.img_sel = Image_selector(params['stick_ctrl'])
        self.log = logwidget
        
        self.topic = Topic(params['url'])
        
    def init_params(self, params, page):
        self.params = params
        self.verb = params['verb']
        self.tree = tree_from_page(page)
        self.dir = self.init_dir(self.tree)
        self.all_topic_pages = sorted([params['url']] + self.others_pages_jvc(self.tree))
        self.all_dl_resources = SortedList()
        self.num_dl = 0
        
        
    def init_dir(self, tree):    
        if self.params['path'] != "<current working directory>":
            base = self.params['path']
        else:
            base = "."
        if self.params['nf']:
            topic_title = tree.xpath('//title/text()')[0]
            new_dir = to_folder_name(topic_title)
        else:
            new_dir = ""
        final = base + "/" + new_dir
        os.makedirs(final, exist_ok=True)
        return final
            
    #Recherche des toutes les pages
    def others_pages_jvc(self, curr_page_tree):
        other_p = curr_page_tree.xpath('//div[@class="bloc-liste-num-page"]//@href')
        no_doubles = set(["http://www.jeuxvideo.com"+cut_link for cut_link in other_p])
        return list(no_doubles)
    
    #Boucles sur toutes les pages
    def start_dl(self):
        self.display(str(self.topic))
        for n_page in range(self.topic.max_page):
            self.display("<==== Page " + str(n_page+1) + " ====>")
            try:
                self.fetch_elmts_from_url(self.topic.get_nth_page_url(n_page+1))
            except timeout:
                pass
        self.display_end()        
        
                
    #Recherche+dl de tous les elmts
    def fetch_elmts_from_url(self, url):
        types_ok = self.params['types_ok']
        str_page = open_page(url)
        tree = tree_from_page(str_page)
        all_url = find_all_url(tree.xpath('//div[@class="bloc-contenu"]//span/text()'))
        
        if types_ok[0]:
            # Recherche et dl des images
            self.fetch_images(tree)
                    
        if types_ok[1]:
            # Recherche et dl des webm
            self.fetch_webms(tree, find_webm_url(all_url))
            
        if types_ok[2]:
            # Recherche et dl des vocaroo
            self.fetch_vocaroos(tree, find_vocaroo_url(all_url))
            
            
    def fetch_images(self, tree):
        self.display("   <---- Images ---->")
        slct_img_fct = self.is_img_relevant if self.params['stick'] in [1, 2] else None
        for img_url in tree.xpath('//img[@class="img-shack"]/@alt'):
            try:
                self.fetch_elmt_oftype(img_url, "image", self.img_from_noel, slct_img_fct)
            except timeout:
                pass
        
    def fetch_webms(self, tree, found_webm_url):
        self.display("   <---- Videos ---->")
        for webm_url in found_webm_url:
            try:
                self.fetch_elmt_oftype(webm_url, "video", self.webm_from_site)
            except timeout:
                pass
                
    def fetch_vocaroos(self, tree, found_voca_url):
        self.display("   <---- Vocaroos ---->")
        for voca_url in found_voca_url:
            try:
                self.fetch_elmt_oftype(voca_url, "audio", self.vocaroo_from_site)
            except timeout:
                pass
    
    
    #DL d'une ressource 
    def fetch_elmt_oftype(self, url, oftype, alt_fct, slct_fct=None, alt_name=None, redirect=False):
        if url in self.all_dl_resources:
            self.display("       *" + reduce_name(url, self.get_name_sep()) + "*")
            return True
        response = http_request(url, keep=False)
        #self.display(str(response.info()))
        if response is None:
            return None
        elif type(response) is tuple:
            self.display("url :" + url)
            self.display("error code :"+ str(response[0]))
            self.display("error content :"+ str(response[1]))
            return None
        (res_type_ok, res_format) = is_url_raw_elmt(response, oftype)
        if res_type_ok:
            # On a la ressource telle quelle
            content = response.read()
            to_reduce = alt_name if alt_name is not None else url
            elmt_name = reduce_name(to_reduce, self.get_name_sep(), res_format)
            self.display("       " + elmt_name)
            accept = True
            if slct_fct is not None:
                accept = slct_fct(response, content, redirect)
            if accept:
                with open(self.dir + "/" + elmt_name, 'wb+') as elmt_file:
                    elmt_file.write(content)
                    self.num_dl += 1
            else:
                self.display("        |_ rejected")
            self.all_dl_resources.add(url)
            return True
        else:
            # On doit la chercher sur la page recue
            alt_fct(response, slct_fct, alt_name)
                
    #Traitement image
    def img_from_noel(self, response, slct_fct=None, alt_name=None):
        tree = tree_from_page(response.read())
        img_url = tree.xpath('/html/head/meta[@property="og:image"]/@content')[0]
        self.fetch_elmt_oftype(img_url, "image", self.img_from_noel, slct_fct, alt_name, redirect=True) 

    def is_img_relevant(self, response, content, redirect=False):
        image = Image.open(BytesIO(content))
        (is_sticker, img_infos) = self.img_sel.is_sticker(image, response, redirect)

        if self.params['stick'] == 1:
            # no stickers
            relevant = not(is_sticker)
        else:
            relevant = is_sticker
        self.display(img_infos)
        return relevant      
        
    #Traitement des webm
    def webm_from_site(self, response, slct_fct, alt_name):
        page = response.read()
        webm_url = None
        link_webm = re_to_url_webm(page)
        if link_webm is None:
            self.display("/!\ Erreur de decodage de la page, section suivante")
            return None
        for webm_url_totry in link_webm:
            page_url_parts = parse.urlparse(response.geturl())
            if webm_url_totry[:2] == "//":
                new_prefix = page_url_parts.scheme + ":"
                webm_url_totry = new_prefix + webm_url_totry
            elif webm_url_totry[0] == '/':
                new_prefix = page_url_parts.scheme + "://" + page_url_parts.netloc
                webm_url_totry = new_prefix + webm_url_totry
            res = self.fetch_elmt_oftype(webm_url_totry, "video", self.webm_from_site)
            if res is not None:
                return webm_url
    
    # Traitement des vocaroos
    def vocaroo_from_site(self, response, slct_fct, alt_name):
        page_tree = tree_from_page(response.read())
        audio_php = page_tree.xpath('//p/a[@download]/@href')
        res = None
        i = 0
        formats = [".mp3", ".ogg", ".flac", ".wav"]
        while not res and i<len(audio_php):
            url_t = "https://vocaroo.com" + audio_php[i]
            res = self.fetch_elmt_oftype(url_t, "audio", self.vocaroo_from_site, alt_name=name_from_php(url_t, "media")+formats[i])
            i += 1
        if res is not None:
            return url_t
        
    
    #Divers    
    def get_name_sep(self):
        minimum = ['/', '?', '&']
        if self.params['short']:
            return minimum + ['-']
        else:
            return minimum
            
    def display_end(self):
        s = "**" + str(self.num_dl)+ " fichiers dl dans " +self.dir+ " **"
        self.display("*"*len(s))
        self.display(s)
        self.display("*"*len(s))
        
    def display(self, str):
        if self.verb:
            if self.log is not None:
                self.log.insert('end', str+"\n")
                self.log.see('end')
            print(str)

            
            
            
            