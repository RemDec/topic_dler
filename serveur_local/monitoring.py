#!/usr/bin/env python
# -*- coding: utf-8 -*-


from utils import to_folder_name
from shutil import copy
import xml.etree.ElementTree as ET
import os

class Monitor():

    TOP_PATH = "./top"
    ZIP_PATH = "./zips"
    LOGS_PATH = "./logs"
    
    def __init__(self, delay=10, xml_req="topics_req_logs.xml"):
        self.delay = delay
        self.xml_path = os.path.join(self.LOGS_PATH, xml_req)
        
    def init_dir(self):
        os.makedirs(self.TOP_PATH, exist_ok=True)
        
        
    def set_target_xml(self, xml_path):
        if os.is_file(xml_path, follow_symlinks=False):
            self.last_tree = ET.parse(xml_path)
            return True
        return False
        
    def start_monitoring():
        self.last_tree = self.set_target_xml(self.xml_path)
        self.init_dir()
        
        self.browse_topics()
        
    
    def get_topics_infos(self, info_attr=["topic_name", "topic_url", "nbr_req"]):
        if self.last_tree:
            topics = self.last_tree.findall(".//topic")
            infos_list = []
            for topic in topics:
                infos_list.append([topic.get(attr_val) for attr_val in info_attr])
            return infos_list
        return False
    
    def browse_topics(self):
        topics = self.get_topics_infos()
        with os.scandir(self.ZIP_PATH) as zips:
            for topic in topics:
                #
                # A faire : check dans la DB si deja reference
                #
                name = to_folder_name(topic[0])
                found_zip = []
                for zip_entry in zips:
                    if name in zip_entry.name:
                        found_zip.append(zip_entry)
                path_top = self.place_on_top(found_zip)
                new_top_entry_DB(topic + [path_top])
            
    def place_on_top(zip_entries):
        if not zip_entries:
            return "no_zip"
        best_zip = (-1, None)
        to_remove = []
        for entry in zip_entries:
            s = entry.stat(follow_symlinks=False)
            size = s.st_rsize
            if best_zip[1] is None or size > best_zip[0]:
                best_zip = (size, entry)
            if zip_too_old(s.st_birthtime):
                to_remove.append(entry.path)
        if best_zip[1] is not None:
            copy(best_zip[1].path, self.TOP_PATH)
        for too_old in to_remove:
            os.remove(too_old)
        return os.path.join(self.TOP_PATH, best_zip[1].name)
        
                
            
if __name__ == "__main__":
    monitor = Monitor()
    
    

