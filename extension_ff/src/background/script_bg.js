console.log("script background |");

//-------- utilitaires --------
function onError(error){console.log('Error:' + error)};

/* Retourne vrai si un objet est vide ( {} )*/
function isEmpty(obj) {
    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            return false;
    }
    return true;
};

/* Affiche le contenu des couples clef - valeur d'un formulaire */
function disp_formData(form){
    for (var [key, value] of form.entries()) { 
      console.log(key, value);
    }
}
//-------- accès stockage --------
/* Affiche tout le contenu du stockage intra extension */
function display_settings(prefix){
    function onGot(items){
        console.log(prefix);
        console.log(items);
    }
    getting = browser.storage.local.get(null);
    getting.then(onGot, onError);
};

/* Remet tous les parametres a leur valeur par defaut, clean toute la memoire */
function set_default(){
    function onGot(options){
        display_settings("Réécriture si mémoire vide:");
        if(isEmpty(options)){
            basic_options = {
                img_ok: 1, webm_ok: 1, voca_ok: 0,
                posts_ok: 0, risi_ok: 0,
                menu_kheys:1
            };
            spec_options = {
                type_img: "all_img", only_op: 0,
                max_size: 500, autonames: 0
            };
            historic = {found_topic:[], requests:[], old_dl:[]};
            browser.storage.local.set({basic_options, spec_options, historic})
                .then(function(){display_settings('Ecriture param défaut :')}, onError);
        }
    };
    let getting_basics = browser.storage.local.get(["basic_options","spec_options"]);
    getting_basics.then(onGot, onError);
};

/* Efface toute la memoire et restaure les valeurs par defaut */
function clean_memory(){
    function onCleared(){
        display_settings("Après nettoyage");
        set_default();
    }
    display_settings("Preparation au nettoyage, état actuel :");
    var clearStorage = browser.storage.local.clear();
    clearStorage.then(onCleared, onError);
};

/* Applique une fonction fun sur l'objet du stockage interne id (args passés à fun)*/
function apply_on_storage(stor_id, fun, args){
    function onGot(stor){
        function onWritten(){display_settings("Après appli "+fun.name+" sur "+stor_id)};
        fun(stor[stor_id], args);
        var to_set = {};
        to_set[stor_id] = stor[stor_id];
        browser.storage.local.set(to_set).then(onWritten);
    }
    browser.storage.local.get(stor_id).then(onGot, onError);
};

//-------- communications extension --------

/* Lance le DL dans le module de base du naviguateur pour la ressource pointée par url */
function download(url){
    function onStartDL(id){
        console.log("Début du DL de " + url);
    }
    console.log("DL >"+url+"\n type" + typeof url);
    var downloading = browser.downloads.download({"url":url, "headers":[{name:"Access-Control-Allow-Origin", value:"*"}]});
    downloading.then(onStartDL, onError);
}

function cancel_dl(){
    if(requester)
        requester.cancel_getting();
    else
        console.log("Aucun requester instancié");
}

var last_popup_maj = {};

/* Envoie un message au popup pour refresh son affichage avec le contenu
passé en argument ou le dernier contenu enregistré pour l'élément si c'est 
son id qui est passé en arg */
function update_popup(new_val){
    function onSend(){
        last_popup_maj[new_val.elmt_id] = new_val;
        console.log("Maj contenu popup dans le background pour " + new_val.elmt_id);
    }
    if(typeof(new_val) == "string")
        new_val = last_popup_maj[new_val];
    if(new_val){
        var sending = browser.runtime.sendMessage(new_val);
        sending.then(onSend, onSend);
    }
}

/* Action déclenchée a la réception de l'url de l'archive à dl retournée par 
le serveur lors du dernier GET d'actualisation */
function alert_dl_ready(zip, dler){
    var dl_url = zip.url;
    browser.browserAction.setIcon({path:"../../icons/icon-32-notif.png"});
    var popup_dl = {elmt_id:"dl_state", new_class:"dl_link", type:"link_img", topic_title:dler.title,
                    val:"Télécharger l'archive", url:dl_url, img:"../../data/icon-dl.png"};
    update_popup(popup_dl);
    var ev_carac = {name:dl_url, url:dl_url, topic_url:dler.topic_url,
                    topic_title:dler.title, author:dler.author, nbr_dl:dler.nbr_dl,
                    max_page:dler.max_page};
    report_history({ev_type:"old_dl", carac:ev_carac});
}

/* Action déclenchée à la réception d'une réponse au GET d'actualisation indiquant 
que le script tourne encore pour ce client, dler contenant les infos de sa progression */
function alert_progress(dler){
    var p = {elmt_id:"dl_state", new_class:"progress", type:"bar",
            min:0, max:dler.max_page, curr:dler.curr_page, dled:dler.nbr_dl};
    update_popup(p);
}

function alert_error(error){
    var err_msg = typeof(error)=="number" ? "serveur injoignable:"+error : error.reason+"("+error.code+")"; 
    var popup_infos = {elmt_id:"dl_state", new_class:"txt_error",
                       type:"text", val:err_msg};
    update_popup(popup_infos);
}

