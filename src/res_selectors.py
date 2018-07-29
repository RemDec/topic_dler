#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
        
        self.stick_names = ["ris", "jes", "stick", "larry", "chancla", "issou", "aya", "reup"]
             
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
                elif len(p) == 4 and p[3] == 0:
                    uni_corners += 1
        infos[0] += " ~ " + str(uni_corners) + " corners"
        return uni_corners>1
        
        
class Risitas_selector():
    
    def __init__(self, topic, others_posters = []):
        self.author = topic.op
        self.others = others_posters
        
    def select_post(self, post):
        if post.op in self.others:
            return True
        if post.op == self.author:
            return self.is_chapter(post)
        return False
    
    def is_chapter(self, post):
        for i, test_fun in enumerate([self.chapt_by_stickers,self.chapt_by_title,self.chapt_by_size]):
            if test_fun(post):
                return True
        return False
        
    def chapt_by_title(self, post):
        txt = post.xml_disp(only_content=True).lower()
        found_keyword = (not "blockquote" in txt) and (("chapitre" in txt) or ("partie" in txt))
        enough_lines = self.chapt_by_size(post, max_size=10)
        return found_keyword and enough_lines
        
    def chapt_by_size(self, post, max_size=20):
        nbr_lines = post.content_tree.xpath("count(.//p | .//br)")
        return nbr_lines > max_size
        
    def chapt_by_stickers(self, post, nbr_max=20):
        nbr_stickers = post.content_tree.xpath("count(.//img[@class='img-shack'])")
        return nbr_stickers > nbr_max
    
    
        
        
        
        