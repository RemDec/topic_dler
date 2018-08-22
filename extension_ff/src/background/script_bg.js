console.log("script background |");
//Set local default settings if undefined

function isEmpty(obj) {
    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            return false;
    }
    return true;
};

function set_default(){
    function onError(error){console.log('Error: ${error}')};
        
    function onGot(basic_options){
        console.log(basic_options);
        if(!basic_options || isEmpty(basic_options)){
            basic_options = {
                img_ok: 1, webm_ok: 1, voca_ok: 0,
                posts_ok: 0, risi_ok: 0,
                menu_kheys:1
            }
            browser.storage.local.set({basic_options})
                .then(function(){console.log('Ecriture param défauts')}, onError);
        }
    };
    
    let getting_basics = browser.storage.local.get("basic_options");
    getting_basics.then(onGot, onError);
};




document.addEventListener("DOMContentLoaded", set_default);