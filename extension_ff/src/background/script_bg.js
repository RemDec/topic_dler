console.log("script background |");

//-------- utilitaires --------
function onError(error){console.log('Error:' + error)};

function isEmpty(obj) {
    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            return false;
    }
    return true;
};

function disp_formData(form){
    for (var [key, value] of form.entries()) { 
      console.log(key, value);
    }
}
//-------- accès stockage --------
function display_settings(prefix){
    function onGot(items){
        console.log(prefix);
        console.log(items);
    }

    getting = browser.storage.local.get(null);
    getting.then(onGot, onError);
};

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

function clean_memory(){
    function onCleared(){
        display_settings("Après nettoyage");
        set_default();
    }
    display_settings("Preparation au nettoyage, état actuel :");
    var clearStorage = browser.storage.local.clear();
    clearStorage.then(onCleared, onError);
};

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

function download(url){
    function onStartDL(id){
        console.log("Début du DL de " + url);
    }
    console.log("DL >"+url+"\n type" + typeof url);
    var downloading = browser.downloads.download({"url":url});
    downloading.then(onStartDL, onError);
}

//-------- communications serveur --------

function Requester(ask_serv_delay=2){
    
    this.ask_serv_delay = ask_serv_delay;
    this.xhr = new XMLHttpRequest();
    this.last_resp = "";
    this.server = "http://localhost:8000";
    this.timeout_id = null;
    
    this.create_request = function(form, url="http://localhost:8000"){
        console.log("lancement requete post");
        function onChange(){
            //console.log(this);
            if(this.readyState===4){
                console.log(this.responseText);
                onChange.req.last_resp = this.responseText;
                console.log(onChange.req);
                onChange.req.start_ask_serv();
            }
        }
        onChange.req = this;
        console.log(this);
        this.xhr = new XMLHttpRequest();
        this.xhr.addEventListener('readystatechange', onChange);
        this.xhr.open("POST", url);
        this.xhr.send(form);
    };
    
    this.treat_response = function(){
        console.log("Traitement de la réponse : \n");
        var json_resp = JSON.parse(this.last_resp);
        var dler = json_resp["jvc_dler"];
        var zip = json_resp["archive"];
        console.log(json_resp);
        switch(json_resp.status){
            case "processing":
                console.log("DL serveur en cours : "+dler.nbr_dl+" objets pour "+dler.curr_page+"/"+dler.max_page+" pages");
                break;
            case "zipping":
                console.log("Zippage en cours");
                break;
            case "done":
                console.log("DL serveur terminé, url ="+zip.url);
                clearInterval(this.timeout_id);
                download(zip.url);
                break;
            case "cancelled":
                console.log("Aucun client serveur pour l'IP " + json_resp.address);
                clearInterval(this.timeout_id);                
                break;
            default:
                console.log("Status serveur inconnu");
        }
    };
    
    this.start_ask_serv = function(){
        function onResponse(){
            //console.log(this.responseText);
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
        console.log(this);
        onResponse.req = this;
        this.timeout_id = setInterval(delayed_send, 5000, this);
    };
        
};

var requester = new Requester();

function init_request(fast_options){
    function onGot(stor){
        var spec = stor["spec_options"];
        for (var key in spec) {
            if (spec.hasOwnProperty(key)) {
                fast_options.append(key, spec[key]);
            }
        }
        requester.create_request(fast_options, "http://localhost:8000");
    }
    browser.storage.local.get("spec_options").then(onGot, onError);
};


//-------- events --------
function report_history(event){
    function save_in_storage(historic, event){
        //event de le forme event = {ev_type:"..", ev_carac:{url:"..", etc}}
        //history de la forme history = {ev_type1:[carac1, carac2,..], ev_type2:[],..}        
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

