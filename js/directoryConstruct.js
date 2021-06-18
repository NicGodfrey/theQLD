/// CONSTRUCTOR
function entry(name, imgPath, about, url, email, phone, addressLink, addressDisp, fsURL, categories, aboutFS, howHelpFS, applyText){ // TODO
    this.name = name;
    this.imgPath = imgPath;
    this.about = about;
    this.url = url;
    this.email = email;
    this.rawPhone = phone;
    if (Array.isArray(phone)) {
        this.phone = parsePhones(phone[0],phone[1]);
    } else {
        this.phone = parsePhones(phone);
    }
    this.addressLink = addressLink;
    this.addressDisp = addressDisp;
    this.fsURL = fsURL;
    this.categories = categories;
    this.aboutFS = aboutFS;
    this.howHelpFS = howHelpFS;
    this.applyText = applyText;
}
///

/// POPULATE FUNCTION
function populateHTML(entry) {
    console.log(entry)
    if (entry.addressDisp != "") {
        console.log("ADDRESS")
        address = `<b>Address: </b><a href='` + entry.addressLink + `' target='_blank'>` + entry.addressDisp + `</a><br></br>`;
    } else {
        console.log("NO ADDRESS")
        address = "";
    }
    generatedHTML = `
    <h3 class="directoryH3">` + entry.name + `</h3>
    <div class="row">
        <div class="directory-col-img">
            <img src="images/logos/` + entry.imgPath + `" >
        </div>
        <div class="directory-col-abt">
            <p>` + entry.about + `</p>
        </div>
        <div class="directory-col-lnks"> 
            <b>Website: </b><a href="` + entry.url + `" target="_blank">` + entry.url + `</a><br>
            <b>E-Mail: </b><a href="mailto:` + entry.email + `">` + entry.email + `</a><br>
            ` + entry.phone + `
            `+ address +`
            <a href="factSheets/`+ entry.fsURL +`.html" class="FS-btn"><i class="fa fa-file-text-o"></i>  Fact Sheet</a>
        </div>
    </div>
    `
    return generatedHTML;
}

function populateCatHTML(category){
    console.log("populateCatHTML")
    console.log(Object.keys(dict).length)
    var generatedHTML ="";
    for (i = 0; i < Object.keys(dict).length; i++) {
        entryObj = Object.values(dict)[i];
        if (entryObj.categories.includes(category)){
            console.log(Object.values(dict)[i])
            entryName = Object.keys(dict)[i];
            generatedHTML += populateHTML(entryObj);
            generatedHTML += "<br><br>"
        }
    }
    
    return generatedHTML;
}

function populateFS(entry){
    console.log("Populating FS: ");
    console.log(entry)
    phoneText="";

    if (Array.isArray(entry.rawPhone)){
        j=1;
        for (i = 0; i < entry.rawPhone[0].length; i++){
            console.log(entry.rawPhone[0][i]);
            if (typeof entry.rawPhone[1][i] != undefined) {
                if (entry.rawPhone[1][i] != "Phone") {
                    if (entry.rawPhone[1][i] != "") {
                        console.log(entry.rawPhone[1][i]);
                        phoneText += 'data-FS-phone-Head' + j + '="' + entry.rawPhone[1][i] + ': <br>"' // data-fs-phone-Head{j}
                        j++;
                        k = 1;
                    }
                }
            }
            console.log(j);
            if ( j <= 2 ) {
                console.log("ABC")
                phoneSuff=(i+1);
                console.log(i)
                if (i==0){
                    phoneSuff="";
                }
                console.log(phoneSuff)

            } else {
                phoneSuff="_" + (j-1) + "_" + k;
                k++;
                }
            phoneText += ` data-FS-phone-disp`+phoneSuff+`="`+entry.rawPhone[0][i]+`"`
            var phoneType;
            if (entry.rawPhone[0][i].substring(0, 3) == "(07") {
                phoneType = "07";
                console.log(phoneType);
            } else if (entry.rawPhone[0][i].substring(0, 4) == "1800") {
                phoneType = "1800";
            }
            phoneLink = phone_disp2link(entry.rawPhone[0][i], phoneType)
            phoneText += ` data-FS-phone-link`+phoneSuff+`="`+phoneLink+`"`;
            console.log(phoneText);
        }
    } else {
        phoneText = ` data-FS-phone-disp="`+entry.rawPhone+`"`
        var phoneType;
            if (entry.rawPhone.substring(0, 3) == "(07") {
                phoneType = "07";
                console.log(phoneType);
            } else if (entry.rawPhone.substring(0, 4) == "1800") {
                phoneType = "1800";
            }
        phoneLink = phone_disp2link(entry.rawPhone, phoneType)
        phoneText += ` data-FS-phone-link="`+phoneLink+`"`;
    }

    generatedHTML=`
    <div data-includeHTML-FS="FSTemplate.html" data-FS-name="` + entry.name + `" data-FS-imgRelPath="`+entry.imgPath+`" 
    data-FS-aboutText="`+entry.aboutFS+`"
    data-FS-helpText="`+entry.howHelpFS+`"
    data-FS-applyText="`+entry.applyText+`"
    data-FS-URL="`+entry.url+`" data-FS-email="`+entry.email+`"
    ` + phoneText + `
    data-FS-FB='<a href="https://www.facebook.com/wwqld/" target="_blank"><i class="fa fa-facebook-square"></i></a>'
    data-FS-LinkedIn= '<a href="https://www.linkedin.com/company/basic-rights-queensland/about/" target="_blank"><i class="fa fa-linkedin-square"></i></a>'

    ></div>`

    return generatedHTML;
}

