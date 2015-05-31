# -*- coding: utf-8 -*-
from uuid import uuid4 as random_uuid

from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Enrollment, Offer, Term


@permission_required("term_market.change_enrollment")
def export_solver_data(request, enrollment=None):
    uuid = str(random_uuid())
    print uuid
    enrollment = get_object_or_404(Enrollment, id=enrollment)
    conflicts = get_conflicts_for_enrollment(enrollment)
    print conflicts
    offers = get_offers(enrollment)
    print offers
    return JsonResponse({"conflicts": conflicts, "offers": offers})


def get_conflicts_for_enrollment(enrollment):
    conflicts = {}
    for term in Term.objects.filter(subject__enrollment=enrollment):
        term_conflicts = map(lambda c: c.id, list(term.conflicting_terms.all()))
        conflicts[str(term.id)] = term_conflicts
    return conflicts


def get_offers(enrollment):
    offers_list = []
    offers = Offer.objects.filter(offered_term__subject__enrollment=enrollment)
    for offer in offers:
        offers_list.append({
            "id": offer.id,
            "donor": offer.donor.id,
            "offered_term": offer.offered_term.id,
            "wanted_terms": map(lambda o: o.id, offer.wanted_terms.all())
        })
    return {"offers": offers_list}
