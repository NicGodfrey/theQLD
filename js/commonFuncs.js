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
        console.log("num_type not recognised! Returning unformatted number!")
        return number;
    }
}