console.log("script options");

//-------- utilitaires --------
onError = browser.extension.getBackgroundPage().onError;    
display_settings = browser.extension.getBackgroundPage().display_settings;
clean_memory = browser.extension.getBackgroundPage().clean_memory;


//-------- chargement des paramètres --------
function load_settings(){
    function onGot(settings){
        basic_options = settings.basic_options;
        spec_options = settings.spec_options;
        var chk = document.querySelectorAll("input[type=checkbox]");
        for(var i=0, l=chk.length; i<l; i++){
            chk[i].checked = basic_options[chk[i].id] || spec_options[chk[i].id];
        }
        display_settings("storage apres (re)chargement :");
    }
    getting = browser.storage.local.get(["basic_options", "spec_options"]);
    getting.then(onGot, onError);
};


//-------- écriture des nouveaux paramètres --------
function save_settings(){
    function add_on_obj(obj, form_id){
        var form_elmt = document.querySelector("form[id="+form_id+"]");
        var chk = form_elmt.querySelectorAll("input[type=checkbox]");
        for(var i=0, l=chk.length; i<l; i++){
            obj[chk[i].id] = chk[i].checked;
        }
        var others = form_elmt.querySelectorAll("input[type=radio],input[type=number]");
        for(var i=0, l=others.length; i<l; i++){
            if(others[i].type == "radio" && others[i].checked)
                obj[others[i].name] = others[i].value;
            else
                obj[others[i].name] = others[i].value;
        }
    }
    
    function onGot(){
        console.log("Paramètres sauvegardés !");
        display_settings("storage apres nouvelle sauvegarde :");
    }
    add_on_obj(basic_options = {}, "basic");
    add_on_obj(spec_options = {}, "spec");
    browser.storage.local.set({basic_options, spec_options}).then(onGot, onError);
};



document.addEventListener("DOMContentLoaded", load_settings);
document.getElementById("clean_memory").addEventListener("click", clean_memory);
document.getElementById("basic").addEventListener("submit", save_settings);