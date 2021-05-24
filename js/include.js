$(document).ready(function () { // Call function when DOM is ready
    $("div[data-includeHTML]").each(function () {                
        $(this).load($(this).attr("data-includeHTML"));
        console.log($(this).attr("data-includeHTML"));
    });

});