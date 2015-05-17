/**
 * Created by Joanna on 2015-05-12.
 */

var link = document.getElementById("css-skin");
var nightCSS = Django.static('css/cover.css');
var dayCSS = Django.static('css/cover-light.css');

function changeCSS() {
    nightMode = !nightMode;

    if (nightMode) {
        $.cookie('skin', 'night', { path: '/', expires: 3650 });
        link.href = nightCSS;
    } else {
        $.cookie('skin', 'day', { path: '/', expires: 3650 });
        link.href = dayCSS;
    }
}

var nightMode = ($.cookie('skin') != 'day');