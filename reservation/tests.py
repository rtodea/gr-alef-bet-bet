from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase
from django.db.utils import IntegrityError
from .models import Rental, Reservation
from reservation.selectors import select_all_reservations_with_previous_reservation
from tabulate import tabulate


class RentalModelTest(TestCase):

    def test_string_representation(self):
        rental = Rental(name='A nice place')
        self.assertEqual(str(rental), rental.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Rental._meta.verbose_name_plural), 'rentals')


class ReservationModelTest(TransactionTestCase):

    def test_string_representation(self):
        rental = Rental(name='A nice place')
        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-02')
        self.assertEqual(str(reservation),
                         f'{reservation.rental.name} ({reservation.check_in} - {reservation.check_out})')

    def test_verbose_name_plural(self):
        self.assertEqual(str(Reservation._meta.verbose_name_plural), 'reservations')

    def test_cannot_create_reservation_with_check_in_after_check_out(self):
        rental = Rental(name='A nice place')
        reservation = Reservation(rental=rental, check_in='2021-01-02', check_out='2021-01-01')

        with self.assertRaises(ValueError):
            reservation.save()

        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_cannot_create_reservation_with_check_in_equal_check_out(self):
        rental = Rental(name='A nice place')
        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-01')

        with self.assertRaises(ValueError):
            reservation.save()

        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_cannot_update_check_in_to_after_check_out(self):
        rental = Rental(name='A nice place')
        rental.save()
        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-02')
        reservation.save()

        reservation.check_in = '2021-01-03'

        with self.assertRaises(IntegrityError):
            reservation.save()

        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_cannot_create_reservation_if_other_reservation_exists(self):
        rental = Rental(name='A nice place')
        rental.save()
        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-02')
        reservation.save()

        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-02')

        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_cannot_create_reservation_overlapping_existing_reservation(self):
        rental = Rental(name='A nice place')
        rental.save()
        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-02')
        reservation.save()

        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-03')

        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_cannot_create_reservation_within_other_reservation(self):
        rental = Rental(name='A nice place')
        rental.save()
        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-04')
        reservation.save()

        reservation = Reservation(rental=rental, check_in='2021-01-02', check_out='2021-01-03')

        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_can_update_same_reservation_with_different_dates(self):
        rental = Rental(name='A nice place')
        rental.save()
        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-04')
        reservation.save()

        reservation.check_in = '2021-01-02'
        reservation.check_out = '2021-01-03'

        reservation.full_clean()
        reservation.save()

        reservation.refresh_from_db(fields=['check_in', 'check_out'])
        self.assertEqual(str(reservation.check_in), '2021-01-02')
        self.assertEqual(str(reservation.check_out), '2021-01-03')


class SelectingReservationsWithPreviousReservationRefTest(TestCase):
    @staticmethod
    def export_reservations_as_pretty_table(reservations):
        headers = ['Rental_name', 'ID', 'Checkin', 'Checkout', 'Previous reservation ID']

        def format_reservation_id(reservation_id):
            if reservation_id is None:
                return '-'
            return f'Res-{reservation_id} ID'

        rows = [(r.rental_name,
                 format_reservation_id(r.id),
                 r.check_in,
                 r.check_out,
                 format_reservation_id(getattr(r, 'previous_reservation_id', None))) for r in reservations]
        return tabulate(rows, headers=headers, tablefmt='psql')

    def test_select_all_reservations_with_previous_reservation(self):
        rental1 = Rental(name='Rental-1')
        rental1.save()
        reservation1 = Reservation(rental=rental1, check_in='2021-01-01', check_out='2021-01-13')
        reservation1.save()
        reservation2 = Reservation(rental=rental1, check_in='2021-01-20', check_out='2021-02-10')
        reservation2.save()
        reservation3 = Reservation(rental=rental1, check_in='2021-02-20', check_out='2021-03-10')
        reservation3.save()

        rental2 = Rental(name='Rental-2')
        rental2.save()
        reservation4 = Reservation(rental=rental2, check_in='2021-01-01', check_out='2021-01-13')
        reservation4.save()
        reservation5 = Reservation(rental=rental2, check_in='2021-01-20', check_out='2021-02-10')
        reservation5.save()

        reservations = select_all_reservations_with_previous_reservation()

        self.assertEqual('''
+---------------+----------+------------+------------+---------------------------+
| Rental_name   | ID       | Checkin    | Checkout   | Previous reservation ID   |
|---------------+----------+------------+------------+---------------------------|
| Rental-1      | Res-1 ID | 2021-01-01 | 2021-01-13 | -                         |
| Rental-1      | Res-2 ID | 2021-01-20 | 2021-02-10 | -                         |
| Rental-1      | Res-3 ID | 2021-02-20 | 2021-03-10 | -                         |
| Rental-2      | Res-4 ID | 2021-01-01 | 2021-01-13 | -                         |
| Rental-2      | Res-5 ID | 2021-01-20 | 2021-02-10 | -                         |
+---------------+----------+------------+------------+---------------------------+
''', f'\n{self.export_reservations_as_pretty_table(reservations)}\n')
