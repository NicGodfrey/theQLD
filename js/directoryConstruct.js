/// CONSTRUCTOR
function entry(name, imgPath, about, url, email, phone, addressLink, addressDisp, fsURL, categories, aboutFS, howHelpFS, applyText, fb, linkedin, twitter, insta){ // TODO
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
    this.fb = fb;
    this.linkedin = linkedin;
    this.twitter = twitter;
    this.insta = insta;
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

/*function populateDir(){
    console.log(categories.length)
    for (i = 0; i < categories.length; i++) {
        console.log(categories[0])
    }
}*/

function populateFS(entry){
    console.log("Populating FS: ");
    console.log(entry)
    phoneText="";

    // PHONE
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

    //SOCIAL MEDIA
    var socialMedia = "";
    if (entry.fb != ""){
        socialMedia += `data-FS-FB='<a href="` + entry.fb + `" target="_blank"><i class="fa fa-facebook-square"></i></a>'`
    }
    if (entry.linkedin != ""){
        socialMedia += `data-FS-LinkedIn='<a href="` + entry.linkedin + `" target="_blank"><i class="fa fa-linkedin-square"></i></a>'`
    }

    generatedHTML=`
    <div data-includeHTML-FS="FSTemplate.html" data-FS-name="` + entry.name + `" data-FS-imgRelPath="`+entry.imgPath+`" 
    data-FS-aboutText="`+entry.aboutFS+`"
    data-FS-helpText="`+entry.howHelpFS+`"
    data-FS-applyText="`+entry.applyText+`"
    data-FS-URL="`+entry.url+`" data-FS-email="`+entry.email+`"
    ` + phoneText + `
    data-FS-address="` + entry.addressDisp + `"
    data-FS-addressLink="` + entry.addressLink + `"
    ` + socialMedia + `

    ></div>`

    return generatedHTML;
}

///

/// ENTRIES
var dict = new Object();
var categories = ["CRIME", "DISCRIMINATION", "TENANCY "]
//function entry(name, imgPath, about, url, email, phone, addressLink, addressDisp, fsURL, categories, aboutFS, howHelpFS, applyText, fb, linkedin, twitter, insta){ // TODO

    // ATSIWLSNQ
    let ATSIWLSNQ = new entry(
        "Aboriginal and Torress Strait Islander Women's Legal Service North Queensland", 'ATSIWLSNQ.png',
    "The Aboriginal and Torres Strait Islander Women’s Legal Service NQ is a service which exists to provide legal services and promote law reform for First Nations women in North Queensland. They provide support in relation to the following matters: child protection, family law, domestic violence, separation, child support, victims assist and discrimination law. In addition to providing legal services, they also run community legal education workshops for Aboriginal and Torres Strait Islander women in Townsville and to remote areas of North Queensland.",
    "http://www.atsiwlsnq.org.au",
    "admin@atsiwlsnq.org.au",
    [["1800 082 600", "(07) 4721 6007"],["Phone",""]],
    "https://www.google.com/maps/place/Aboriginal+and+Torres+Strait+Islander+Women's+Legal+Services+NQ+Inc./@-19.2582827,146.8081721,15z/data=!3m1!4b1!4m5!3m4!1s0x6bd5f8db33e6cf57:0x24526a120a707ba9!8m2!3d-19.258214!4d146.8168359", 
    "Level 3, 42 Sturt St, Townsville, Queensland 4810",
    "ATSIWLSNQ",
    ['INDIGENOUS','DISCRIMINATION', 'FAMILY'],
    `
    The Aboriginal and Torres Strait Islander Women’s Legal Service NQ (ATSIWLSNQ) is a service which exists to provide legal services and promote law reform for First Nations women in North Queensland.
        <br><br>
        Originally founded as part of the North Queensland Women’s Legal Service, ATSIWLSNQ has operated independently since 2006. The service is funded by the Commonwealth Attorney General’s Department and the State Attorney General’s Department through the Legal Aid Queensland’s Community Legal Service Program. 
        <br><br>
        In addition to providing legal services, they also run community legal education workshops for Aboriginal and Torres Strait Islander women in Townsville and to remote areas of North Queensland.    `,
    `
    ATSIWLSNQ can provide assistance to Aboriginal and Torres Strait women and their families from clinics throughout North Queensland. They provide support in relation to the following matters: child protection, family law, domestic violence, separation, child support, victims assist and discrimination law.
    <br><br>
    ATSIWLSNQ provide a broad range of legal services to their clients. They may be able to provide you with preliminary legal advice, ongoing legal casework and even court representation. 
    `,
    `Free call ATSIWLSNQ by calling 1800 082 600 between 09:00-17:00, Mondays to Friday.
    `,
    "https://www.facebook.com/ATSIWLSNQ/",
    "",
    );
    dict["ATSIWLSNQ"] = ATSIWLSNQ;

    // Bayside
    let Bayside = new entry(
        'Bayside Community Legal Service', 'bcls.png',
    "Basic Rights Queensland provides legal advice and advocacy with regards to Centrelink assistance, disability discrimination and women’s workplace issues. Their team includes lawyers, social workers and volunteers, who work to provide community legal education, advocate for law reform and provide specialist services to other community organisations.",
    "https://bcls.org.au/",
    "enquiries@bcls.org.au",
    "(07) 3162 3282",
    "https://www.google.com/maps/place/Bayside+Community+Legal+Service+Inc./@-27.4460855,153.1611739,14.31z/data=!4m5!3m4!1s0x6b915d8d7a1d980b:0x131d3b4d4eb032b4!8m2!3d-27.444219!4d153.1723517", // AddressLink
    "Wynnum Community Centre, 1st Floor, 105 Florence St, Wynnum, Queensland 4178", // AddressDisp
    "BRQ",
    ['DISCRIMINATION','WELFARE'],
    `Bayside Community Legal Service (BCLS) is a legal service founded in 1992 which provides legal support to the Bayside community. Their services include providing legal advice and representation, mediation, legal information, referrals and community legal education.
    <br><br>
    BCLS is heavily reliant on their volunteers made up of students, lawyers and mediators. Bayside Community Legal Service could not provide legal assistance to the Bayside community without the hardwork and dedication of their volunteers.
    <br><br>
    BCLS receives some funding through through Legal Aid Queensland, but also accepts individual tax-deductible donations.`,
    `Bayside Community Legal Centre offers one-off, 30 minute advice appointments. These can be held by phone or in-person.
    <br><br>
    BCLS can only provide assistance within their practice areas. These include debt issues, property damage from a motor vehicle accident, neighbourhood disputes, tenancy, consumer complaints and bailment. They can also advise you on family law issues regarding domestic violence, divorce/separation and parenting. Within criminal law, they can provide advice in relation to criminal offences, traffic offences and breaches of domestic violence orders. 
    `,
    `To organise a consultation, call (07) 3162 3282, request a call back on BCLS' website or email enquiries@bcls.org.au.`,
    "https://www.facebook.com/BCLS.WYNNUM/",
    ""
    );
    dict["Bayside"] = Bayside;

    // BRQ
    let BRQ = new entry(
        'Basic Rights Queensland', 'BRQ.png',
    "Basic Rights Queensland provides legal advice and advocacy with regards to Centrelink assistance, disability discrimination and women’s workplace issues. Their team includes lawyers, social workers and volunteers, who work to provide community legal education, advocate for law reform and provide specialist services to other community organisations.",
    "http://www.brq.org.au",
    "brq@brq.org.au",
    [["(07) 3847 5532", "1800 358 511", "1800 621 458"],["Free Call (Social Security / Disability Discrimination)", "", "Free Call (Women's Employment)"]],
    "", // AddressLink
    "", // AddressDisp
    "BRQ",
    ['DISCRIMINATION','WELFARE'],
    `Basic Rights Queensland (BRQ) is a service which provides legal advice and advocacy in the areas of of Centrelink assistance, disability discrimination and women’s workplace issued. The service was originally founded over thirty years ago as the ‘Welfare Rights Centre’. Since then, it has grown and in 2018 merged with Working Women Queensland.
    <br><br>
    Their team includes lawyers, social workers and volunteers, who work to provide community legal education, advocate for law reform and provide specialist services to other community organisations.
    <br><br>
    This service is funded by both State and Federal governments through the <a href='https://www.ag.gov.au/legal-system/legal-assistance-services/community-legal-services-program' target='_blank'>Community Legal Services Program.</a>`,
    `Basic Rights Queensland can provide assistance if you are having Centrelink issues, facing disability discrimination or are a woman facing issues at the workplace. However, the service is only able to provide support for those who are very vulnerable and unable to advocate for themselves. 
    <br><br>
    BRQ may also be unable to provide support where they deem a case does not have merit or when facing issues with capacity.`,
    `Contact Basic Rights Queensland by calling (07) 3847 5532 or 1800 358 511 between 09:00-16:30 Mondays to Thursdays, or 09:00-12:30 Fridays, for <b>social security</b> or <b>disability discrimination</b> matters. For <b>women's employment</b> advice, free call 1800 621 458 between 09:00-13:00 Mondays or Tuesdays, or 09:00-16:00 on Fridays.`,
    "https://www.facebook.com/wwqld/",
    "https://www.linkedin.com/company/basic-rights-queensland/about/"
    );
    dict["BRQ"] = BRQ;

    // BNCLS
    let BNCLS = new entry(
        'Brisbane North Community Legal Service', 'NorthsideConnect.png',
    "Brisbane North Community Legal Service (BNCLS) is a generalist community legal service which provides free legal advice, information, and referral to individuals on a range of legal issues including family law, domestic violence, civil disputes, criminal matters, neighbourhood issues, elder law and employment.",
    "https://northsideconnect.org.au/legal-service/",
    "admin@northsideconnect.org.au",
    "(07) 3260 6820",
    "https://www.google.com/maps/place/Northside+Connect/@-27.4013307,153.051648,15z/data=!3m1!4b1!4m5!3m4!1s0x6b915861ecd5f391:0x16401a8027fcdbf1!8m2!3d-27.4013621!4d153.0603798", 
    "14 Station St, Nundah, Queensland 4012",
    "brisbane_north",
    ['FAMILY','TENANCY', 'CRIME', 'EMPLOYMENT'],
    `
    Brisbane North Community Legal Service (BNCLS) is a generalist community legal service which provides free legal advice, information and referral to individuals on a range of legal issues.
    <br><br>
    A service of <a href='https://northsideconnect.org.au/' target='_blank'>Northside Connect</a>, volunteer legal practitioners and volunteer students which work at the BNCLS can also provide information on and referral to other services such as counselling and support.
    `,
    `
    Based in Nundah and open to north side residents, BNCLS service provides free legal assistance on a range of legal issues including family law, domestic violence, civil disputes, criminal matters, neighbourhood issues, elder law and employment, as well as referrals to other qualified solicitors. Northside Connect also has a dedicated Domestic Violence and Family Support Program, which provides legal services and counselling to families.       
        <br><br>
        Appointments are available, in addition to drop-in legal advice by consultation. 
    `,
    `To see if BNCLS can help with your matter, call (07) 3260 6820 between 9:00-16:00 Monday to Thursday.
    `,
    "https://www.facebook.com/Northside-Connect-658994620794556/",
    "",
    );
    dict["BNCLS"] = BNCLS;

    // Care Goondiwindi Legal Service
    let careGoondiwindi = new entry(
        'Care Goondiwindi Legal Service', 'careGoondiwindi2.png',
    "Care Goondiwindi Community provides a range of community services to residents of Goondiwindi, including legal information and referrals to other organisations that may be able to assist with legal matters. They do not, however, provide ongoing support or court representation.",
    "http://www.caregoondiwindi.org.au",
    "info@caregoondiwindi.org.au",
    "(07) 4670 0700",
    "https://www.google.com/maps/place/Care+Goondiwindi/@-28.5463105,150.3112495,17z/data=!3m1!4b1!4m5!3m4!1s0x6ba3169e3ab9d81f:0xc0ab38373c6b96a2!8m2!3d-28.5463105!4d150.3134382", 
    "111 Callandoon Street, Goondiwindi, Queensland 4390",
    "care_goondiwindi",
    ['TENANCY', 'WELFARE'],
    `
    Care Goondiwindi provides a range of community services to the people of Goondiwindi, which includes the Care Goondiwindi Community Legal Services (CGCLS), founded in 2006. This service is committed to providing advice and support to vulnerable, disadvantaged and disabled members of the community.
    <br><br>
    CGCLS are also committed to informing and empowering the community through legal education and can provide clients with support in using government issued self-help kits.    `,
    `
    CGCLS provides legal information and referrals to other organisations that may be able to assist you with your matter. However, they do not provide ongoing support or court representation.
    <br><br>
    Appointments are held on Mondays and Thursdays between 9:45am and 2:45pm at the Care Goondiwindi office or over the phone, and are by booking only. CGCLS also have a Stanthorpe Office which provides phone appointments only. 
    `,
    `To get in touch with CGCLS, call (07) 4670 0700 between 09:45-14:45 Mondays or Thursdays, or email info@caregoondiwindi.org.au.
    `,
    "https://www.facebook.com/gundycare/",
    "",
    );
    dict["careGoondiwindi"] = careGoondiwindi;

    // Hub Community Legal
    let HubCL = new entry(
        'Hub Community Legal', 'HubCL.svg',
    "Hub Community Legal offers advice, assistance, and in some circumstances, ongoing casework and court representation across south west Brisbane. They operate in a variety of legal areas, including family, property, traffic, youth, crime & employment, though they cannot assist with personal injury, commercial, or conveyancing matters.",
    "https://hubcommunity.org.au",
    "legal@hubcommunity.org.au",
    "(07) 3372 7677",
    "https://www.google.com/maps/place/HUB+Community+Legal+(formerly+South+West+Brisbane+Community+Legal+Centre)/@-34.1862962,141.0480228,5z/data=!4m9!1m2!2m1!1sgoogle+maps+hub+community+legal!3m5!1s0x6b914f1932fadb43:0xfb06e2c5c0538aaf!8m2!3d-27.5976697!4d152.9658072!15sCh9nb29nbGUgbWFwcyBodWIgY29tbXVuaXR5IGxlZ2FsIgOIAQGSARBjb21tdW5pdHlfY2VudGVy", 
    "79 Poinsettia St, Inala, Queensland 4077",
    "Hub_CL",
    ['WILLS', 'FAMILY', 'YOUTH', 'CRIME', 'EMPLOYMENT'],
    `
    Initially started in 1986 as the Community of Inala Legal Service, Hub Community Legal (HCL) offers legal advice and assistance throughout Brisbane's south west suburbs.
    <br><br>
    The Community of Inala Legal Service has also been known as the South West Brisbane Community Legal Centre, and merged with the Hub Neighbourhood Centre in 2019. They accept both State and Federal funding.
    `,
    `
    HCL offers free legal advice appointments during the day and evening at their Inala offices, as well as with partner organisations. In addition, limited advice is offered by telephone with appointment. In some circusmtances, HCL is able to offer ongoing casework or representation in court.       
        <br><br>
        HCL operates in a variety of legal areas, including family, property, traffic, youth, crime & employment, though they cannot assist with personal injury, commercial, or conveyancing matters. 
        <br><br>
        HCL provide youth lawyers for children and teenagers, and have arrangements in place for assisting individuals with hearing or speech impediments, as well as individuals who have difficulty with English.
    `,
    `Contact Hub Community Legal on (07) 3372 7677. Individuals who have difficluty with English can call the <a href='https://www.tisnational.gov.au/Help-using-TIS-National-services/Contact-TIS-National' target='_blank'>Translating and Interpreting Service</a> on 131 450 for assistance in making a booking. Individuals with a hearing or speech impediment can contact HCL through the <a href='https://relayservice.gov.au/' target='_blank'>National Relay Service</a>.
    `,
    "https://www.facebook.com/HUBcommunitylegal/",
    "https://www.linkedin.com/company/south-west-brisbane-community-legal-centre/about/",
    );
    dict["HubCL"] = HubCL;


