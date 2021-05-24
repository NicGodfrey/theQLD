$(document).ready(function () { // Call function when DOM is ready
    $("div[data-includeHTML]").each(function () {                
        $(this).load($(this).attr("data-includeHTML"));
    });
    $("div[data-includeHTML-FS]").each(function () {     
        console.log("LOADING");
        //console.log($(this).attr("data-includeHTML-FS") + "?" + "name=" + $(this).attr("data-FS-name"));
        window.clcName=$(this).attr("data-FS-name");
        window.clcAboutText=$(this).attr("data-FS-aboutText");
        window.clcHelpText=$(this).attr("data-FS-helpText");
        window.clcImgPath=$(this).attr("data-FS-imgRelPath");
        console.log(window.clcAboutText);
        $(this).load($(this).attr("data-includeHTML-FS"));
    });
});