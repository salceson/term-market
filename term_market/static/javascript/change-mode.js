/**
 * Created by Joanna on 2015-05-12.
 */

var nightMode = false;

function changeCSS() {
		nightMode = !nightMode;
		var cssLinkIndex = 2;
		var nightCSS = "../stylesheets/cover.css";
		var dayCSS = "../stylesheets/cover-light.css";

        var oldLink = document.getElementsByTagName("link").item(cssLinkIndex);

        var newLink = document.createElement("link");
        newLink.setAttribute("rel", "stylesheet");
        newLink.setAttribute("type", "text/css");

        if(nightMode){
        	newLink.setAttribute("href", nightCSS);
        } else {
        	newLink.setAttribute("href", dayCSS);
        }

        document.getElementsByTagName("head").item(0).replaceChild(newLink, oldLink);
}


