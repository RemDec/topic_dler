#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from tkinter import *
from tkinter import filedialog
from jvc_downloader import *
from os import path, getenv
from subprocess import run
import threading, sys, subprocess


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
        self.post_ok = IntVar()
        self.risi_ok = IntVar()
        self.vars['types_ok'] = (self.img_ok, self.webm_ok, self.voca_ok, self.post_ok, self.risi_ok)
        self.vars['path'] = StringVar()
        self.vars['path'].set("<current working directory>")
        self.vars['nf'] = IntVar()
        self.vars['nf'].set(1)
        self.vars['open_explorer'] = IntVar()
        self.vars['open_explorer'].set(1)
        self.vars['stick'] = IntVar()
        self.vars['stick'].set(0)
        self.vars['stick_ctrl'] = DoubleVar()
        self.vars['stick_ctrl'].set(1)
        self.vars['only_op'] = IntVar()
        self.vars['sel_pseudos'] = []
        self.vars['pseudo'] = StringVar()
        self.vars['short'] = IntVar()
        self.vars['auto_names'] = IntVar()
        self.vars['verb'] = IntVar()
        self.vars['power'] = DoubleVar()
        self.vars['power'].set(0.5)
        self.vars['url'] = StringVar()
        self.vars['url'].set("<empty URL>")
        
        
        self.p = PanedWindow(self, orient=VERTICAL)
        self.logf = Frame(self, padx=5)
        self.log = Text(self.logf, padx=5, pady=5)
        
        self.create_widgets()
        self.create_mainframe()

    # Type de ressources
    def adjust_res(self):
        if self.risi_ok.get():
            self.post_ok.set(1)
            self.vars['only_op'].set(1)
    
    def fill_res(self, box):
        btn_img = Checkbutton(box, text="images", padx=10, variable=self.img_ok)
        btn_img.select()
        btn_webm = Checkbutton(box, text="webm", padx=10, variable=self.webm_ok)
        btn_webm.select()
        btn_voca = Checkbutton(box, text="vocaroo", padx=10, variable=self.voca_ok)
        btn_voca.select()
        btn_posts = Checkbutton(box, text="posts", padx=10, variable=self.post_ok)
        btn_risi = Checkbutton(box, text="[RISITAS]", padx=10, variable=self.risi_ok, command=self.adjust_res)
        
        btn_img.pack(side=LEFT)
        btn_webm.pack(side=LEFT)
        btn_voca.pack(side=LEFT)
        btn_posts.pack(side=LEFT)
        btn_risi.pack(side=LEFT)
        
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
            self.vars['path'].set("<current working directory>")
        else:
            self.vars['path'].set(new_path)
        
    def fill_path(self, box):
        label_path = Label(box, textvariable=self.vars['path'])
        bot_frame = Frame(box)
        btn_path = Button(bot_frame, text="...", command=self.modif_path, padx=5)
        btn_oe = Checkbutton(bot_frame, text="post-ouverture", variable=self.vars['open_explorer'])
        btn_nf = Checkbutton(bot_frame, text="nouveau dossier", variable=self.vars['nf'], padx=20)
        
        label_path.pack(side=TOP, fill=X)
        bot_frame.pack(side=BOTTOM, fill=X)
        btn_path.pack(side=LEFT)
        btn_oe.pack(side=RIGHT)
        btn_nf.pack(side=RIGHT)
        
    # Forumeurs cibles
    def add_to_list(self, pseudo):
        pseudo = pseudo.strip('\n ')
        if pseudo not in self.vars['sel_pseudos'] and pseudo != "":
            self.vars['sel_pseudos'].append(pseudo)
            self.widgets['ps_listbox'].insert(END, pseudo)
        
    def del_from_list(self):
        delta = 0
        for ind in self.widgets['ps_listbox'].curselection():
            del self.vars['sel_pseudos'][ind-delta]
            self.widgets['ps_listbox'].delete(ind-delta)
            delta += 1
        
    def fill_listbox(self):
        for p in self.vars['sel_pseudos']:
            self.widgets['ps_listbox'].insert(END, p)
        
    def add_new_pseudo(self, event=None):
        self.add_to_list(self.vars['pseudo'].get())
        self.vars['pseudo'].set("")
    
    def fill_pseudo(self, box):
        btn_add = Button(box, text="Ajouter", command=self.add_new_pseudo, padx=10)
        entry_pseudo = Entry(box, textvariable=self.vars['pseudo'])
        entry_pseudo.bind('<Return>', self.add_new_pseudo)
        
        entry_pseudo.pack(side=LEFT, expand = True, fill=X)
        btn_add.pack(side=RIGHT, padx=10)
        
    
    def disp_pseudo_frame(self):
        ps_frame = Toplevel(self)
        ps_frame.title("Ciblage des forumeurs")
        list_pseudo = Listbox(ps_frame, selectmode=MULTIPLE)
        self.widgets['ps_listbox'] = list_pseudo
        self.fill_listbox()
        add_box = self.create_named_box("ajout de pseudos", ps_frame)
        self.fill_pseudo(add_box)
        btn_del = Button(ps_frame, text="Supprimer sélection", command=self.del_from_list, pady=2)
        
        list_pseudo.pack(side=TOP, expand=True, fill=X)
        add_box.pack(side=BOTTOM, expand=True, fill=X)
        btn_del.pack(side=BOTTOM)
        
    
    def fill_msg(self, box):
        btn_op = Checkbutton(box, text="cibler auteur", variable=self.vars['only_op'])
        btn_others = Button(box, text="autres", command=self.disp_pseudo_frame)
        
        btn_op.pack(side=LEFT)
        btn_others.pack(side=RIGHT)
        
    # Parametres
    def fill_param(self, box):
        comp_frame = Frame(box)
        comp_frame2 = Frame(box)
        btn_short = Checkbutton(comp_frame, text="abréviations", padx=7, variable=self.vars['short'])
        btn_short.select()
        btn_verb = Checkbutton(comp_frame, text="verbeux", padx=7, variable=self.vars['verb'])
        btn_verb.select()
        btn_names = Checkbutton(comp_frame, text="noms autos", padx=7, variable=self.vars['auto_names'])
        label_power = Label(comp_frame2, text="puissance:")
        slide = Scale(comp_frame2, variable=self.vars['power'], from_=0, to=1, orient=HORIZONTAL, resolution=0.1)

        
        btn_short.pack(side=LEFT)
        btn_verb.pack(side=LEFT)
        btn_names.pack(side=RIGHT)
        slide.pack(side=RIGHT)
        label_power.pack(side=RIGHT)

        comp_frame.pack(side=TOP)
        comp_frame2.pack(side=BOTTOM)
    
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
    def create_named_box(self, boxname, parent=None):
        given_parent =True
        if parent is None:
            parent = self.p
            given_parent = False
        box = LabelFrame(parent, text=boxname, padx=10, pady=10)
        if not(given_parent):
            self.v_elmts.append(box)
        return box
        
    def create_widgets(self):
        res_type_box = self.create_named_box("types de ressource")
        self.fill_res(res_type_box)
        
        stick_box = self.create_named_box("tri des images")
        self.fill_stickers(stick_box)
        
        path_box = self.create_named_box("dossier cible")
        self.fill_path(path_box)

        msg_box = self.create_named_box("forumeurs cibles")
        self.fill_msg(msg_box)

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
                if isinstance(v, list):
                  t = v  
                elif isinstance(v, tuple):
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
            self.log.insert('end', str(e) +"\n")
            self.log.see('end')


            
            
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
        self.open_explorer()
        
    def open_explorer(self):
        if os.name == 'nt' and self.jvc_dl.params['open_explorer']:
            path = os.path.normpath(self.jvc_dl.dir)
            FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
            if os.path.isdir(path):
                subprocess.run([FILEBROWSER_PATH, path])

                
if __name__ == "__main__":

    if getattr(sys, 'frozen', False): # PyInstaller adds this attribute
        # Running in a bundle
        currentPath = sys._MEIPASS
    else:
        # Running in normal Python environment
        currentPath = os.path.dirname(__file__)

    root = Tk()
    root.title("topic_DLer by Kyprinite")
    folder_path = path.join(currentPath, "data")
    root.iconbitmap(path.join(folder_path, "mini.ico"))
    app = Application(master=root)
    app.mainloop()


