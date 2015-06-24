from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin

from term_market.models import User, Enrollment, Subject, Teacher, Term, Offer, BugReports


class UserAdmin(OriginalUserAdmin):
    fieldsets = OriginalUserAdmin.fieldsets + (
        ('I@IET', {
            'fields': ('transcript_no', 'internal_id')
        }),
    )
    list_display = OriginalUserAdmin.list_display + ('transcript_no', )


class TermAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'enrollment', 'subject', 'teacher', 'start_time', 'week')
    list_display_links = ('id', 'external_id')
    filter_horizontal = ('students', )


class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment', 'offered_term', 'donor', 'bait', 'is_available')
    list_display_links = ('id', )


class EnrollmentAdmin(admin.ModelAdmin):
    change_list_template = 'term_market/admin/enrollments_change_list.html'
    list_display = ('id', 'name')


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name')
    list_display_links = ('id', 'external_id')


class BugReportsAdmin(admin.ModelAdmin):
    list_display = ('message', 'user')
    list_display_links = ('message', )


admin.site.register(User, UserAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Teacher)
admin.site.register(Term, TermAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(BugReports, BugReportsAdmin)
