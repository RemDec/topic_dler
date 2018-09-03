#!/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from io import BytesIO
from jvc_downloader import *
from urllib.parse import parse_qs
import re, os, datetime, threading, time, shutil


class Logger():

    def __init__(self, path="logs.txt"):
        self.path = path
        with open(path, 'w+') as newlog:
            newlog.write("----"+self.currdate(cut=False)+"----\n")
        
    def log(self, loginfo, stdout=True):
        loginfo = self.currdate() + " :" + loginfo
        if stdout:
            print("#log ", loginfo)
        with open(self.path, 'a') as logger:
            logger.write(loginfo+'\n')
            
    def currdate(self, cut=True):
        now = datetime.datetime.now()
        if cut:
            return str(now)[11:19]
        return str(now)
            
    def clean(self):
        with open(self.path, 'w'):
            pass

class Param_controller():
    def __init__(self):
        self.defaults = {"img_ok":0, "webm_ok":0, "voca_ok":0, "post_ok":0, "risi_ok":0, "url":"no_url",
                         "stick":0, "stick_ctrl":1, "only_op":0, "sel_pseudos":[], "auto_names":0, "short":1,
                         "verb":1, "power":1, "nf":1, "path":"."}
        
    def regularize_param(self, prop_form):
        pre_param = self.form_to_params(prop_form)
        return self.set_def_onabsent(pre_param)
    
    def form_to_params(self, form):
        params = {}
        for param, value in form:
            if value == 'on':
                value = True
            else:
                try:
                    value = int(value)
                except ValueError:
                    pass
            params[param] = value
        return params
        
    def set_def_onabsent(self, pre_param):
        for k, default_val in self.defaults.items():
            if pre_param.get(k) is None:
                pre_param[k] = default_val
        pre_param["types_ok"] = (pre_param["img_ok"], pre_param["webm_ok"], pre_param["voca_ok"], pre_param["post_ok"], pre_param["risi_ok"])
        return pre_param
        
class JSONer():

    def __init__(self):
        pass
        
    def get_head(self, status):
        return ('{\n    "status":"'+status+'",\n', '\n}')
        
    def zipping(self, client):
        # client = jvc_dler dont le dl est fini
        h = self.get_head('zipping')
        return h[0] + client.to_json() + h[1]
        
    def processing(self, client):
        # client = jvc_dler en cours de dl des ressources
        h = self.get_head('processing')
        return h[0] + client.to_json() + h[1]
        
    def dl_done(self, client):
        # client = [#perdiodes attendues, lien dl archive]
        h = self.get_head('done')
        zip = ('"archive":{"url":"'+DOMAIN+client[1][1:] + '", "wait":'+str(client[0])+'},'+
               client[2]) 
        return h[0] + zip + h[1]
        
    def cancelled(self, client_id):
        h = self.get_head('cancelled')
        c = '"address":"'+client_id + '"'
        return h[0] + c + h[1]

    def error(self, err_str):
        h = self.get_head('error')
        i = err_str.find('-')
        code = err_str[:i]
        if i < 0:
            code = "000" 
        e = '"error":{"code":"'+code+'", "reason":"'+err_str[i+1:]+'"}'
        return h[0] + e + h[1]
        
class Zipper_thread(threading.Thread):
    
    def __init__(self, dler):
        threading.Thread.__init__(self)
        os.makedirs(ZIP_DIR_PATH, exist_ok=True)
        self.dler = dler
        self.cont = True
        
    def run(self):
        self.find_dl_over()
        
    def stop(self):
        self.cont = False
        
    def delete_client_res(self, client_id):
        del self.dler.curr_clients[client_id]
        logger.log("client supprimé :" + client_id)
    
    def find_dl_over(self):
        while self.cont:
            # print("Iteration clients pour zipper")
            dl_finished = []
            overtimed = []
            for client_id, jvc_dler in self.dler.curr_clients.items():
                if type(jvc_dler) is Jvc_downloader and jvc_dler.stop_dl:
                    # Le dl vient de se terminer, zippage et recup du chemin de l'archive
                    zipath = self.zippify(jvc_dler, client_id)
                    logger.log("zip créé pour client "+client_id+" (path="+zipath+")")
                    dl_finished.append((client_id, zipath, jvc_dler.to_json()))
                elif type(jvc_dler) is list:
                    # Archive prete, en attente du dl depuis client
                    zipinfo = jvc_dler
                    zipinfo[0] += 1
                    if zipinfo[0]*INTERVAL > self.dler.MAX_TIME_KEEPING:
                        overtimed.append(client_id)
            for client_id, zipath, topic_info in dl_finished:
                self.dler.curr_clients[client_id] = [0, zipath, topic_info]
            for client_id in overtimed:
                self.delete_client_res(client_id)
            time.sleep(INTERVAL)
        
    def zippify(self, jvc_dler, client_id):
        logger.log("création zip pour " + client_id)
        zip_path = '.' + ZIP_DIR_PATH+ '/' + jvc_dler.target_folder
        target_dir = DL_DIR_PATH+'/'+client_id+'/'+jvc_dler.target_folder
        shutil.make_archive(zip_path, 'zip', target_dir)
        return zip_path+'.zip'
    
        
