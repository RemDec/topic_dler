#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from tkinter import *
from tkinter import filedialog
from jvc_downloader import *
import threading
import sys
from os import path

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=True, fill=BOTH)
        self.v_elmts = []
        self.vars = {}
        self.widgets = {}
        
        self.img_ok = IntVar()
        self.webm_ok = IntVar()
        self.voca_ok = IntVar()
        self.vars['types_ok'] = (self.img_ok, self.webm_ok, self.voca_ok)
        self.vars['path'] = StringVar()
        self.vars['path'].set("<current working directory>/nom_topic")
        self.vars['url'] = StringVar()
        self.vars['url'].set("<empty URL>")
        self.vars['stick'] = IntVar()
        self.vars['stick'].set(0)
        self.vars['stick_ctrl'] = DoubleVar()
        self.vars['stick_ctrl'].set(1)
        self.vars['short'] = IntVar()
        self.vars['verb'] = IntVar()
        self.vars['power'] = DoubleVar()
        self.vars['power'].set(1)
        
        
        self.p = PanedWindow(self, orient=VERTICAL)
        self.logf = Frame(self, padx=5)
        self.log = Text(self.logf, padx=5, pady=5)
        
        self.create_widgets()
        self.create_mainframe()

    # Type de ressources
    def fill_res(self, box):
        btn_img = Checkbutton(box, text="images", padx=10, variable=self.img_ok)
        btn_img.select()
        btn_webm = Checkbutton(box, text="webm", padx=10, variable=self.webm_ok)
        btn_webm.select()
        btn_voca = Checkbutton(box, text="vocaroo", padx=10, variable=self.voca_ok)
        btn_voca.select()
        btn_img.pack(side=LEFT)
        btn_webm.pack(side=LEFT)
        btn_voca.pack(side=LEFT)
        
    # Controle stickers
    def fill_stickers(self, box):
        btn_all = Radiobutton(box, text="Toutes", variable=self.vars['stick'], value=0)
        btn_onlyimg = Radiobutton(box, text="Pas de stickers", variable=self.vars['stick'], value=1)
        btn_stickers = Radiobutton(box, text="Stickers", variable=self.vars['stick'], value=2)
        slide = Scale(box, variable=self.vars['stick_ctrl'], from_=0, to=1, orient=HORIZONTAL, resolution=0.1)
        
        btn_all.pack(side=LEFT)
        btn_onlyimg.pack(side=LEFT)
        btn_stickers.pack(side=LEFT)
        slide.pack(side=RIGHT)
        
        
    # Chemin de sauvegarde
    def modif_path(self):
        new_path = filedialog.askdirectory(title="Sélectionner dossier d'enregistrement")
        if new_path == "":
            self.vars['path'].set("<current working directory>/nom_topic")
        else:
            self.vars['path'].set(new_path)
        
    def fill_path(self, box):
        label_path = Label(box, textvariable=self.vars['path'])
        btn_path = Button(box, text="...", command=self.modif_path)
        label_path.pack(side=LEFT)
        btn_path.pack(side=RIGHT)
        
    # Parametres
    def fill_param(self, box):
        btn_short = Checkbutton(box, text="abréviations", padx=1, variable=self.vars['short'])
        btn_short.select()
        btn_verb = Checkbutton(box, text="verbeux", variable=self.vars['verb'])
        btn_verb.select()        
        label_power = Label(box, text="puissance:")
        slide = Scale(box, variable=self.vars['power'], from_=0, to=1, orient=HORIZONTAL, resolution=0.1)
        
        btn_short.pack(side=LEFT)
        btn_verb.pack(side=LEFT)
        slide.pack(side=RIGHT)
        label_power.pack(side=RIGHT)
    
    # Input de l'URL
    def clean_entry(self, event):
        if self.vars['url'].get() == "<empty URL>":
            self.widgets['url_entry'].delete(0, END)
        
    def fill_URL_zone(self):
        comp_frame = Frame(self.p)
        input_url = Entry(comp_frame, textvariable=self.vars['url'])
        self.widgets['url_entry'] = input_url
        input_url.bind('<Button-1>', self.clean_entry)
        input_url.bind('<Return>', self.launch_dl)
        btn_go = Button(comp_frame, text="GO", command=self.launch_dl)
        
        input_url.pack(side=LEFT, expand=True, fill=X)
        btn_go.pack(side=RIGHT, padx=5)
        self.v_elmts.append(comp_frame)
        
    # Initialisation
    def create_named_box(self, boxname):
        box = LabelFrame(self.p, text=boxname, padx=10, pady=10)
        self.v_elmts.append(box)
        return box
        
    def create_widgets(self):
        res_type_box = self.create_named_box("types de ressource")
        self.fill_res(res_type_box)
        
        stick_box = self.create_named_box("tri des images")
        self.fill_stickers(stick_box)
        
        path_box = self.create_named_box("dossier cible")
        self.fill_path(path_box)
        
        param_box = self.create_named_box("paramètres")
        self.fill_param(param_box)
        
        self.fill_URL_zone()
        
    def create_mainframe(self):
        for elmt in self.v_elmts:
            self.p.add(elmt)
        self.p.pack(expand=True, fill=X, padx=10, pady=10, side=LEFT)
        
        self.logf.pack(side=RIGHT)
        
    # Appel au script
    def freeze_vars(self):
        frozen = {}
        for k, v in self.vars.items():
            try:
                frozen[k]= v.get()
            except AttributeError:
                if isinstance(v, tuple):
                    t = ()
                    for e in v:
                        try:
                            t += (e.get(),)
                        except:
                            t += (e,)
                frozen[k] = t
        return frozen
        
    def launch_dl(self, event=None):
        if self.vars['url'].get() in ["", "<empty URL>"]:
            self.vars['url'].set("<empty URL>")
            return None
        frozen = self.freeze_vars()
        try:
            dl_thread = Jvc_dl_thread(frozen, self.log)
            dl_thread.start()
        except Page_not_foundError as e:
            print(e)
        


class Jvc_dl_thread(threading.Thread):
    def __init__(self, params, log_widget):
        threading.Thread.__init__(self)
        self.log = log_widget
        self.log.pack()
        self.jvc_dl = Jvc_downloader(params, self.log)
        
    def run(self):
        if self.jvc_dl.verb:
            self.log.delete("0.0", END)
        self.jvc_dl.start_dl()
        
        
if __name__ == "__main__":

    if getattr(sys, 'frozen', False): # PyInstaller adds this attribute
        # Running in a bundle
        CurrentPath = sys._MEIPASS
    else:
        # Running in normal Python environment
        CurrentPath = os.path.dirname(__file__)

    root = Tk()
    root.title("topic_DLer by Kyprinite")
    folder_path = path.join(CurrentPath, "data")
    root.iconbitmap(path.join(folder_path, "mini.ico"))
    app = Application(master=root)
    app.mainloop()


