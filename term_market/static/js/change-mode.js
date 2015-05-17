/**
 * Created by Joanna on 2015-05-12.
 */

var nightMode = true;

function changeCSS() {
    nightMode = !nightMode;
    var nightCSS = Django.static('css/cover.css');
    var dayCSS = Django.static('css/cover-light.css');
    var link = document.getElementById("css-skin")

    if (nightMode) {
        link.href = nightCSS;
    } else {
        link.href = dayCSS;
    }
}
