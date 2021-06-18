function phone_disp2link(number, num_type) {
    if (num_type == "1800") {
        var formattedNum = "tel:" 
        formattedNum += number.replace(/\s+/g, '-');      // Replace space with hyphen: 1800 123 456 --> 1800-123-456   
        console.log("Formatted number " + number + " to " + formattedNum)
        return formattedNum
    } else if (num_type == "07") {
        var formattedNum = "tel:+61-" 
        formattedNum += number.replace(/\s+/g, '-');      // Replace space with hyphen
        formattedNum =  formattedNum.replace(/[()]/g,''); // Delete parantheses (07) 1234 5678 --> 07 1234 5678  
        console.log("Formatted number " + number + " to " + formattedNum)
        return formattedNum
    } else {
        console.log("num_type " + num_type + " not recognised! Returning unformatted number!")
        return number;
    }
}

function parsePhones(input, prefixes){
    prefixes = prefixes || ["Phone", ""];
    generatedHTML = "";
    if (Array.isArray(input)) {
        console.log("Length: " + input.length)
        for (i = 0; i < input.length; i++) {
            phoneDisp = input[i];
            var phoneType;
            console.log(phoneDisp.substring(0, 3));
            if (phoneDisp.substring(0, 3) == "(07") {
                phoneType = "07";
                console.log(phoneType);
            } else if (phoneDisp.substring(0, 4) == "1800") {
                phoneType = "1800";
            }
            phoneLink = phone_disp2link(phoneDisp, phoneType);
            if (typeof prefixes[i] != undefined){
                prefix_i = prefixes[i];
            } else {
                prefix_i = "";
            }
            console.log()
            if (prefix_i == ""){
                generatedHTML += '<a href="' + phoneLink + '">' + phoneDisp + '</a><br>'    
            } else {
                generatedHTML += '<b>' + prefix_i + ': </b><a href="' + phoneLink + '">' + phoneDisp + '</a><br>'
            }
        } 
    } else {
        phoneDisp = input;
        var phoneType;
        console.log(phoneDisp.substring(0, 3));
        if (phoneDisp.substring(0, 3) == "(07") {
            phoneType = "07";
            console.log(phoneType);
        } else if (phoneDisp.substring(0, 4) == "1800") {
            phoneType = "1800";
        }
        phoneLink = phone_disp2link(input, phoneType);
        generatedHTML = '<b>Phone: </b><a href="' + phoneLink + '">' + phoneDisp + '</a><br>'
        return generatedHTML;
    }
    return generatedHTML;
}