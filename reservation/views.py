from django.shortcuts import render
from .selectors import select_all_reservations_with_previous_reservation


def reservations_with_previous_reference(request):
    return render(request, 'reservations_with_previous_reference.html',
                  {'reservations': select_all_reservations_with_previous_reservation()})
