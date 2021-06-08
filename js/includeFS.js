$(document).ready(function () { // Call function when DOM is ready
    $("div[data-includeHTML-FS]").each(function () {     
        console.log("LOADING...");
        //console.log($(this).attr("data-includeHTML-FS") + "?" + "name=" + $(this).attr("data-FS-name"));
        window.clcName=$(this).attr("data-FS-name");
        window.clcAboutText=$(this).attr("data-FS-aboutText");
        window.clcHelpText=$(this).attr("data-FS-helpText");
        window.clcImgPath=$(this).attr("data-FS-imgRelPath");
        window.clcApplyText=$(this).attr("data-FS-applyText");
        window.clcURL=$(this).attr("data-FS-URL");
        
        window.clcEmail=$(this).attr("data-FS-email");
        window.clcPhoneLink=$(this).attr("data-FS-phone-link");
        window.clcPhoneDisp=$(this).attr("data-FS-phone-disp");
        window.clcPhoneLink2=$(this).attr("data-FS-phone-link2");
        window.clcPhoneDisp2=$(this).attr("data-FS-phone-disp2");
        
        window.clcAddress=$(this).attr("data-FS-address");
        window.clcFB=$(this).attr("data-FS-FB");
        console.log(window.clcPhoneDisp2);
        $(this).load($(this).attr("data-includeHTML-FS"));
    });
});