console.log("script background |");
//Set local default settings if undefined

function onError(error){console.log('Error:' + error)};

function isEmpty(obj) {
    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            return false;
    }
    return true;
};

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
                type_img: "all_img", op_target: 0,
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
}

function apply_on_storage(stor_id, fun, args){
    function onGot(stor){
        fun(stor[stor_id], args);
        function onWritten(){display_settings("Après appli "+fun.name+" sur "+stor_id)};
        var to_set = {};
        to_set[stor_id] = stor[stor_id];
        browser.storage.local.set(to_set).then(onWritten);
    }
    browser.storage.local.get(stor_id).then(onGot, onError);
}

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
}


document.addEventListener("DOMContentLoaded", set_default);