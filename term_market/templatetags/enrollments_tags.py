from django.contrib.admin.templatetags.admin_list import items_for_result, result_headers
from django.core.urlresolvers import reverse
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

URL_TEMPLATE = '<a href="%s" class="grp-button grp-btn-default">%s %s</a>&nbsp;'
TD_TEMPLATE = '<td>%s</td>'
ICON_TEMPLATE = '<i class="fa %s"></i>'


def extend_results_with_custom_columns(cl, additional_links):
    for res in cl.result_list:
        rl = list(items_for_result(cl, res, None))
        for column in additional_links:
            column_str = ''
            for link in column:
                link_str = reverse(link['url_name'], kwargs={'enrollment': res.id})
                icon_str = ICON_TEMPLATE % link['icon']
                column_str += URL_TEMPLATE % (link_str, icon_str, link['url_text'])
            rl.append(mark_safe(TD_TEMPLATE % column_str))
        yield rl


def extended_result_list(cl, additional_links, additional_headers):
    headers = list(result_headers(cl))
    for header in additional_headers:
        headers.append(header)

    return {
        'cl': cl,
        'result_headers': headers,
        'results': list(extend_results_with_custom_columns(cl, additional_links))
    }


def enrollment_result_list(cl):
    additional_links = [
        [
            {
                'url_name': 'import_terms',
                'url_text': 'Import terms',
                'icon': 'fa-upload'
            },
            {
                'url_name': 'import_department_list',
                'url_text': 'Import department list',
                'icon': 'fa-upload'
            },
            {
                'url_name': 'import_conflicts',
                'url_text': 'Import conflicts',
                'icon': 'fa-upload'
            },
            {
                'url_name': 'export',
                'url_text': 'Export',
                'icon': 'fa-download'
            },
            {
                'url_name': 'run_solver',
                'url_text': 'Run solver',
                'icon': 'fa-play-circle'
            }
        ],
    ]
    headers = [
        {'text': 'Actions', 'sortable': False}
    ]

    return extended_result_list(cl, additional_links, headers)


enrollment_result_list = register.inclusion_tag("admin/change_list_results.html")(enrollment_result_list)
