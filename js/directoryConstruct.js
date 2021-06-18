/// CONSTRUCTOR
function entry(name, imgPath, about, url, email, phone, phoneExtra, addressLink, addressDisp, fsURL, categories){ // TODO
    this.name = name;
    this.imgPath = imgPath;
    this.about = about;
    this.url = url;
    this.email = email;
    this.phone = phone;
    this.phoneExtra = phoneExtra;
    this.addressLink = addressLink;
    this.addressDisp = addressDisp;
    this.fsURL = fsURL;
    this.categories = categories;
}
///

/// POPULATE FUNCTION
function populateHTML(entry) {
    console.log(entry)
    generatedHTML = `
    <h3 class="directoryH3">` + entry.name + `</h3>
    <div class="row">
        <div class="directory-col-img">
            <img src="` + entry.imgPath + `" >
        </div>
        <div class="directory-col-abt">
            <p>` + entry.about + `</p>
        </div>
        <div class="directory-col-lnks"> 
            <b>Website: </b><a href="` + entry.url + `" target="_blank">` + entry.url + `</a><br>
            <b>E-Mail: </b><a href="mailto:` + entry.email + `">` + entry.email + `</a><br>
            ` + entry.phone + `
            <b>Address: </b><a href='` + entry.addressLink + `' target='_blank'>` + entry.addressDisp + `</a><br>
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

///

/// ENTRIES
var dict = new Object();
var categories = ["CRIME", "DISCRIMINATION", "TENANCY "]
// function entry(name, imgPath, about, url, email, phone, phoneExtra, addressLink, addressDisp, fsURL, categories){ // TODO
// BRQ
let BRQ = new entry(
    'Basic Rights Queensland', 'images/logos/BRQ.png',
"Basic Rights Queensland provides legal advice and advocacy with regards to Centrelink assistance, disability discrimination and women’s workplace issues. Their team includes lawyers, social workers and volunteers, who work to provide community legal education, advocate for law reform and provide specialist services to other community organisations.",
"http://www.brq.org.au",
"brq@brq.org.au",
`<b>Phone: </b><a href="tel:+61-07-3847-5532">(07) 3847 5532</a><br>
<b>Free Call (Social Security / Disability Discrimination): </b><a href="tel:1800-358-511">1800 358 511</a><br>
<b>Free Call (Women's Employment): </b><a href="tel:1800-621-458">1800 621 458</a><br>`,
"", // Extra phone
"", // AddressLink
"", // AddressDisp
"BRQ",
['DISCRIMINATION','TENANCY', 'CRIME']
);
dict["BRQ"] = BRQ;

// BNCLS
let BNCLS = new entry(
    'Brisbane North Community Legal Service', 'images/logos/NorthsideConnect.png',
"Brisbane North Community Legal Service (BNCLS) is a generalist community legal service which provides free legal advice, information, and referral to individuals on a range of legal issues including family law, domestic violence, civil disputes, criminal matters, neighbourhood issues, elder law and employment.",
"https://northsideconnect.org.au/legal-service/",
"admin@northsideconnect.org.au",
`<b>Phone: </b><a href="tel:+61-07-3260-6820">(07) 3260 6820</a><br>`,
"", // Extra Phone
"https://www.google.com/maps/place/Northside+Connect/@-27.4013307,153.051648,15z/data=!3m1!4b1!4m5!3m4!1s0x6b915861ecd5f391:0x16401a8027fcdbf1!8m2!3d-27.4013621!4d153.0603798", 
"14 Station St, Nundah, Queensland 4012</a><br>",
"brisbane_north",
['DISCRIMINATION','TENANCY', 'CRIME']
);
dict["BNCLS"] = BNCLS;

