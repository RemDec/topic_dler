console.log("Script historique");
onError = browser.extension.getBackgroundPage().onError;

function div_it(div_class){
    var div = document.createElement("div");
    div.className = div_class;
    return div;
}

function link_it(link, short_it=true){
    var a = document.createElement("a");
    a.href = link;
    a.target = "_blank";
    /*
    if (short_it && link.length > 70)
        link = link.substring(0, 5) + "[..]" + link.substring(55);
    if (link.length > 40)
        link = "Lien JVC";*/
    a.innerHTML = "Lien JVC";
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

function load_topics(topics){
    console.log("Chargement des topics visités");
    var main_div = document.getElementById("found_topic");
    var new_elmt, link, copy;
    for(let topic of topics){
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
        new_elmt = div_it("request");
        new_elmt.innerHTML = "<span class='url'>" + req.url + "</span>";
        new_elmt.appendChild(link_it(req.url));
        new_elmt.appendChild(get_copy_button(req.url));
        main_div.appendChild(new_elmt);
    }
};

function load_dl(dls){
    console.log("Chargement des anciens téléchargements");
    var main_div = document.getElementById("old_dl");
    var new_elmt, link, copy;
    for(let dl of dls){
        new_elmt = div_it("dl");
        new_elmt.innerHTML = "<span class='zip_url'>" + dl.url + "</span>";
        new_elmt.appendChild(link_it(dl.url));
        new_elmt.appendChild(get_copy_button(dl.url));
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