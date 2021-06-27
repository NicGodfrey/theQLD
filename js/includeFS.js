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
        window.clcPhoneLink_2_1=$(this).attr("data-FS-phone-link_2_1");
        window.clcPhoneDisp_2_1=$(this).attr("data-FS-phone-disp_2_1");
        window.clcPhoneHead1=$(this).attr("data-FS-phone-Head1");
        window.clcPhoneHead2=$(this).attr("data-FS-phone-Head2");
        
        
        window.clcAddress=$(this).attr("data-FS-address");
        window.clcAddressLink=$(this).attr("data-FS-addressLink");
        window.clcFB=$(this).attr("data-FS-FB");
        window.clcLinkedIn=$(this).attr("data-FS-LinkedIn");
        window.clcTwitter=$(this).attr("data-FS-Twitter")
        window.clcInsta=$(this).attr("data-FS-Insta")
        console.log("ABC:")
        console.log($(this))
        console.log(window.clcPhoneLink)
        $(this).load($(this).attr("data-includeHTML-FS"));
    });
});