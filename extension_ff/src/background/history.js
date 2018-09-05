console.log("Script historique");
onError = browser.extension.getBackgroundPage().onError;

function app_children(parent, child_array){
    for(var i=0, l=child_array.length; i<l; i++){
        parent.appendChild(child_array[i]);
    }
}

function div_it(div_class, style="", text=""){
    var div = document.createElement("div");
    div.className = div_class;
    if(style)
        div.style = style;
    if(text)
        div.innerHTML = text;
    return div;
}

function link_it(link, short_it=true, shortcut="Lien JVC", blank=true){
    var a = document.createElement("a");
    a.href = link;
    a.target = "_blank";
    /*
    if (short_it && link.length > 70)
        link = link.substring(0, 5) + "[..]" + link.substring(55);
    if (link.length > 40)
        link = "Lien JVC";*/
    if(short_it)
        a.innerHTML = shortcut;
    else
        a.innerHTML = link;
    return a;
};

function get_copy_button(url){
    function copy_rel_link(event){
        url_node = event.target.lastChild;
        url_node.style = "display:block";
        url_node.select();
        document.execCommand("copy");
        url_node.style = "display:none";
    }
    var btn = document.createElement("button");
    btn.innerHTML = "Copier <textarea style='display:none'>"+ url +"</textarea>";
    btn.addEventListener('click', copy_rel_link);
    return btn;
};

function get_linked_line(url, prefix = "Lien", copy_btn=true, classname="prefixed"){
    var btn = copy_btn ? get_copy_button(url) : "";
    var prefix_linked = link_it(url, true, prefix);
    var h = copy_btn ? prefix_linked.outerHTML+" ["+btn.outerHTML+"]" : prefix_linked.outerHTML;
    return div_it(classname, "", h+" : <em>" + url + "</em>");
}

function load_topics(topics){
    console.log("Chargement des topics visités");
    var main_div = document.getElementById("found_topic");
    var new_elmt, link, copy;
    for(let topic of topics){
        console.log(topic.name);
        new_elmt = div_it("topic");
        new_elmt.innerHTML = "<span class='title'>" + topic.name + "</span>";
        new_elmt.appendChild(link_it(topic.url));
        new_elmt.appendChild(get_copy_button(topic.url));
        main_div.appendChild(new_elmt);
    }
};

function load_requests(reqs){
    console.log("Chargement des requêtes lancées");
    var main_div = document.getElementById("requests");
    var new_elmt, link, copy;
    for(let req of reqs){
        new_elmt = get_linked_line(req.url, "Lien JVC", true, "t_link");
        main_div.appendChild(new_elmt);
    }
};

function get_dl_carac(dl){
    var p = dl.max_page > 1 ? " pages ~ " : " page ~ ";
    var o = dl.nbr_dl > 1 ? " objets téléchargés" : " objet téléchargé";
    var carac = "Auteur : "+dl.author+" ~ "+dl.max_page+ p +dl.nbr_dl+ o;
    return div_it("dl_carac", "", carac);
}

function load_dl(dls){
    console.log("Chargement des anciens téléchargements");
    var main_div = document.getElementById("old_dl");
    var new_elmt, t_link, copy, t_title;
    for(let dl of dls){
        new_elmt = div_it("dl", "background-color:#d6f2ff");
        t_title = document.createElement("h3");
        console.log(dl.topic_title);
        t_title.innerHTML = dl.topic_title;
        t_carac = get_dl_carac(dl);
        t_link = get_linked_line(dl.topic_url, "Lien JVC", true, "t_link");
        zip_link = get_linked_line(dl.url, "Lien de DL", true, "zip_link");
        
        app_children(new_elmt, [t_title, t_carac, t_link, zip_link]);
        main_div.appendChild(new_elmt);
    }
    
};

function load_history(){
    function onGot(storage){
        var historic = storage.historic;
        load_topics(historic.found_topic);
        load_requests(historic.requests);
        load_dl(historic.old_dl);
    }
    browser.storage.local.get("historic").then(onGot, onError);
}


document.addEventListener("DOMContentLoaded", load_history);
document.getElementById('to_refresh').style.display = 'none';
document.getElementById('to_refresh').style.display = 'block';

