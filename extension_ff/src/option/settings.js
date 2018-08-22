console.log("script options");

function onError(error){console.log('Error: ${error}')};
    
function display_settings(prefix){
    function onGot(items){
        console.log(prefix);
        console.log(items);
    }

    getting = browser.storage.local.get(null);
    getting.then(onGot, onError);
};

function load_settings(){
    function onGot(settings){
        basic_options = settings.basic_options;
        var chk = document.querySelectorAll("input[type=checkbox]");
        for(var i=0, l=chk.length; i<l; i++){
            chk[i].checked = basic_options[chk[i].id];
        }
        display_settings("storage apres (re)chargement :");
    }
    getting = browser.storage.local.get("basic_options");
    getting.then(onGot, onError);
};


function save_settings(){
    function onGot(){
        console.log("Paramètres sauvegardés !");
        display_settings("storage apres nouvelle sauvegarde :");
    }
    var new_settings = {};
    var chk = document.querySelectorAll("input[type=checkbox]");
    for(var i=0, l=chk.length; i<l; i++){
        new_settings[chk[i].id] = chk[i].checked;
    }
    var basic_options = new_settings;
    browser.storage.local.set({basic_options}).then(onGot, onError);
};

document.addEventListener("DOMContentLoaded", load_settings);
document.getElementById("basic").addEventListener("submit", save_settings);