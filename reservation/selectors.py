from typing import Optional
from reservation.models import Reservation
from dataclasses import dataclass


@dataclass
class ReservationWithPrev:
    rental_name: str
    id: str
    check_in: str
    check_out: str
    prev_reservation_id: Optional[int]


def select_all_reservations_with_previous_reservation():
    return [ReservationWithPrev(r.rental.name,
                                r.id,
                                r.check_in,
                                r.check_out,
                                None) for r in Reservation.objects.all()]