///

/// ENTRIES
var dict = new Object();
var categories = ["CRIME", "DISCRIMINATION", "TENANCY "]
// function entry(name, imgPath, about, url, email, phone, phoneExtra, addressLink, addressDisp, fsURL, categories, aboutFS, howHelpFS){ // TODO

    // BRQ
    var BRQPhone = parsePhones(["(07) 3847 5532", "1800 358 511", "1800 621 458"],["Free Call (Social Security / Disability Discrimination)", "", "Free Call (Women's Employment)"])
    let BRQ = new entry(
        'Basic Rights Queensland', 'BRQ.png',
    "Basic Rights Queensland provides legal advice and advocacy with regards to Centrelink assistance, disability discrimination and women’s workplace issues. Their team includes lawyers, social workers and volunteers, who work to provide community legal education, advocate for law reform and provide specialist services to other community organisations.",
    "http://www.brq.org.au",
    "brq@brq.org.au",
    [["(07) 3847 5532", "1800 358 511", "1800 621 458"],["Free Call (Social Security / Disability Discrimination)", "", "Free Call (Women's Employment)"]],
    "", // AddressLink
    "", // AddressDisp
    "BRQ",
    ['DISCRIMINATION','TENANCY', 'CRIME'],
    `Basic Rights Queensland (BRQ) is a service which provides legal advice and advocacy in the areas of of Centrelink assistance, disability discrimination and women’s workplace issued. The service was originally founded over thirty years ago as the ‘Welfare Rights Centre’. Since then, it has grown and in 2018 merged with Working Women Queensland.
    <br><br>
    Their team includes lawyers, social workers and volunteers, who work to provide community legal education, advocate for law reform and provide specialist services to other community organisations.
    <br><br>
    This service is funded by both State and Federal governments through the <a href='https://www.ag.gov.au/legal-system/legal-assistance-services/community-legal-services-program' target='_blank'>Community Legal Services Program.</a>`,
    `Basic Rights Queensland can provide assistance if you are having Centrelink issues, facing disability discrimination or are a woman facing issues at the workplace. However, the service is only able to provide support for those who are very vulnerable and unable to advocate for themselves. 
    <br><br>
    BRQ may also be unable to provide support where they deem a case does not have merit or when facing issues with capacity.`,
    `Contact Basic Rights Queensland by calling (07) 3847 5532 or 1800 358 511 between 09:00-16:30 Mondays to Thursdays, or 09:00-12:30 Fridays, for <b>social security</b> or <b>disability discrimination</b> matters. For <b>women's employment</b> advice, free call 1800 621 458 between 09:00-13:00 Mondays or Tuesdays, or 09:00-16:00 on Fridays.`
    );
    dict["BRQ"] = BRQ;

    // BNCLS
    var BNCLSPhone = parsePhones("(07) 3260 6820")
    let BNCLS = new entry(
        'Brisbane North Community Legal Service', 'NorthsideConnect.png',
    "Brisbane North Community Legal Service (BNCLS) is a generalist community legal service which provides free legal advice, information, and referral to individuals on a range of legal issues including family law, domestic violence, civil disputes, criminal matters, neighbourhood issues, elder law and employment.",
    "https://northsideconnect.org.au/legal-service/",
    "admin@northsideconnect.org.au",
    "(07) 3260 6820",
    "https://www.google.com/maps/place/Northside+Connect/@-27.4013307,153.051648,15z/data=!3m1!4b1!4m5!3m4!1s0x6b915861ecd5f391:0x16401a8027fcdbf1!8m2!3d-27.4013621!4d153.0603798", 
    "14 Station St, Nundah, Queensland 4012</a><br>",
    "brisbane_north",
    ['DISCRIMINATION','TENANCY', 'CRIME'],
    );
    dict["BNCLS"] = BNCLS;

