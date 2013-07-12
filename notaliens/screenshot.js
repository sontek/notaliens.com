var page = require('webpage').create();
page.onError = function(msg, trace){
    //if there is a run time error in the loaded page, log it
    console.log("JS Error on the page: " + msg);
};

var system = require('system');

var url = system.args[1];
var path = system.args[2];

console.log("Loading page... ", url);

page.open(url, function () {
    page.render(path);
    phantom.exit();
});

console.log("Saving to path...", path);
