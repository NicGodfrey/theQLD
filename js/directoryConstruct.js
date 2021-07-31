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

var categoriesDict = {"CRIME": "Crime", 
"DEBT":"Debt", 
"DISCRIMINATION": "Discrimination",
"EMPLOYMENT": "Employment",
"FAMILY": "Family & DV",
"IMMIGRATION": "Immigration",
"INDIGENOUS": "Indigenous",
"LGBTIQ": "LGBTIQ",
"TENANCY": "Tenancy",
"WELFARE": "Welfare",
"WILLS": "Wills & Estates",
"YOUTH": "Youth"}


/// GENERATE OTHER LEGAL AREAS
function legalAreas(categories, current){
    //console.log(categoriesDict)
    var generatedHTML = "";
    for (x = 0; x < Object.keys(categories).length; x++){
        iterCat = Object.values(categories)[x];
        console.log(x)
        console.log(iterCat)
        if (iterCat != current){
            lowerCase = iterCat.toLowerCase()
            capitalised = iterCat.charAt(0).toUpperCase() + lowerCase.slice(1)
            friendlyText = categoriesDict[iterCat];
            generatedHTML += "<a href='#" + capitalised + "'>" + friendlyText + "</a> | "
        }
    }
    returnedHTML = generatedHTML.substring(0, generatedHTML.length - 2);
    //console.log("Returning " + returnedHTML)
    return returnedHTML;
}


/// POPULATE FUNCTION
function populateHTML(entry, otherCats) {
    console.log(entry)
    console.log(otherCats)
    
    if (entry.addressDisp != "") {
        //console.log("ADDRESS")
        address = `<b>Address: </b><a href='` + entry.addressLink + `' target='_blank'>` + entry.addressDisp + `</a><br></br>`;
    } else {
        //console.log("NO ADDRESS")
        address = "";
    }

    if (entry.url != "NONE") {
        urlLine = `<b>Website: </b><a href="` + entry.url + `" target="_blank">` + entry.url + `</a><br>`;
    } else {
        urlLine = "";
    }

    generatedHTML = `
    <h3 class="directoryH3">` + entry.name + `</h3>
    <div class="row">
        <div class="directory-col-img">
            <img src="images/logos/` + entry.imgPath + `" >
        </div>
        <div class="directory-col-abt">
            <p>` + entry.about + `</p>
            <div class="otherAreas">
            <p><b>Other Areas:</b> ` + otherCats + `</p>
            </div>
        </div>
        <div class="directory-col-lnks"> 
            ` + urlLine + `
            <b>E-Mail: </b><a href="mailto:` + entry.email + `">` + entry.email + `</a><br>
            ` + entry.phone + `
            `+ address +`
            <a href="factSheets/`+ entry.fsURL +`.html" class="FS-btn"><i class="fa fa-file-text-o"></i>  Fact Sheet</a>
        </div>
    </div>
    `
    console.log(generatedHTML)
    return generatedHTML;
}