//-------- communications serveur --------

function Requester(ask_serv_delay=4){
    /* Objet gérant les communications serveur et adaptant le comportement
    de l'extension en fonction des réponses reçues (1 seul DL à la fois) */
    this.ask_serv_delay = ask_serv_delay;
    this.xhr = new XMLHttpRequest();
    this.last_resp = "";
    // this.server = "http://localhost:8000";
    // this.server = "http://81.247.116.134:8000";
    this.server = "http://85.201.215.252:8000";
    this.timeout_id = null;
    
    this.create_request = function(form, url=this.server){
        function onChange(){
            if(this.status===200){
                onChange.req.last_resp = this.responseText;
                onChange.req.start_ask_serv();
                onChange.req.treat_response();
            }else{
                if(this.status===503)
                    alert_error(JSON.parse(this.responseText)["error"]);
                else
                    alert_error(this.status);
            }
        }
        onChange.req = this;
        this.xhr = new XMLHttpRequest();
        this.xhr.timeout = 4000;
        this.xhr.addEventListener('loadend', onChange);
        this.xhr.open("POST", url);
        this.xhr.send(form);
    };
    
    this.start_ask_serv = function(){
        function onResponse(){
            onResponse.req.last_resp = this.responseText;
            onResponse.req.treat_response();
        };
        
        function delayed_send(requester){
            console.log("Envoi d'un GET au serveur ");
            requester.xhr = new XMLHttpRequest();
            requester.xhr.timeout = 10000;
            requester.xhr.addEventListener('loadend', onResponse);
            requester.xhr.open("GET", requester.server);
            requester.xhr.send(null);
        };
        onResponse.req = this;
        this.timeout_id = setInterval(delayed_send, this.ask_serv_delay*1000, this);
    };
    
    this.treat_response = function(){
        console.log("Traitement de la réponse : \n");
        var json_resp = JSON.parse(this.last_resp);
        var dler = json_resp["jvc_dler"];
        var zip = json_resp["archive"];
        console.log(json_resp);
        switch(json_resp.status){
            case "processing":
                console.log("DL serveur en cours : "+dler.nbr_dl+" objets "+dler.curr_page+"/"+dler.max_page+" pages");
                alert_progress(dler);
                break;
            case "zipping":
                console.log("Zippage en cours");
                break;
            case "done":
                console.log("DL serveur terminé, url ="+zip.url);
                clearInterval(this.timeout_id);
                this.timeout_id = null;
                alert_dl_ready(zip, dler);
                break;
            case "cancelled":
                console.log("Aucun client admis par le serveur pour l'IP " + json_resp.address);
                clearInterval(this.timeout_id);
                this.timeout_id = null;
                break;
            default:
                console.log("Status serveur inconnu");
        }
    };
    
    this.is_getting = function(){
        return !(this.timeout_id === null);
    };
    
    this.cancel_getting = function(){
        if(this.is_getting()){
            clearInterval(this.timeout_id);
            this.send_cancel_alert();
            var popup_infos = {elmt_id:"dl_state", new_class:"txt_error",
                                type:"text", val:"requête annulée"};
            update_popup(popup_infos);
        }
    };
      
    this.send_cancel_alert = function(){
        xhr = new XMLHttpRequest();
        xhr.timeout = 5000;
        xhr.open("HEAD", this.server);
        xhr.setRequestHeader('Connection', 'close');
        xhr.send(null);
    }
};

var requester = new Requester();

/* Lancement d'une nouvelle requete au serveur, avec les options rapides 
 en arguments qui priment sur celles contenues dans le stockage */
function init_request(fast_options){
    function onGot(stor){
        var spec = stor["spec_options"];
        for (var key in spec) {
            if (spec.hasOwnProperty(key)) {
                fast_options.append(key, spec[key]);
            }
        }
        requester.create_request(fast_options);
    }
    browser.storage.local.get("spec_options").then(onGot, onError);
    var popup_infos = {elmt_id:"dl_state", new_class:"",
                       type:"text", val:"contact du serveur.."};
    update_popup(popup_infos);
};


//-------- events --------
/* Enregistre dans le stockage (la zone dédiée à l'historique client) l'évènement
 donné, qui doit mentionner son type d'event */
function report_history(event){
    function save_in_storage(historic, event){
        //event de le forme event = {ev_type:"..", carac:{url:"..", etc}}
        //historic de la forme historic = {ev_type1:[carac1, carac2,..], ev_type2:[],..}        
        var all_carac = historic[event.ev_type];
        for(let carac of all_carac){
            if(carac.name == event.carac.name)
                return 0;
        }
        if(all_carac.unshift(event.carac) > 10)
            all_carac.pop();
    }
    console.log("Nouvel event pour l'historique :");
    console.log(event);
    apply_on_storage("historic", save_in_storage, event);
};

document.addEventListener("DOMContentLoaded", set_default);

