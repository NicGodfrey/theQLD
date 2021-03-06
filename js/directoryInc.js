$(document).ready(function () { // Call function when DOM is ready
    $("div[data-includeHTML-Dir]").each(function () {     
        console.log("LOADING...!");
        console.log($(this).attr("data-includeHTML-Dir"))
        entryObj = dict[$(this).attr("data-includeHTML-Dir")];
        console.log(entryObj)
        generatedHTML = populateHTML(entryObj)
        console.log(generatedHTML);
        console.log($(this))
        document.getElementById($(this).attr("data-includeHTML-Dir")).innerHTML = generatedHTML;
    });
});

$(document).ready(function () { // Call function when DOM is ready
    $("div[data-includeHTML-DirCat]").each(function () {     
        console.log("LOADING...");
        category = $(this).attr("data-includeHTML-DirCat");
        console.log(category);
        generatedCatHTML = populateCatHTML(category)
        document.getElementById($(this).attr("data-includeHTML-DirCat")).innerHTML = generatedCatHTML;
        
    });
});

$(document).ready(function () { // Call function when DOM is ready
    $("div[data-FS-objName]").each(function () {     
        console.log("LOADING...");
        objName = $(this).attr("data-FS-objName");
        objIt = dict[objName];
        generatedFSHTML = populateFS(objIt)
        console.log("Generated FS: " + generatedFSHTML)
        document.getElementById($(this).attr("data-FS-objName")).innerHTML = generatedFSHTML;
        
    });
});