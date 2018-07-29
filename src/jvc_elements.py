#!/usr/bin/env python
# -*- coding: utf-8 -*-

from web_utils import *

class Post():
    
    def __init__(self, post_tree):
        try:
            self.post_tree = post_tree
            self.req = self.init_req()
            self.op = self.format_op_name()
            self.date = self.format_date()
            self.content_tree = self.xpath_post(self.req['content_tree'])[0]
            self.ext_urls = self.get_ext_urls()
        except IndexError as e:
            print(e)
            print(self.xml_disp(only_content=False))
        
    def init_req(self):
        req = {}
        req['author'] = "(.//@alt)[1]"
        req['date'] = ".//div[@class='bloc-date-msg']//text()"
        req['content_tree'] = ".//div[@class='bloc-contenu']"
        req['imgs'] = ".//img[@class='img-shack']/@alt"
        req['ext_links'] = ".//span/@title | .//span[not(./img)][not(@title)][@class]/text()"
        return req
        
    def xpath_post(self, req):
        return self.post_tree.xpath(req)
        
    def format_date(self):
        res = self.xpath_post(self.req['date'])
        if not res:
            return "unknown date"
        date = "".join(res)
        date = date.lstrip('\n ').rstrip('\n ')
        return date
        
    def format_op_name(self):
        res = self.xpath_post(self.req['author'])
        if not res:
            return "Pseudo supprimé"
        else:
            return res[0]
    
    def get_ext_urls(self):
        return list(dict.fromkeys(self.content_tree.xpath(self.req['ext_links'])))
        
    def get_raw_content(self):
        return self.content_tree.xpath(".//p//text()")
        
    def get_images_url(self):
        return list(dict.fromkeys(self.content_tree.xpath(self.req['imgs'])))
        
    def get_webms_url(self):
        # a ameliorer -> lister tous les sites à webm?
        return [webm_url for webm_url in self.ext_urls if "http" in webm_url]
        
    def get_vocas_url(self):
        return [voca_url for voca_url in self.ext_urls if "vocaroo.com" in voca_url]
        
    def __str__(self):
        return self.op + " le " + self.date + ":\n URLS " + str(self.ext_urls)
        
    def xml_disp(self, only_content = True):
        import xml.etree.ElementTree as ET
        if only_content:
            s = ET.tostring(self.content_tree, encoding="utf-8")
        else:
            s = ET.tostring(self.post_tree, encoding="utf-8")
        return s.decode("utf-8").replace('    ', ' ').replace('>', '>\n')
    
    
class Topic():
                     
    def __init__(self, url):
        self.main_url = url
        main_page = open_page(url)
        if main_page is None or type(main_page) is tuple:
            raise Page_not_foundError(url)
        self.req = self.init_requests()
        self.tree = tree_from_page(main_page)
        self.topic_tree = self.tree.xpath(self.req['topic'])[0]
        self.title = self.xpath_topic(self.req['title'])[0]
        self.main_page = int(self.xpath_topic(self.req['curr_p'])[0])
        self.max_page = self.get_max_page()
        
        # Retour a la page 1 pour trouver l'auteur
        self.set_page(1)
        self.op = self.xpath_topic(self.req['op'])[0].strip(' \n')

        
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
            raise Page_not_foundError(url_n)
        self.tree = tree_from_page(page_n)
        self.topic_tree = self.tree.xpath(self.req['topic'])[0]
        self.curr_page = n
        self.curr_url = url_n
        return True
        
    def get_all_post(self, sel_posters=[]):
        posts = []
        for elmt_post in self.xpath_topic(self.req['all_msg']):
            p = Post(elmt_post)
            if len(sel_posters) > 0:
                if p.op in sel_posters:
                    posts.append(p)
            else:
                posts.append(p)     
        return posts

    def get_nth_post(self, n): 
        res = self.xpath_topic("(.//div[@class='bloc-message-forum '])[" + str(n) + "]")
        if len(res) == 0:
            return None
        return Post(res)
        
    def __str__(self):
        return self.title + "\n de " + self.op + " (" + str(self.main_page) + " | " + str(self.max_page) + " pages)"
        
        
        
        
            
class Post_HTML_writer():
    
    def __init__(self, topic):
        self.filename = "topic.html"
        self.html_posts = ""
        self.topic = topic
        self.js = self.init_js()
        self.css = self.init_css()
        
    def add_post(self, post):
        self.html_posts += post.xml_disp(only_content=False)
        
    def write_html(self, title=None):
        title = title if title is not None else self.filename
        with open(title, 'w+', encoding="utf-8-sig") as fp:
            script = self.js + "\n" + self.css
            fp.write(self.html_posts + script)
        
    def init_css(self):
        return """<style>
                .bloc-message-forum {
                    font-family:"robotoboldcondensed",Arial,Helvetica,sans-serif;
                }
                .conteneur-message {
                    background-color : #c5dfff;
                    border : solid #bcd2e9;
                }
                .bloc-header {
                    background-color : #939da8;
                }
                .bloc-contenu {
                    background-color : #939fff;
                    padding : 0.1px 5px 0px 10px;
                }
                .bloc-pseudo-msg {
                    background-color : #c5dfff;
                }
                .blockquote-jv {
                font-style : italic;
                color : #4d4d4d;
                }
                </style>"""
        
        
    def init_js(self):
        main_title = self.topic.title.replace("'", "\\'")
        main_url = self.topic.main_url
        return """<script>
                var title = document.createElement('h2');
                title.textContent = '""" + main_title + """';
                var main = document.querySelector('.bloc-message-forum');
                var jvc_link = document.createElement('p');
                jvc_link.innerHTML = 'JVC topic'.link('""" + main_url + """');
                main.insertBefore(jvc_link, main.firstChild);
                main.insertBefore(title, main.firstChild);
                var bloc_headers = document.querySelectorAll('.bloc-header');
                for(var i=0, l=bloc_headers.length; i < l; i++){
                    bloc_headers[i].removeChild(bloc_headers[i].querySelector('.bloc-mp-pseudo'));
                }
                var img_elmts = document.querySelectorAll('.img-shack');
                for(var i=0, l=img_elmts.length; i < l; i++){
                    img_elmts[i].setAttribute("onclick", "window.open('" + img_elmts[i].alt + "', '_blank')");
                }
                
                var spoils = document.querySelectorAll('.bloc-spoil-jv');
                var new_content, to_remove;
                for(var i=0, l=spoils.length; i<l; i++){
                    new_content = spoils[i].querySelector('.contenu-spoil');
                    spoils[i].parentNode.replaceChild(new_content, spoils[i]);
                }
                </script>"""
        
        
        
        