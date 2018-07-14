#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topic_dler_main import *
from sortedcontainers import SortedList
from PIL import Image
import io
        
class Page_not_foundError(Exception):
    def __init__(self, url):
        self.url = url
    def __str__(self):
        return "Error 404 - page " + self.url + " not found." 

class Jvc_downloader():
    
    def __init__(self, params, logwidget=None):
        main_page = open_page(params['url'])
        if main_page is None or type(main_page) is tuple:
            raise Page_not_foundError(params['url'])
        self.init_params(params, main_page)
        self.log = logwidget
        
        
    def init_params(self, params, page):
        self.params = params
        self.verb = params['verb']
        self.tree = tree_from_page(page)
        self.dir = self.init_dir(self.tree)
        self.all_topic_pages = sorted([params['url']] + others_pages_jvc(self.tree))
        self.all_dl_resources = SortedList()
        self.num_dl = 0
        self.stick_detect_fct = self.init_detect_fct()
        self.stick_names = self.init_stick_names()
        
        
    def init_dir(self, tree):
        if self.params['path'] != "<current working directory>/nom_topic":
            return self.params['path']
        else:
            topic_title = tree.xpath('//title/text()')[0]
            new_dir = to_folder_name(topic_title)
            os.makedirs(new_dir, exist_ok=True)
            return new_dir
        
    def init_detect_fct(self):
        all_fct = [self.nr_by_weight, self.nr_by_name, self.nr_by_borders]
        to_return = [self.nr_by_size]
        strength = self.params['stick_ctrl']
        if strength > 0.3:
            to_return.append(all_fct[0])
        if strength > 0.4:
            to_return.append(all_fct[1])
        if strength > 0.7:
            to_return.append(all_fct[2])
        return to_return
        
    def init_stick_names(self):
        return ["ris", "jes", "stick", "larry", "chancla", "issou"]
    
    #Boucles sur toutes les pages
    def start_dl(self):
        for num, page_url in enumerate(self.all_topic_pages):
            self.display("<==== Page " + str(num+1) + " ====>")
            try:
                self.fetch_elmts_from_url(page_url)
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
        response = http_request(url)
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
            if url in self.all_dl_resources:
                self.display("       *" + elmt_name + "*")
                return True
            self.display("       " + elmt_name)
            accept = True
            if slct_fct is not None:
                accept = slct_fct(response, content, redirect)
            if accept:
                with open(self.dir + "/" + elmt_name, 'wb+') as elmt_file:
                    elmt_file.write(content)
                    self.all_dl_resources.add(url)
                    self.num_dl += 1
            else:
                self.display("        |_ rejected")
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
        image = Image.open(io.BytesIO(content))
        is_sticker = False
        infos = ["        |"]
        for test_fct in self.stick_detect_fct:
            if redirect and test_fct in [self.nr_by_size]:
                continue
            seems_sticker = test_fct(image, response, infos)
            if seems_sticker:
                is_sticker = True
                break
        
        if self.params['stick'] == 1:
            # no stickers
            relevant = not(is_sticker)
        else:
            relevant = is_sticker
        self.display(infos[0])
        return relevant
        
    def nr_by_size(self, image, response, infos):
        #Les stickers suivent une taille de ratio hauteur = largeur*4/3
        (width, height) = image.size
        is_sticker_size = abs(width - (height*4)/3) <= 1
        infos[0] += str(width) + "x" + str(height)
        return is_sticker_size
        
    def nr_by_weight(self, image, response, infos):
        weight = int(response.headers['content-length'])
        # En dessous de 15 Ko, considere sticker
        infos[0] += " ~ " + str(weight/1000) + " ko"
        return weight < 15000
        
    def nr_by_name(self, image, response, infos):
        name = response.geturl()
        infos[0] += " ~ " + name
        for n in self.stick_names:
            if n in name:
                # nom de l'image contient un nom de stickers
                return True
        return False
        
    def nr_by_borders(self, image, response, infos):
        # Detection des pixels blancs dans les coins
        (width, height) = image.size
        corners = [(0,0), (width-1, 0), (width-1,height-1), (0, height-1)]
        pixels = []
        for coord in corners:
            pixels.append(image.getpixel(coord))
        white_corners = pixels.count((255,255,255,0))
        infos[0] += " ~ " + str(white_corners) + " corners"
        return white_corners>1
        
        
    #Traitement des webm
    def webm_from_site(self, response):
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
            res = self.fetch_elmt_oftype(webm_url_totry, "video", self.webm_from_site)
            if res is not None:
                return webm_url
    
    # Traitement des vocaroos
    def vocaroo_from_site(self, response):
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
        s = "** fin," +str(self.num_dl)+ " fichiers dl dans /" +self.dir+ " **"
        self.display("*"*len(s))
        self.display(s)
        self.display("*"*len(s))
        
    def display(self, str):
        if self.verb:
            if self.log is not None:
                self.log.insert('end', str+"\n")
                self.log.see('end')
            print(str)

            
            
            