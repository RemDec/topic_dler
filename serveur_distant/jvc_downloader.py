#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import *
from web_utils import *
from res_selectors import *
from jvc_elements import *
from sortedcontainers import SortedList
from PIL import Image
from io import BytesIO
import threading
        
class Jvc_downloader():
    
    def __init__(self, params, logwidget=None):
        self.topic = Topic(params['url'])

        self.sel_posters = SortedList()
        self.all_dl_resources = SortedList()
        self.all_used_name = SortedList()
        self.denied_req = []
        self.num_dl = 0
        self.ua_list = get_n_useragents(6)
        self.ind_ua = 0
        self.stop_dl = False
        self.target_folder = "."
        
        self.init_params(params)

        self.log = logwidget
        
        
    def init_params(self, params):
        self.params = params
        self.verb = params['verb']
        self.dir = self.init_dir(self.topic.tree)
        (self.img_ok, self.webm_ok, self.voca_ok, self.post_ok, self.risi_ok) = params['types_ok']
        
        if self.img_ok:
            self.img_sel = Image_selector(params['stick_ctrl'])
        
        if params['only_op']:
            self.sel_posters.add(self.topic.op)
        self.sel_posters.update(params['sel_pseudos'])
        
        if self.risi_ok:
            self.post_ok = True
            self.risi_selector = Risitas_selector(self.topic, params['sel_pseudos'])

        if self.post_ok:
            self.html = Post_HTML_writer(self.topic)
        
    def init_dir(self, tree):    
        if self.params['path'] != "<current working directory>":
            base = self.params['path']
        else:
            base = "."
        if self.params['nf']:
            topic_title = self.topic.title
            new_dir = to_folder_name(topic_title)
            self.target_folder = new_dir
        else:
            new_dir = ""
        final = base + "/" + new_dir
        os.makedirs(final, exist_ok=True)
        return final
            
    
    #Boucles sur toutes les pages
    def start_dl(self):
        self.display(str(self.topic))
        if len(self.sel_posters) > 0:
            self.display("Recherche pour les pseudos suivants :\n"+str_sorted_list(self.sel_posters))
        for n_page in range(self.topic.max_page):
            if self.stop_dl:
                break
            self.display("<==== Page " + str(n_page+1) + "|" + str(self.topic.max_page) + " ====>")
            nbr_try = 0
            while nbr_try < 3:
                try:
                    get_ok = self.topic.set_page(n_page+1)
                    if get_ok:
                        self.fetch_elmts_from_url(self.topic.topic_tree)
                        break
                    nbr_try += 1
                except (timeout, Page_not_foundError) as e:
                    self.display("Page " + str(n_page+1) + " non trouvée :" + str(e))
            self.retry_connection()
        self.retry_connection()
        self.write_HTML_page()
        self.display_end()
        self.stop_dl = True
        
    def retry_connection(self):
        if not self.denied_req:
            return None
        img_urls = [u for u in self.denied_req if "noel" in u]
        self.display("\nTentatives de reconnexion (" + str(len(img_urls)) + ") :\n" + str(img_urls))
        postpose = self.params['power'] > 0.8
        postposed = set()
        
        nbr_try = int(int(self.params['power']*10)/2)
        for i in range(nbr_try):
            if not self.denied_req:
                return None
            self.display("  Tentative " + str(i+1))
            self.ind_ua = (self.ind_ua + 1) % len(self.ua_list)
            self.denied_req = []
            self.fetch_images(img_urls)
            if postpose:
                postposed.update(self.denied_req)
        self.denied_req = list(postposed) if postposed else []
    
    #Recherche+dl de tous les elmts
    def fetch_elmts_from_url(self, page_tree):
        all_urls = ([], [], [])
        (all_img_urls, all_webm_urls, all_voca_urls) = all_urls
        for post in self.topic.get_all_post(self.sel_posters):
            if self.stop_dl:
                return 0
            all_img_urls.extend(post.get_images_url())
            all_webm_urls.extend(post.get_webms_url())
            all_voca_urls.extend(post.get_vocas_url())           
            if self.post_ok:
                if self.risi_ok:
                    if self.risi_selector.select_post(post):
                        self.html.add_post(post)
                else:
                    self.html.add_post(post)
        if self.img_ok:
            # Recherche et dl des images
            self.fetch_images(list(dict.fromkeys(all_img_urls)))
                    
        if self.webm_ok:
            # Recherche et dl des webm
            self.fetch_webms(list(dict.fromkeys(all_webm_urls)))
            
        if self.voca_ok:
            # Recherche et dl des vocaroo
            self.fetch_vocaroos(list(dict.fromkeys(all_voca_urls)))
        
            
    def fetch_images(self, urls):
        self.display("   <---- Images ---->")
        slct_img_fct = self.is_img_relevant if self.params['stick'] in [1, 2] else None
        for img_url in urls:
            if self.stop_dl:
                return 0            
            try:
                self.fetch_elmt_oftype(img_url, "image", self.img_from_noel, slct_img_fct)
            except timeout:
                pass
        
    def fetch_webms(self, urls):
        self.display("   <---- Videos ---->")
        for webm_url in urls:
            if self.stop_dl:
                return 0
            try:
                self.fetch_elmt_oftype(webm_url, "video", self.webm_from_site)
            except timeout:
                pass
                
    def fetch_vocaroos(self, urls):
        self.display("   <---- Vocaroos ---->")
        for voca_url in urls:
            if self.stop_dl:
                return 0
            try:
                self.fetch_elmt_oftype(voca_url, "audio", self.vocaroo_from_site)
            except timeout:
                pass
    
    def write_HTML_page(self):
        if self.post_ok:
            self.display("   <---- Page HTML du topic ---->")
            page_name = to_folder_name(self.topic.title) + ".html"
            self.html.write_html(self.dir + "/" + page_name)
            self.num_dl += 1
            self.display("       " + page_name)
            
    #DL d'une ressource 
    def fetch_elmt_oftype(self, url, oftype, alt_fct, slct_fct=None, alt_name=None, redirect=False):
        if url in self.all_dl_resources:
            self.display("       *" + reduce_name(url, self.get_name_sep()) + "*")
            return True
        response = http_request(url, u_a=self.ua_list[self.ind_ua], keep=False)
        if response is None:
            return None
        elif type(response) is tuple:
            self.report_http_error(url, response)
            return None
        (res_type_ok, res_format) = is_url_raw_elmt(response, oftype)
        if res_type_ok:
            # On a la ressource telle quelle
            content = response.read()
            elmt_name = self.formate_name(url, res_format, alt_name)
            self.display("       " + elmt_name)
            accept = True
            if slct_fct is not None:
                accept = slct_fct(response, content, redirect)
            if accept:
                with open(self.dir + "/" + elmt_name, 'wb+') as elmt_file:
                    elmt_file.write(content)
                    self.all_used_name.add(elmt_name)
                    self.num_dl += 1
            else:
                self.display("        |_ rejected")
            self.all_dl_resources.add(url)
            return True
        else:
            # On doit la chercher sur la page recue
            alt_fct(response, slct_fct, alt_name)
            
    def formate_name(self, base_url, extension, alt_name):
        to_reduce = alt_name if alt_name is not None else base_url
        elmt_name = reduce_name(to_reduce, self.get_name_sep(), extension)
        if self.params['auto_names']:
            if "." in elmt_name:
                elmt_name = str(self.num_dl) + elmt_name[(elmt_name.rfind(".")):]
            else:
                elmt_name = str(self.num_dl)
        if not(elmt_name in self.all_used_name):
            return elmt_name
        ind = 1
        while "("+str(ind)+")"+elmt_name in self.all_used_name:
            ind += 1
        return "("+str(ind)+")"+elmt_name

                
    #Traitement image
    def img_from_noel(self, response, slct_fct=None, alt_name=None):
        tree = tree_from_page(response.read())
        #img_url = tree.xpath('/html/head/meta[@property="og:image"]/@content')[0]
        img_url = tree.xpath('//a[@id="img_actu"]/@href')[0]        
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
        try:
            page = response.read().decode('utf-8')
        except UnicodeDecodeError as e:
            self.display("Page illisible, erreur d'encodage :" + response.geturl())
            return None
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
            
    def report_http_error(self, url, response):
        try:
            if int(response[0]) == 503:
                self.denied_req.append(url)
            else:
                self.display("----------------------------------------------")
                self.display("url :" + url)
                self.display("error :"+ str(response[1]))
                self.display("----------------------------------------------")
        except ValueError:
            pass

            
    def display_end(self):
        s = "**" + str(self.num_dl)+ " fichiers dl dans " +self.dir+ " **"
        self.display("*"*len(s))
        self.display(s)
        self.display("*"*len(s))
        
    def display(self, str):
        if self.verb:
            try:
                if self.log is not None:
                    self.log.insert('end', str+"\n")
                    self.log.see('end')
            except:
                print("Erreur ecriture log de :")
            print(str)
            
    def __str__(self):
        return self.topic.__str__()
        
    def to_json(self):
        title = self.topic.title.replace('"', '\'')
        topic = self.topic
        return ('"jvc_dler":{"title":"'+title+'", "topic_url":"'+topic.main_url+
                '","author":"'+topic.op+'", "nbr_dl":'+ str(self.num_dl)+
                ',"curr_page":'+str(topic.curr_page)+',"max_page":'+str(topic.max_page)+ 
                '}')

    def stop(self):
        self.display("Exécution avortée !!!")
        self.stop_dl = True;

    def get_topic_info(self):
        return {"title":self.topic.title, "url":self.topic.main_url, "author":self.topic.op}



#Thread associe a l'objet
         
class DLing_thread(threading.Thread):

    def __init__(self, params):
        threading.Thread.__init__(self)
        self.jvc_dler = Jvc_downloader(params)
        
    def run(self):
        self.jvc_dler.start_dl()
        
    def stop(self):
        self.jvc_dler.stop()
        
        
    
        
        
            
