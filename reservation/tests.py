from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import Rental, Reservation


class RentalModelTest(TestCase):

    def test_string_representation(self):
        rental = Rental(name='A nice place')
        self.assertEqual(str(rental), rental.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Rental._meta.verbose_name_plural), 'rentals')


class ReservationModelTest(TestCase):

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

        with self.assertRaises(ValueError):
            reservation.save()

        with self.assertRaises(ValidationError):
            reservation.full_clean()
