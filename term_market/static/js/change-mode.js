NIGHT_CSS = '//maxcdn.bootstrapcdn.com/bootswatch/3.3.4/darkly/bootstrap.min.css';
DAY_CSS = '//maxcdn.bootstrapcdn.com/bootswatch/3.3.4/flatly/bootstrap.min.css';

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