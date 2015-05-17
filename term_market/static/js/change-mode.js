/**
 * Created by Joanna on 2015-05-12.
 */

NIGHT_CSS = Django.static('css/cover.css');
DAY_CSS = Django.static('css/cover-light.css');

nightMode = ($.cookie('skin') != 'day');
stylesheet = $('#skin-css');

$('#skin-toggle').click(function () {
    nightMode = !nightMode;

    if (nightMode) {
        $.cookie('skin', 'night', { path: '/', expires: 3650 });
        stylesheet.attr('href', NIGHT_CSS);
    } else {
        $.cookie('skin', 'day', { path: '/', expires: 3650 });
        stylesheet.attr('href', DAY_CSS);
    }
});
$('#skin-toggle').show();