function populateCatHTML(category){
    //console.log("populateCatHTML")
    //console.log(Object.keys(dict).length)
    var generatedHTML ="";
    for (i = 0; i < Object.keys(dict).length; i++) {
        entryObj = Object.values(dict)[i];
        if (entryObj.categories.includes(category)){
            console.log(Object.values(dict)[i])
            entryName = Object.keys(dict)[i];
            //console.log(entryObj.categories)
            otherCats = legalAreas(entryObj.categories, category);
            console.log("XYZ")
            //otherCats = "ABC"
            generatedHTML += populateHTML(entryObj, otherCats);
            generatedHTML += "<br><br>"
        }
    }

    console.log("DONE")
    
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
    if (entry.twitter != ""){
        socialMedia += `data-FS-Twitter='<a href="` + entry.twitter + `" target="_blank"><i class="fa fa-twitter-square"></i></a>'`
    }
    if (entry.insta != ""){
        socialMedia += `data-FS-Insta='<a href="` + entry.insta + `" target="_blank"><i class="fa fa-instagram"></i></a>'`
    }

    // URL
    if (entry.url != "NONE"){
        urlLine = entry.url;
    } else {
        urlLine = "NONE";
    }

    generatedHTML=`
    <div data-includeHTML-FS="FSTemplate.html" data-FS-name="` + entry.name + `" data-FS-imgRelPath="`+entry.imgPath+`" 
    data-FS-aboutText="`+entry.aboutFS+`"
    data-FS-helpText="`+entry.howHelpFS+`"
    data-FS-applyText="`+entry.applyText+`"
    data-FS-URL="`+urlLine+`" data-FS-email="`+entry.email+`"
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
    "",
    ""
    );
    dict["ATSIWLSNQ"] = ATSIWLSNQ;

    // ATSILS
    let ATSILS = new entry(
        "Aboriginal and Torress Strait Islander Legal Service (Qld)", 'atsils.png',
    "The Aboriginal and Torres Strait Islander Legal Service provides professional and culturally proficient legal services for Aboriginal and Torres Strait Islander people across Queensland. This includes legal advice and representation relating to criminal, civil and family law.",
    "https://www.atsils.org.au/",
    "info@atsils.org.au",
    [["1800 012 255", "(07) 3025 3888"],["Phone",""]],
    "https://www.atsils.org.au/contact/", 
    "Multiple Locations",
    "ATSILS",
    ['INDIGENOUS','CRIME', 'FAMILY'],
    `
    The Aboriginal and Torres Strait Islander Legal Service (Qld) ('ATSILS') provides professional and culturally proficient legal services for Aboriginal and Torres Strait Islander people across Queensland.
    <br><br>
    Funded by the Commonwealth Attorney Generals' Department and the Department of Prime Minister and Cabinet, ATSILS provides legal advice, as well as law reform efforts, legal education, coronial and public sector monitoring, and support for former offenders in transitioning back into the community through their <a href='https://www.atsils.org.au/prisoner-throughcare/' target='_blank'>Throughcare Program</a>.
    `,
    `
    ATSILS provides legal advice and representation relating to criminal, civil and family law. Specifically, ATSILS' services include advice, duty matters and casework matters, though means testing is applied to the latter. 
    <br><br>
    Finally, ATSILS provides 24 hour legal representation and advice specifically on criminal matters for Aboriginal and Torres Strait Islander people at police stations.
    `,
    `
    Contact ATSILS' toll-free number at 1800 012 255, or find your closest ATSILS office <a href='https://www.atsils.org.au/contact/' target='_blank'>here</a>.
    `,
    "https://www.facebook.com/atsils/",
    "https://www.linkedin.com/company/atsils?originalSubdomain=au",
    "https://twitter.com/atsils?lang=en",
    "https://www.instagram.com/atsilsq/?hl=en"
    );
    dict["ATSILS"] = ATSILS;

    // Bayside
    let Bayside = new entry(
        'Bayside Community Legal Service', 'bcls.png',
    "Bayside Community Legal Service provides legal support to the Bayside community, including providing legal advice and representation, mediation, legal information, referrals and community legal education.",
    "https://bcls.org.au/",
    "enquiries@bcls.org.au",
    "(07) 3162 3282",
    "https://www.google.com/maps/place/Bayside+Community+Legal+Service+Inc./@-27.4460855,153.1611739,14.31z/data=!4m5!3m4!1s0x6b915d8d7a1d980b:0x131d3b4d4eb032b4!8m2!3d-27.444219!4d153.1723517", // AddressLink
    "Wynnum Community Centre, 1st Floor, 105 Florence St, Wynnum, Queensland 4178", // AddressDisp
    "bayside_community_legal_service",
    ['DISCRIMINATION','WELFARE', 'FAMILY', 'DEBT', 'TENANCY', 'CRIME'],
    `Bayside Community Legal Service (BCLS) is a legal service founded in 1992 which provides legal support to the Bayside community. Their services include providing legal advice and representation, mediation, legal information, referrals and community legal education.
    <br><br>
    BCLS is heavily reliant on their volunteers made up of students, lawyers and mediators. Bayside Community Legal Service could not provide legal assistance to the Bayside community without the hardwork and dedication of their volunteers.
    <br><br>
    BCLS receives some funding through through Legal Aid Queensland, but also accepts individual tax-deductible donations.`,
    `Bayside Community Legal Centre offers one-off, 30 minute advice appointments. These can be held by phone or in-person.
    <br><br>
    BCLS can only provide assistance within their practice areas. These include debt issues, property damage from a motor vehicle accident, neighbourhood disputes, tenancy, consumer complaints and bailment. They can also advise you on family law issues regarding domestic violence, divorce/separation and parenting. Within criminal law, they can provide advice in relation to criminal offences, traffic offences and breaches of domestic violence orders. 
    `,
    `To organise a consultation, call (07) 3162 3282, <a href ='https://bcls.org.au/contact-us/' target='_blank'>request a call back on BCLS' website</a> or email enquiries@bcls.org.au.`,
    "https://www.facebook.com/BCLS.WYNNUM/",
    "https://www.linkedin.com/company/bayside-community-legal-service/?originalSubdomain=au",
    "",
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
    ['DISCRIMINATION','WELFARE', 'EMPLOYMENT'],
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
    "https://www.linkedin.com/company/basic-rights-queensland/about/",
    "",
    ""
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
        Consultations are available generally by booking as well as drop-in sessions, though due to the COVID-19 pandemic, all appointments must be booked. Further, all consultations are by phone, and held during office hours or on Wednesday evenings. 
    `,
    `To see if BNCLS can help with your matter, call (07) 3260 6820 between 9:00-16:00 Monday to Thursday.
    `,
    "https://www.facebook.com/Northside-Connect-658994620794556/",
    "",
    "",
    ""
    );
    dict["BNCLS"] = BNCLS;

    // Cairns Community Legal Centre
    let cairnsCLC = new entry(
        'Cairns Community Legal Centre', 'cairns.png',
    "Cairns Community Legal Centre Inc (CCLC) provides assistance for socially or financially disadvantaged members of the community with legal concerns in a variety of areas, both over the phone and in-person. In addition, they offer duty lawyer services for family and domestic violence cases at the Cairns Magistrates Court, as well as discretionary discrete assistance services throughout Queensland.",
    "http://www.cclc.org.au",
    "enquiry@cclc.org.au",
    [["(07) 4031 7688", "1800 062 608"],["Phone",""]],
    "https://www.google.com/maps/place/Cairns+Community+Legal+Centre/@-16.9232826,145.7732019,17z/data=!3m1!4b1!4m5!3m4!1s0x6978669248502ce3:0x2890ef414900ad4e!8m2!3d-16.9233033!4d145.7753631", 
    "Level 2, Main Street Arcade, 82 Grafton St, Cairns City, Queensland 4870",
    "cairns_community_legal_centre",
    ['FAMILY','DISCRIMINATION'],
    `
    Cairns Community Legal Centre Inc (CCLC) provides assistance for socially or financially disadvantaged members of the community with legal concerns in a variety of areas, both over the phone and in-person.
        <br><br>
        CCLC are also committed to providing legal education to the community, and achieve this through group presentations and workshops on a range of legal topics.
    `,
    `
    CCLC can provide information, referrals and legal advice, and will, in some situations, provide ongoing casework assistance. 
        <br><br>
        CCLC offers general legal services as well as assistance in areas of discrimination and human rights, mental health, consumer law, family law and elderly law. In addition, they offer a duty lawyer service at the Cairns Magistrates Court for domestic and family violence cases in partnership with the <a href='factSheets/NQWLS' target='_blank'>North Queensland Women's Legal Services</a>, as well as discretionary discrete assistance services across Queensland.
    `,
    `Contact the CCLC by calling (07) 4031 7688 or 1800 062 608 between 09:00-16:00 Mondays to Fridays, or visit the centre on the 2nd floor of the Main Street Arcade, 82 Grafton Street, Cairns from 09:00-16:00 Monday to Thursday, or 09:00-12:00 on Fridays. To access the CCLC's family law and domestic violence duty lawyer, approach them at the Cairns Magistrate Court on Thursdays without appointment.
    `,
    "https://www.facebook.com/cairnscommunitylegalcentre/",
    "",
    "",
    ""
    );
    dict["cairnsCLC"] = cairnsCLC;



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
    "",
    ""
    );
    dict["careGoondiwindi"] = careGoondiwindi;

    // Caxton Legal Centre
    let caxtonlegalcentre = new entry(
        'Caxton Legal Centre', 'caxton.jpg',
    "Caxton Legal Centre (CLC) is an independent, non-profit, non-government organisation. They advise and refer in a wide array of areas, and, in limited circumstances, assist with casework. In addition to these services, CLC advocates for a number of law reform projects every year.",
    "https://caxton.org.au",
    "caxton@caxton.org.au",
    "(07) 3214 6333",
    "https://www.google.com/maps/place/Caxton+Legal+Centre/@-27.4747474,153.0112587,17z/data=!3m1!4b1!4m5!3m4!1s0x6b91598ba2f2b2df:0xe5ecd4fffbe75833!8m2!3d-27.4747474!4d153.0134474", 
    "1 Manning St, South Brisbane, Queensland 4101",
    "caxton_legal_centre",
    ['CRIME', 'FAMILY', 'EMPLOYMENT', 'DEBT'],
    `
    Caxton Legal Centre (CLC) is an independent, non-profit, non-government organisation.
        <br><br>
        In addition to providing legal assistance, CLC advocates for law reform, <a href='https://caxton.org.au/about-caxton-legal-centre/law-reform/' target='_blank'>taking on various projects each year</a>.
        <br><br>
        CLC also implemented its first Reconciliation Action Plan in 2014 to further Australia's reconciliation with Aboriginal and Torres Strait Islander communities, and <a href='https://caxton.org.au/about-caxton-legal-centre/reconciliation-action-plan/' target='_blank'>has continued to develop plans since</a>.  
        <br><br>
        CLC is supported by a collection of volunteer lawyers and law students. They accept funding from the federal and Queensland governments, as well as independent donations. Occasionally, CLC fundraises for particular cases.
    `,
    `
    Caxton Legal Centre advises in a variety of areas of law, including human rights, family law, employment law, criminal charges, elder law, and more.
        <br><br>
        In areas of employment law, CLC can only assist those earning less than $80,000 annually, or who were doing so prior to dismissal. They cannot advise with regards to certain matters of employment law, such as unpaid wages, contracts or work cover. Further, CLC can only assist employees in employment law, not contractors. 
        <br><br>
        Due to limited resources, while CLC will endeavour to advise and refer, they can only handle casework in limited circumstances. In some courts, CLC offers a duty lawyer service.
        <br><br>
        <b>NOTE:</b> CLC cannot help employers, businesses, landlords, real estate agents, or guarantors seeking a solictor's certificate about a loan. Further, there are a number of specific matters in which caxton cannot assist, a full list of which can be found <a href='https://caxton.org.au/wp-content/uploads/2020/02/Matters-we-cannot-assist-with-website.pdf' target='_blank'>here</a>. Please consult this list prior to applying to CLC. If you are unsure if your matter is applicable, don't hesitate to ask us at the Queensland Legal Directory for some assistance!
    `,
    `Book an appointment with Caxton Legal Centre by calling (07) 3214 6333 between 09:00-16:00, Mondays to Friday.
    `,
    "https://www.facebook.com/caxtonlegalcentre/",
    "https://www.linkedin.com/company/caxtonlegalcentre/?originalSubdomain=au",
    "https://twitter.com/caxtonlegal?lang=en",
    ""
    );
    dict["caxtonlegalcentre"] = caxtonlegalcentre;   

    // Central Queensland CLC
    let central_qld_clc = new entry(
        'Central Queensland Community Legal Centre', 'cqclc.png',
    "Central Queensland Community Legal Centre (CQCLC) is a Rockhampton based centre which can provide advice on consumer law, criminal law, neighbourhood and tenancy disputes, estate administration, family law, employment law, and migration law. They hold advice clinics regularly, and can otherwise provide assistance in-person, over the phone, or by video call.",
    "https://www.cqclc.org.au/",
    "admin@cqclc.org.au",
    ["(07) 4922 1200", "1800 155 121"],["Phone",""],
    "https://www.google.com/maps/place/Central+Queensland+Community+Legal+Centre+Inc./@-23.3799527,150.515067,18.2z/data=!4m13!1m7!3m6!1s0x6bc300991aeb5a41:0x83113c8a10cf4f9d!2s240+Quay+St,+Rockhampton+QLD+4700!3b1!8m2!3d-23.3803746!4d150.5159459!3m4!1s0x6bc300980e20cd85:0x9943b8c4bbfc82d2!8m2!3d-23.3802694!4d150.5161044", 
    "240 Quay St, Rockhampton, Queensland 4700",
    "central_qld_clc",
    ['CRIME', 'TENANCY', 'EMPLOYMENT', 'WILLS', 'FAMILY', 'IMMIGRATION'],
    `
    Central Queensland Community Legal Centre is a Rockhampton based centre incorporated in 1996.  Their mission is to provide free legal services for vulnerable and disadvantaged people. They provide services from just south of Mackay to Bundaberg and west to the border with the Northern Territory.
        <br><br>
        CQCLC is also committed to providing community legal education to the public. This can include offering workshops on specific legal issues, providing legal information factsheets and delivering information to student bodies.
    `,
    `
    CQCLC can provide advice on consumer law, criminal law, neighbourhood and tenancy disputes, estate administration, family law, employment law, and migration law. They can offer advice in person, by phone, or via FaceTime/Skype, and have a <a href='https://www.cqclc.org.au/chatbot/' target='_blank'>chatbot</a> which can provide information 24/7.
        <br><br>
        CQCLC hold advice clinics in Emerald, Gladstone and Rockhampton throughout the week. There is also an additional estate administration clinic held once a month. Session times can be confirmed at CQCLC's <a href='https://www.cqclc.org.au/our-services/' target='_blank'>website</a>.
    `,
    `Book an appointment with Central Queensland Community Legal Centre by calling (07) 4922 1200 or free-calling 1800 155 121 between office hours.
    `,
    "https://www.facebook.com/CQCLC",
    "",
    "",
    ""
    );
    dict["central_qld_clc"] = central_qld_clc;   

    // Gold Coast CLC
    let goldCoastCLC = new entry(
        'Gold Coast Community Legal Centre', 'goldcoastclc.svg',
    "The Gold Coast Community Legal Centre is a generalist centre providing free legal advice and assistance throughout the Gold Coast region. They operate out of Southport and service the whole of the Gold Coast region from Beenleigh to Coolangatta.",
    "https://www.gcclc.org.au/",
    "office@gcclc.org.au",
    "(07) 5532 9611",
    "https://www.google.com/maps/place/The+Gold+Coast+Community+Legal+Centre/@-27.9637818,153.4085772,17z/data=!3m1!4b1!4m5!3m4!1s0x6b910ff26e05d885:0x80c8ff6a1fae8e50!8m2!3d-27.9636194!4d153.4106495", 
    "34 Railway St, Southport, Queensland 4215",
    "gold_coast_clc",
    ['FAMILY', 'CRIME', 'DEBT', 'TENANCY', 'WELFARE', 'EMPLOYMENT'],
    `
    The Gold Coast Community Legal Centre (GCCLC) is a generalist centre providing free legal advice and assistance throughout the Gold Coast region. 
        <br><br>
        The GCCLC operates out of Southport and services the whole of the Gold Coast region from Beenleigh to Coolangatta.   
    `,
    `
    In addition to legal advice, the GCCLC offers prototype and collaborative project work, community legal information and general information and referrals. Legal advice and assistance is offered Monday to Friday by appointment between 08:30-16:00, as well as via a Night Clinic on Tuesday evenings from 17:00. 
        <br><br>
        The Centre is able to provide legal assistance to clients in most areas of the law, including family law, consumer law, and neighbourhood disputes, however, it cannot assist business owners.
    `,
    `Book an appointment with the Gold Coast Community Legal Centre by calling (07) 5532 9611 or <a href='https://www.gcclc.org.au/request-a-call-back' target='_blank'>requesting a call-back online</a>.
    `,
    "https://www.facebook.com/GoldCoastLegalService/",
    "https://www.linkedin.com/company/gold-coast-community-legal-centre/?originalSubdomain=au",
    "",
    ""
    );
    dict["goldCoastCLC"] = goldCoastCLC;

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
    ['WILLS', 'FAMILY', 'YOUTH', 'CRIME', 'EMPLOYMENT', 'DEBT'],
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
    "",
    ""
    );
    dict["HubCL"] = HubCL;

    // Institute for Urban Indigenous Health
    let IUIH = new entry(
        'Institute for Urban Indigenous Health', 'iuih.jpg',
    'The Institute for Urban Indigenous Health Legal Service provides advice for individuals or families referred through the <a href="https://www.moretonatsichs.org.au/your-health/family-wellbeing/" target="_blank">Moreton ATSICHS Family Wellbeing Service</a> or by a general practitioner or allied health worker. They can assist with family law, discrimination or harassment, Centrelink reviews, SPER or debt recovery, elder abuse and tenancy matters.',
    "http://www.iuih.org.au/",
    "reception@iuih.org.au",
    "(07) 3828 3600",
    "https://www.google.com/maps/place/Institute+for+Urban+Indigenous+Health/@-27.4363131,153.0182591,15z/data=!3m2!4b1!5s0x6b9159c4b02acd2f:0xd42ccac1e6205b07!4m5!3m4!1s0x6b9159eadbc8a5a7:0xb487302427344a55!8m2!3d-27.4363134!4d153.0270139", 
    "22 Cox Road, Windsor, Queensland 4030",
    "institute_for_urban_indigenous_health",
    ['WELFARE', 'FAMILY', 'DISCRIMINATION', 'TENANCY', 'DEBT', 'INDIGENOUS'],
    `
    The Institute for Urban Indigenous Health was founded in 2009 and pursues the planning, development and delivery of health, family wellbeing and social support services to the Aboriginal and Torres Strait Islander population of South East Queensland.
        <br><br>
    IUIH identifies the link between legal matters and health, and provides legal education and support to Aboriginal and Torres Strait Islander people, particularly those experiencing hardship. The IUIH Legal Service provides advice for individuals or families referred through <a href='https://www.moretonatsichs.org.au/your-health/family-wellbeing/' target='_blank'>the Moreton ATSICHS Family Wellbeing Service</a> or by a general practitioner or allied health worker. 
    `,
    `
    The IUIH Legal Service team assists women, parents or guardians of children, and elders. They can assist with family law, discrimination or harassment, Centrelink reviews, SPER or debt recovery, elder abuse and tenancy matters. 
        <br><br>
    They cannot assist with criminal law, personal injury or migration matters.
    `,
    `
    To access IUIH's legal service, seek referral by contacting the <a href='https://www.moretonatsichs.org.au/your-health/family-wellbeing/' target='_blank'> Moreton ATSICHS clinics</a>.
    `,
    "https://www.facebook.com/InstituteforUrbanIndigenousHealth/",
    "https://www.linkedin.com/company/institute-of-urban-indigenous-health/?originalSubdomain=au",
    "https://twitter.com/iuih_?lang=en",
    "https://www.instagram.com/iuih/?hl=en"
    );
    dict["IUIH"] = IUIH;   

    let Junkuri_Laka = new entry(
        'Junkuri Laka Community Centre', 'Junkuri_Laka.png',
    "The Junkuri Laka Community Legal Centre, also known as the Mornington Island Community Legal Centre, is based on Mornington Island and promotes the wellbeing of the people of the Wellesley Islands. The centre runs a domestic violence program, a men's support group including individuals struggling with violence and/or alcohol, and provides mediation services.",
    "NONE",
    "nikita.junkurilaka@gmail.com",
    [["(07) 4745 7278", "1800 062 608"],["Phone",""]],
    "https://www.google.com/maps/place/Junkuri+Laka/@-18.7237645,131.9785424,6.19z/data=!4m5!3m4!1s0x69f4448548a94161:0x684839f7f4803d5d!8m2!3d-16.6627594!4d139.1721021", 
    "2 Lardil Street Gununa Mornington Island, Queensland, 4871",
    "junkuri_laka",
    ['WILLS', 'INDIGENOUS', 'FAMILY', 'CRIME', 'WELFARE'],
    `
    The Junkuri Laka Community Legal Centre is based on Mornington Island and promotes the wellbeing of the people of the Wellesley Islands.
    <br>
    The centre was established in 2013, and is also known as the Mornington Island Community Legal Centre.
    `,
    `
    The Junkuri Laka Community Legal Centre engages with government organisations and is active in promoting the human, legal and civil rights of residents of the Wellesley Islands.
    <br>
    The centre runs a domestic violence program, a men's support group including individuals struggling with violence and/or alcohol, and provides mediation services. They cannot assist in matters related to general banking services, but can assist in such disputes. The centre is also unable to assist where conflicts of interest occur, such as disputes between two members of the community.
    `,
    `
    To seek assistance, contact the Junkuri Laka Community Legal Centre by email or phone at (07) 4745 7278.
    `,
    "",
    "",
    "",
    ""
    );
    dict["Junkuri_Laka"] = Junkuri_Laka;   
    
                //function entry(name, imgPath, about, url, email, phone, addressLink, addressDisp, fsURL, categories, aboutFS, howHelpFS, applyText, fb, linkedin, twitter, insta){ // TODO


    // [LawRight]
    let LAWRIGHT = new entry(
    'Law Right', 'LawRight.svg',
    "LawRight, formerly known as QPILCH, is a non-for-profit which increases access to justice by connecting clients with pro bono lawyers. These lawyers work with health and social workers to assist people experiencing mental illness, homelessness & other forms of hardship, as well as to provide services for vulnerable individuals navigating Queensland’s courts and tribunals.",
    "http://www.lawright.org.au/",
    "admin@lawright.org.au",
    "(07) 3846 6317",
    "https://www.lawright.org.au/find-legal-help/community-health-justice-partnerships/", // AddressLink
    'Numerous Locations', 
    "law_right",
    ['WELFARE', 'DISCRIMINATION', 'DEBT', 'TENANCY'],
    `
    Founded in 2001, LawRight is a not-for-profit organisation that aims to improve access to justice through strategic partnerships with pro bono lawyers. Each year over 800 lawyers, 170 barristers and 140 law students give up their time to help disadvantaged members of the community. 
    <br><br>
    At 15 Community and Health Justice Partnership locations, pro bono lawyers work with health and social workers to assist people experiencing mental illness, homelessness & other forms of hardship. They also provide services for vulnerable individuals navigating Queensland’s courts and tribunals. 
    `,
    `
    LawRight can provide advice and support in a range of civil law areas for individuals who could not otherwise fund legal assistance. However, they cannot assist with criminal law, family law, native title matters or complex commercial disputes.
    <br><br>
    LawRight may be able to provide you with legal advice at one of their outreach locations. They may also be able to partner you with one of the pro bono lawyers that work with them to provide you with ongoing legal support. 
    `,
    `To get in contact with LawRight, fill out an <a href='https://www.lawright.org.au/apply/' target='_blank'>online form</a>, or call (07) 3846 6317.`,
    "https://www.facebook.com/LawRightQLD/",
    "https://www.linkedin.com/company/lawrightqld/?originalSubdomain=au",
    "https://twitter.com/lawrightqld?lang=en",
    "https://www.instagram.com/lawrightqld/?hl=en",
    );
    dict["LAWRIGHT"] = LAWRIGHT;

    // [LGBTI]
    let LGBTI = new entry(
    'The LGBTI Legal Service', 'lgbti.png',
    "The LGBTI Legal Service provides legal support on a free and confidential basis to Queensland residents who identify as members of the lesbian, gay, bisexual, trans, and intersex community free of charge. In addition to providing legal services, the LGBT Legal Service is also active in the area of law reform, via parliamentary submissions and the provision of free legal toolkits and fact sheets on their website.",
    "https://lgbtilegalservice.org.au/",
    "mail@lgbtilegalservice.org",
    "(07) 3124 7160",
    "https://www.google.com/maps/place/20+Hockings+St,+West+End+QLD+4101/@-27.4746414,153.0058547,17z/data=!3m1!4b1!4m5!3m4!1s0x6b9150a43b5f2863:0xdd28c5e3334f8a30!8m2!3d-27.4746414!4d153.0080434", // AddressLink
    'Level 1, Oxley House, 20 Hockings Street, West End, Queensland 4101', 
    "LGBTI",
    ['LGBTIQ', 'FAMILY', 'CRIME', 'DISCRIMINATION', 'EMPLOYMENT', 'WELFARE'],
    `The LGBTI Legal Service provides legal support on a free and confidential basis to Queensland residents who identify as members of the lesbian, gay, bisexual, trans, and intersex community.
    <br><br>
    The service offers advice on legal issues specifically linked to a person's identification as LGBTI and/or for people who would prefer to interact with a solicitor who has an understanding of the particular treatment of LGBTI individuals both culturally and legally.
    <br><br>
    The services provided by the LGBTI Legal Service are free of charge.
    <br><br>
    In addition to providing legal services, the LGBT Legal Service is also active in the area of law reform, via parliamentary submissions and the provision of free legal toolkits and fact sheets on their website.`,
    `With no means testing, the LGBTI Legal Service is able to assist any members of the Queensland LGBTI community. They offer support in legal services relating to:
    <li>Family law</li>
    <li>Domestic violence</li>
    <li>Surrogacy and parenting rights</li>
    <li>Criminal law (including victim support)</li>
    <li>Employment law</li>
    <li>Gender identity</li>
    <li>Civil law</li>
    <li>Administrative law and government decisions</li>
    <li>Discrimination and human rights issues</li>
    <br>
They do not offer assistance in the areas of:
    <li>Immigration and visas</li>
    <li>Medical negligence</li>
    <li>Building disputes</li>
    <li>Personal injuries</li>
    <li>Taxation law</li>
    <li>Commercial law</li>
    <li>Investments</li>
    <br>
The volunteer lawyers of the service are unable to provide legal representation, though offer legal advice for one to represent themselves in court. The LGBTI Legal Service also may not advise on the behalf of someone else without a power of attorney.`,
    `Apply for in-person consultation at the Brisbane office or telephone/videoconference for clients outside of Brisbane by calling (07) 3124 7160. `,
    "https://www.facebook.com/LGBTILegalService",
    "https://www.linkedin.com/company/lgbti-legal-service-inc/?originalSubdomain=au",
    "https://twitter.com/lgbtilegal",
    "https://www.instagram.com/lgbtilegalservice/",
    );
    dict["LGBTI"] = LGBTI;

    // [Mackay Regional CLC]
    let mackay = new entry(
    'Mackay Regional Community Legal Centre Inc.', 'mackay_clc.png',
    "The Mackay Regional Community Legal Centre assists financially disadvantaged people in the Mackay, Whitsunday and Iasaac regions, by providing legal advice, information, referrals and ongoing assistance. MRCLC provides a generalist legal service, covering family law (property and parenting matters), employment, debt, and neighbourhood or consumer disputes. Further, as part of the Queensland Statewide Tenant Advice and Referral Service (QSTARS), MRCLC advises tenants and rooming accomodation residents.",
    "https://mrclc.com.au/",
    "admin@mrclc.com.au",
    "(07) 4953 1211",
    "https://www.google.com/maps/place/Mackay+Regional+Community+Legal+Centre/@-21.1408117,149.1764143,15z/data=!3m1!4b1!4m5!3m4!1s0x6bdbd3f88118c089:0xa586c4da4b078f1e!8m2!3d-21.1409533!4d149.1851312", // AddressLink
    'Suite 9, The Dome, 134 Victoria Street, Mackay, Queensland 4740', 
    "mackay_regional_clc",
    ['WILLS', 'TENANCY'],
    `
    The Mackay Regional Community Legal Centre ('MRCLC') assists financially disadvantaged people in the Mackay, Whitsunday and Iasaac regions, by providing legal advice, information, referrals and ongoing assistance.
    <br><br>
    In addition to legal assistance, MRCLC also educates local organisations and members of the community through legal presentations.
    `,
    `
    MRCLC provides a generalist legal service, covering family law (property and parenting matters), employment, debt, and neighbourhood or consumer disputes. Further, as part of the Queensland Statewide Tenant Advice and Referral Service (QSTARS), MRCLC advises tenants and rooming accomodation residents.
    <br><br>
    MRCLC's solicitors provide advice at pre-booked appointments (both in person and over the phone) from 09:00 to 16:00 Monday to Friday, and can also arrange appointments from 08:30 to 17:00 where necessary. Once a month, MRCLC also provides offer appointments through their outreach services in Bowen, Prosperine, Cannonvale and Sarina. Finally, MRCLC hold legal advice evenings twice a month between 17:35 and 20:00 by appointment.
    `,
    `To get in touch with MRCLC, contact them on (07) 4953 1211 between 09:00-16:00 on weekdays.`,
    "https://www.facebook.com/MackayRegionalCLC/",
    "",
    "",
    "",
    );
    dict["mackay"] = mackay;

    // Moreton Bay Regional Community Legal Service
    let mbrcls = new entry(
    'Moreton Bay Regional Community Legal Service', 'Moreton.png',
    'The Moreton Bay Regional Community Legal Service is a generalist service which supports disadvantaged, vulnerable and marginalised individuals in the Moreton Bay region. They provide a variety of legal services, including the provision of legal advice, community legal education, outreach work, court support, and advocacy, case work, and document assistance.',
    "https://www.mbrcls.org.au/",
    "office@mbrcls.org.au",
    "(07) 5495 5916",
    "https://www.google.com/maps/place/Moreton+Bay+Regional+Community+Legal+Service/@-27.0837242,152.9467609,17z/data=!3m1!4b1!4m5!3m4!1s0x6b93f3c15a48aadb:0xf2644ae58e917941!8m2!3d-27.0837242!4d152.9489496", // AddressLink
    '9 George St, Caboolture, Queensland 4510', 
    "moreton_bay_regional",
    ['FAMILY', 'CRIME', 'DEBT', 'WILLS', 'WELFARE', 'DISCRIMINATION', 'TENANCY'],
    `
    The Moreton Bay Regional Community Legal Service ('MBRCLS') is a generalist service which provides legal services to disadvantaged, vulnerable and marginalised individuals in the Moreton Bay region.
    <br><br>
    In addition to providing legal advice and referrals, MBRCLS educates the community on legal issues through their <a href='https://www.mbrcls.org.au/legal-chat/' target='_blank'>Legal Chat Community Legal Education Program</a>.  
    `,
    `
    MBRCLS provides a variety of legal services, including the provision of legal advice, community legal education, outreach work, court support and advocacy. Further, MBRCLS provide ongoing case work and legal document assistance, though these services are generally limited to individuals on annual incomes of $35,000 or less, and preference is given to individuals with literary, social or economic disadvantages.
    <br><br>
    As a generalist service, MBRCLS can assist in the areas of family law, criminal law, domestic violence, human rights, bankruptcy & debt, wills & estates, tenancy issues, discrimination, motor vehicle offences, government subsidies & pensions, and civil disputes.
    `,
    `To get in touch with MBRCLS, contact them on (07) 5495 5916 or fill out <a href='https://www.mbrcls.org.au/morton-bay-legal-services/#page-footer' target='_blank'>the contact form</a> on their website.`,
    "https://www.facebook.com/mbrcls/",
    "https://www.linkedin.com/company/moreton-bay-regional-community-legal-service-inc-/?originalSubdomain=au",
    "https://twitter.com/moretonbaylegal",
    "",
    );
    dict["mbrcls"] = mbrcls;

    // Pine Rivers Community Legal Service
    let pine_rivers = new entry(
    'Pine Rivers Community Legal Service', 'encircle.jpeg',
    "An initiative of <a href='https://encircle.org.au/about/' target='_blank'>Encircle Ltd.</a>, the Pine Rivers Community Legal Service offers general legal assistance in the greater Northern Brisbane area. PRCLS is a general legal service, providing advice, document drafting, duty lawyers at the Pine Rivers Magistrates Court and mediation services.",
    "https://encircle.org.au/community-legal-service/",
    "prcls@encircle.org.au",
    "(07) 3881 3500",
    "https://www.google.com/maps/place/Pine+Rivers+Community+Legal+Service/@-27.3003355,152.9862021,17z/data=!3m1!4b1!4m5!3m4!1s0x6b93fc95ad352f9f:0xd26b52b3afbd92d6!8m2!3d-27.3003643!4d152.9882778", // AddressLink
    '4/481 Gympie Road, Strathpine, Queensland 4500', 
    "pine_rivers",
    ['FAMILY', 'CRIME', 'DEBT', 'WILLS', 'WELFARE'],
    `
    An initiative of <a href='https://encircle.org.au/about/' target='_blank'>Encircle Ltd.</a>, the Pine Rivers Community Legal Service ('PRCLS') offers general legal assistance in the greater Northern Brisbane area. In addition to legal services, PRCLS engages in law reform activities and legal education, while Encircle offers link-ups of services to support clients' broader needs, such as counselling and family support.  
    `,
    `
    PRCLS is a general legal service, providing advice, document drafting, duty lawyers at the Pine Rivers Magistrates Court and mediation services. 
    <br>
    <br>
    Day appointments are held from 09:00-16:30, Mondays-Fridays, while short walk-ins are also accepted on Thursday nights from 17:45-19:30 (aside from during the Queensland December to January school holidays and public holidays) at Strathpine. Day appointments are also available at a number of other locations, listed on their website. 
    `,
    `Book an appointment by calling PRCLS at (07) 3881 3500 or visiting their offices from 09:00-16:30 Mondays-Fridays.`,
    "https://www.facebook.com/pineriverscommunitylegalservice/",
    "https://www.linkedin.com/company/pine-rivers-community-legal-service/about/",
    "",
    "",
    );
    dict["pine_rivers"] = pine_rivers;

    // Suncoast CLS
    let suncoast = new entry(
    'Suncoast Community Legal Service', 'scls.png',
    "Suncoast Community Legal Service Inc is an independent, non-profit community organisation providing legal advice, referrals and education. They can provide legal advice and appropriate referrals in the areas of family law, crime, employment law, debts, consumer complaints, discrimination, residential tenancies and neighbourhood disputes.",
    "http://www.suncoastcommunitylegal.org",
    "reception@suncoastcommunitylegal.org",
    "(07) 5376 7800",
    "https://www.google.com/maps/place/Suncoast+Community+Legal+Service+Inc/@-26.653338,153.0806823,15z/data=!3m1!4b1!4m5!3m4!1s0x6b9376621d5441a1:0x10f34d3fac2a782d!8m2!3d-26.6533463!4d153.0894354", // AddressLink
    '170 Horton Parade, Maroochydore, Queensland 4558', 
    "suncoast",
    ['FAMILY', 'CRIME', 'DEBT', 'WILLS', 'WELFARE', 'EMPLOYMENT', 'DISCRIMINATION', 'TENANCY'],
    `
    Suncoast Community Legal Service Inc ('SCLS') is an independent, non-profit community organisation providing legal advice, referrals and education. Their mission is to provide quality legal services to address disadvantage in the Sunshine Coast community using volunteers and staff.
    <br><br>
    Since their inception in 1984, SCLS has developed strong community and referral networks across the region. They use these networks to secure better access to justice for people facing hardship and disadvantage in the Sunshine Coast region. 
    <br><br>
    SCLS holds regular consultations at Maroochydore, Caloundra, Landsborough, Noosa, Pomona, Maleny and Nambour.
    `,
    `
    SCLS can provide legal advice and appropriate referrals in the areas of family law, crime, employment law, debts, consumer complaints, discrimination, residential tenancies and neighbourhood disputes. In these areas, SCLS does not provide ongoing casework.
    <br><br>
    SCLS also provides a dedicated Elder Abuse Prevention Support service. They provide advice and some ongoing casework regarding common forms of elder abuse, wills, enduring powers of attorney, and grandparents' rights.
    <br><br>
    SCLS does not provide advice in relation to commercial matters or property conveyances, nor can they assist landlords, employee organisations or business owners.
    `,
    `Book a consultation with SCLS by contacting them at (07) 5376 7800 or through their website.`,
    "https://www.facebook.com/SuncoastLegal/",
    "",
    "",
    "",
    );
    dict["suncoast"] = suncoast;