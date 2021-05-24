$(document).ready(function () { // Call function when DOM is ready
    $("div[data-includeHTML]").each(function () {                
        $(this).load($(this).attr("data-includeHTML"));
    });
    $("div[data-includeHTML-FS]").each(function () {     
        console.log($(this).attr("data-includeHTML-FS") + "?" + "name=" + $(this).attr("data-FS-name"))
        window.name="Bob";           
        $(this).load($(this).attr("data-includeHTML-FS") + "?" + "name=" + $(this).attr("data-FS-name"));
    });
});