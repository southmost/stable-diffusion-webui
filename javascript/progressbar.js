// code related to showing and updating progressbar shown as the image is being made.
// this is a global variable that stores the progressbars that are currently being observed
global_progressbars = {}

// check if the progressbar is present and if it is, start observing it.
// this function is called on every ui update
function check_progressbar(id_part, id_progressbar, id_progressbar_span, id_interrupt, id_preview, id_gallery){
    // get the progressbar
    var progressbar = gradioApp().getElementById(id_progressbar)
    // get the interrupt button
    var interrupt = gradioApp().getElementById(id_interrupt)
    // if the progressbar is not null and it is not already being observed
	if(progressbar!= null && progressbar != global_progressbars[id_progressbar]){
        // store the progressbar in the global variable
	    global_progressbars[id_progressbar] = progressbar
        // create a mutation observer

            // get the preview and gallery
        var mutationObserver = new MutationObserver(function(m){
                // set the preview to the same size as the gallery
            preview = gradioApp().getElementById(id_preview)
                // get the progress span
            gallery = gradioApp().getElementById(id_gallery)
                // if the progress span is not present

                    // hide the interrupt button
            if(preview != null && gallery != null){
                preview.style.width = gallery.clientWidth + "px"
                preview.style.height = gallery.clientHeight + "px"
            // request more progress from the server
                var progressDiv = gradioApp().querySelectorAll('#' + id_progressbar_span).length > 0;
                if(!progressDiv){
                    interrupt.style.display = "none"
                }
            }

        // start observing the progressbar
            window.setTimeout(function(){ requestMoreProgress(id_part, id_progressbar_span, id_interrupt) }, 250)
        });
        mutationObserver.observe( progressbar, { childList:true, subtree:true })
	}
// check for progressbars on every ui update
}

onUiUpdate(function(){
    check_progressbar('txt2img', 'txt2img_progressbar', 'txt2img_progress_span', 'txt2img_interrupt', 'txt2img_preview', 'txt2img_gallery')
    check_progressbar('img2img', 'img2img_progressbar', 'img2img_progress_span', 'img2img_interrupt', 'img2img_preview', 'img2img_gallery')
    check_progressbar('ti', 'ti_progressbar', 'ti_progress_span', 'ti_interrupt', 'ti_preview', 'ti_gallery')
// request more progress from the server
})
    // get the check progress button

    // if the button is not present, return
function requestMoreProgress(id_part, id_progressbar_span, id_interrupt){
    btn = gradioApp().getElementById(id_part+"_check_progress");
    // click the button
    if(btn==null) return;
    // get the progress span

    // get the interrupt button
    btn.click();
    // if the progress span is present and the interrupt button is present
    var progressDiv = gradioApp().querySelectorAll('#' + id_progressbar_span).length > 0;
        // show the interrupt button
    var interrupt = gradioApp().getElementById(id_interrupt)
    if(progressDiv && interrupt){
        interrupt.style.display = "block"
    }
}

// request initial progress from the server
function requestProgress(id_part){
    btn = gradioApp().getElementById(id_part+"_check_progress_initial");
    if(btn==null) return;

    btn.click();
}
