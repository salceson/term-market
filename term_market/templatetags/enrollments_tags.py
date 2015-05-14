from django.contrib.admin.templatetags.admin_list import items_for_result, result_headers
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


def results(cl, additional_links):
    for res in cl.result_list:
        rl = list(items_for_result(cl, res, None))
        for link in additional_links:
            rl.append(mark_safe(link['url_template'] % res.id))
        yield rl


def extended_result_list(cl, additional_links):
    headers = list(result_headers(cl))
    for header in additional_links:
        headers.append(header)

    return {
        'cl': cl,
        'result_headers': headers,
        'results': list(results(cl, additional_links))
    }


# This function is an example template tag for use in an overridden change_list.html template.
def enrollment_result_list(cl):
    additional_links = (
        {'text': 'Actions',
         'sortable': False,
         'url_template': '<td><a href="/admin/term_market/enrollment/%d/import/terms/"'
                         ' class="grp-button grp-btn-default">Import terms</a></td>'
         },
    )

    return extended_result_list(cl, additional_links)


enrollment_result_list = register.inclusion_tag("admin/change_list_results.html")(enrollment_result_list)