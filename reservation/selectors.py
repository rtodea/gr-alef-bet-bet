from django.db.models import Window, F
from django.db.models.functions import Lag

from reservation.models import Reservation


def select_all_reservations_with_previous_reservation():
    # use Lag window function to get previous reservation id
    # https://docs.djangoproject.com/en/4.1/ref/models/database-functions/#lag
    #
    # Supported by Sqlite and Postgres:
    #
    # 1. https://www.sqlitetutorial.net/sqlite-window-functions/sqlite-lag/
    # 2. https://www.postgresql.org/docs/9.1/tutorial-window.html

    return Reservation.objects.annotate(
        prev_reservation_id=Window(
            expression=Lag('id'),
            order_by=F('check_in').asc(),
            partition_by=F('rental'),
        )
    ).values_list(
        'rental__name',
        'id',
        'check_in',
        'check_out',
        'prev_reservation_id',
    ).order_by(
        'rental__name',
        'check_in',
    ).all()
