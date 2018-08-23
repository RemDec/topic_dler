console.log("popup!");

//Utilitaires navigateur
onError = browser.extension.getBackgroundPage().onError;
report_history = browser.extension.getBackgroundPage().report_history;



function is_jvc_tab(tab_name){
    if(~(limit = tab_name.indexOf("sur le forum ")))
        return tab_name.substring(0, limit-1);
    return false;
};

function find_jvc_tab(){
    var curr_topic_name, res;
    var all_tabs_prom = browser.tabs.query({currentWindow: true});
    function find_first_tab(all_tabs){
        for(var j=0; j<2; j++){
            for(let tab of all_tabs){
                if(curr_topic_name = is_jvc_tab(tab.title)){
                    set_curr_topic(curr_topic_name, tab.url);
                    return true;
                }
            }
            all_tabs = browser.tabs.query({currentWindow: false});
        }
    }
    all_tabs_prom.then(find_first_tab, onError);
};

//Mutateurs popup
function set_curr_topic(name, url){
    var txt = document.getElementById("topic_name");
    txt.innerHTML = name;
    txt.url = url;
    report_history({ev_type:"found_topic", carac:{name:name, url:url}});
};

//Events
function open_settings(){
    browser.runtime.openOptionsPage();
};

function refresh_curr_topic(e){
    //document.getElementById("refresh").style.transform = "rotate(90deg)";
    function change_curr(tabs){
        var curr_tab = tabs[0];
        var curr_topic_name = is_jvc_tab(curr_tab.title);
        if(curr_topic_name)
            set_curr_topic(curr_topic_name, curr_tab.url);
        else
            find_jvc_tab();
    }
    var querying = browser.tabs.query({active:true, currentWindow:true});
    querying.then(change_curr, function (tab_error) {console.log('Error: ${tab_error}')});
};


function load_basic_settings(){
    function onGot(settings){
        basic_options = settings.basic_options;
        var chk = document.querySelectorAll(".basic");
        for(var i=0, l=chk.length; i<l; i++){
            chk[i].checked = basic_options[chk[i].id];
        }
        display_settings("storage apres (re)chargement :");
    }
    getting = browser.storage.local.get("basic_options");
    getting.then(onGot, onError);
};

function display_history(){
    function onOpened(new_window){
        
    }
    var win = {type:"panel", url:"../background/history.html",
               height:600, width:800, titlePreface:"Historique topic_dler"};
    browser.windows.create(win).then(onOpened, onError);
    
}


document.getElementById("settings").addEventListener('click', open_settings);
document.addEventListener("DOMContentLoaded", refresh_curr_topic);
document.addEventListener("DOMContentLoaded", load_basic_settings);
document.getElementById("refresh").addEventListener('click', refresh_curr_topic);
document.getElementById("history").addEventListener('click', display_history);