class Downloader():

    def __init__(self, max_client=10):
        self.MAX_TIME_KEEPING = 20
        self.p_controller = Param_controller()
        self.max_client = max_client
        self.curr_clients = {}
        os.makedirs(DL_DIR_PATH, exist_ok=True)
        self.zip_thread = Zipper_thread(self)
        self.zip_thread.start()

    def accept_client(self, client_req):
        if len(self.curr_clients.keys()) >= self.max_client:
            return (False, "Too much clients")
        client_id = self.get_client_id(client_req)
        try:
            jvc_dler_thread = self.new_client_thread(client_req, client_id)
            self.curr_clients[client_id] = jvc_dler_thread.jvc_dler
            jvc_dler_thread.start()
            return (True, jsoner.processing(jvc_dler_thread.jvc_dler))
        except Exception as e:
            return (False, str(e))
        
    def get_client_id(self, req):
        return req.client_address[0]
        
    def init_client_dir(self, client_id, params):
        client_path = DL_DIR_PATH + "/" + client_id
        os.makedirs(client_path, exist_ok=True)
        params["path"] = client_path
        return client_path
        
    def new_client_thread(self, client_req, id):
        pre_param_list = self.parse_regex(client_req)
        params = self.p_controller.regularize_param(pre_param_list)
        self.init_client_dir(id, params)
        return DLing_thread(params)
        
    def client_status_json(self, client_id):
        client = self.curr_clients.get(client_id)
        if type(client) is Jvc_downloader:
            if client.stop_dl:
                return jsoner.zipping(client)
            else:
                return jsoner.processing(client)
        elif type(client) is list:
            return jsoner.dl_done(client)
        else:
            return jsoner.cancelled(client_id)
        
    def parse_regex(self, client_req):
        content_type = client_req.headers["Content-Type"]
        content_length = int(client_req.headers["Content-Length"])
        body =  client_req.rfile.read(content_length).decode('utf-8')
        boundary = content_type[content_type.find("=")+1:]
        clean = body.split(boundary+'\r\n')
        p = re.compile(r'name="(.*)"\r\n\r\n(.*)\r')
        return p.findall(body)
    
    def kill_all_threads(self):
        self.zip_thread.stop()
        for _, jvc_dler in self.curr_clients.items():
            if type(jvc_dler) is Jvc_downloader:
                jvc_dler.stop()
        time.sleep(2)
        return 0
        
        
class ExtensionRequestHandler(SimpleHTTPRequestHandler):
        
    def do_GET(self):
        self.protocol_version = 'HTTP/1.1'
        print("--------------------------------")
        logger.log("# GET received from " + str(self.client_address))
        #logger.log("# Headers : \n" + str(self.headers))
        logger.log("    for the path " + self.path)
        #logger.log("BODY :" + self.rfile.read(self.headers['Content-Length']).decode('utf-8'))
        if not "zips" in self.path:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            to_send = bytes(dler.client_status_json(dler.get_client_id(self)), "utf-8")
            self.send_header('Content-Length', str(len(to_send)))
            self.end_headers()
            self.wfile.write(to_send)
        else:
            super().do_GET()
        
        
        
    def do_POST(self):
        self.protocol_version = 'HTTP/1.1'
        logger.log("# POST received from " + str(self.client_address))
        (accept_client, state) = dler.accept_client(self)

        if accept_client:
            # Script lance pour le nouveau client 
            code = 200
            resp = bytes(state, "utf-8")
        else:
            # Erreur url invalide, trop de clients..
            code = 503
            resp = bytes(jsoner.error(state), "utf-8")

        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)
        logger.log("# POST reply to "+str(self.client_address)+" code :"+str(code))
        
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Override de certaines methodes de HTTPServer pour multithreading"""

# constantes
DOMAIN = "http://localhost:8000"
DL_DIR_PATH = "./clients_dl"
ZIP_DIR_PATH = "/zips"
INTERVAL = 3


if __name__=="__main__":
    try:
        jsoner = JSONer()
        logger = Logger()
        dler = Downloader()
        httpd = ThreadedHTTPServer(('localhost', 8000), ExtensionRequestHandler)
        print("#########--Lancement du serveur--#########")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("---------Ctrl+c---------")
        httpd.server_close()
        dler.kill_all_threads()
        from sys import exit as exit
        exit(0)
        
