from django.test import TestCase
from .models import Rental, Reservation


class RentalModelTest(TestCase):

    def test_string_representation(self):
        rental = Rental(name='My rental')
        self.assertEqual(str(rental), rental.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Rental._meta.verbose_name_plural), 'rentals')


class ReservationModelTest(TestCase):

    def test_string_representation(self):
        rental = Rental(name='My rental')
        reservation = Reservation(rental=rental, check_in='2021-01-01', check_out='2021-01-02')
        self.assertEqual(str(reservation), f'{reservation.rental.name} ({reservation.check_in} - {reservation.check_out})')

    def test_verbose_name_plural(self):
        self.assertEqual(str(Reservation._meta.verbose_name_plural), 'reservations')
