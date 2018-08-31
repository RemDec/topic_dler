console.log("popup!");


//-------- utilitaires --------
onError = browser.extension.getBackgroundPage().onError;
report_history = browser.extension.getBackgroundPage().report_history;
init_request = browser.extension.getBackgroundPage().init_request;
cancel_dl = browser.extension.getBackgroundPage().cancel_dl;
download = browser.extension.getBackgroundPage().download;

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

function refresh_icon(){
    browser.browserAction.setIcon({path:"../../icons/icon-32.png"});
}

//-------- mutateurs DOM --------
function init_popup(){
    refresh_icon();
    refresh_curr_topic();
    load_basic_settings();
    refresh_from_bg();
}

function set_curr_topic(name, url){
    var txt = document.getElementById("topic_name");
    txt.innerHTML = name;
    txt.url = url;
    report_history({ev_type:"found_topic", carac:{name:name, url:url}});
};

var cancel_btn = null;

function get_cancel_btn(){
    if(cancel_btn === null){
        var btn = document.createElement("div");
        btn.style = "display:inline-block";
        btn.id = "cancel_dl";
        btn.innerHTML = '<img src="../../data/cancel.png" alt="annuler" width="15px" style="vertical-align:-2px">';
        btn.addEventListener('click', cancel_dl);
        cancel_btn = btn;
        return btn;
    }else
        return cancel_btn;
}

//-------- events --------
function open_settings(){
    browser.runtime.openOptionsPage();
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

function display_history(){
    function onOpened(new_window){}
    var win = {type:"panel", url:"../background/history.html",
               height:600, width:800, titlePreface:"Historique topic_dler"};
    browser.windows.create(win).then(onOpened, onError);
}

function send_request(event){
    console.log("Init new fast request")
    var url;
    if(event.target.id == "dl_fast_button_url")
        url = document.getElementById("url_input").value;
    else
        url = document.getElementById("topic_name").url;
    if(url){
        var formData = new FormData(document.getElementById("fast_options"));
        formData.append('url', url);
        init_request(formData);
        report_history({ev_type:"requests", carac:{url:url}});
    }
}

//----- messages extension ------

function update_dl_state(request){
    var target = document.getElementById(request.elmt_id);
    if(request.type == "text" || request.type == "link_img"){
        target.innerHTML = request.val;
        target.className = request.new_class;
    }
    if(request.type == "link_img"){
        target.innerHTML = "<div id='dl_div'>"+target.innerHTML+"</div>";
        var img = document.createElement("img");
        img.src = request.img; img.alt="dl_img";
        target.firstChild.appendChild(img);
        target.addEventListener('click', function(){download(request.url);refresh_icon()});
    }
    if(request.type == "bar"){
        target.innerHTML = "<progress id='prog_bar' value='"+request.curr+"' max='"+request.max+"'/>";
        target.appendChild(document.createTextNode(request.dled + "objets"));
        target.appendChild(get_cancel_btn());
    }
}

var refresh_fcts = {dl_state:update_dl_state};

function handleMessage(request, sender, sendResponse){
    refresh_fcts[request.elmt_id](request);
}

function refresh_from_bg(){
    for(let id in refresh_fcts){
        browser.extension.getBackgroundPage().update_popup(id);
    }
}

document.addEventListener("DOMContentLoaded", init_popup);
document.getElementById("settings").addEventListener('click', open_settings);
document.getElementById("refresh").addEventListener('click', refresh_curr_topic);
document.getElementById("history").addEventListener('click', display_history);
document.getElementById("dl_fast_button").addEventListener('click', send_request);
document.getElementById("dl_fast_button_url").addEventListener('click', send_request);

browser.runtime.onMessage.addListener(handleMessage);