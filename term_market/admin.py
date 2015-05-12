from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from term_market.models import User, Enrollment, Subject, Teacher, Term, Offer


class UserAdmin(OriginalUserAdmin):
    fieldsets = OriginalUserAdmin.fieldsets + (
        ('I@IET', {
            'fields': ('transcript_no', 'internal_id')
        }),
    )
    list_display = OriginalUserAdmin.list_display + ('transcript_no', )


class TermAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'teacher', 'start_time', 'week')
    list_display_links = ('id', 'subject')
    filter_horizontal = ('students', )


class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'offered_term', 'donor', 'is_available')
    list_display_links = ('id', 'offered_term')


admin.site.register(User, UserAdmin)
admin.site.register(Enrollment)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Term, TermAdmin)
admin.site.register(Offer, OfferAdmin)
