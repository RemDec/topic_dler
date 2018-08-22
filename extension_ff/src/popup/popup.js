console.log("popup!");

//Utilitaires navigateur
function onError(error){console.log('Error: ${error}')};

function is_jvc_tab(tab_name){
    if(~(limit = tab_name.indexOf("sur le forum ")))
        return tab_name.substring(0, limit);
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
    all_tabs_prom.then(find_first_tab);
};

//Mutateurs popup
function set_curr_topic(name, url){
    var txt = document.getElementById("topic_name");
    txt.innerHTML = name;
    txt.url = url;
};

//Events
function open_settings(){
    browser.runtime.openOptionsPage();
};

function refresh_curr_topic(e){
    //document.getElementById("refresh").style.transform = "rotate(90deg)";
    var querying = browser.tabs.query({active:true, currentWindow:true});
    querying.then(function (tabs){
                    var curr_tab = tabs[0];
                    var curr_topic_name = is_jvc_tab(curr_tab.title);
                    if(curr_topic_name)
                        set_curr_topic(curr_topic_name, curr_tab.url);
                    else
                        find_jvc_tab();
                }, function (tab_error) {console.log('Error: ${tab_error}')});
};


function load_settings(){
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



document.getElementById("settings").addEventListener('click', open_settings);
document.addEventListener("DOMContentLoaded", refresh_curr_topic);
document.addEventListener("DOMContentLoaded", load_settings);
document.getElementById("refresh").addEventListener('click', refresh_curr_topic);