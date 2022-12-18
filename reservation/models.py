from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Rental(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Reservation(BaseModel):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()

    def _validate_no_overlapping_reservations_within_same_rental(self):
        if Reservation.objects.filter(
                rental=self.rental,
                check_in__lt=self.check_out,
                check_out__gt=self.check_in
        ).exclude(id=self.id).exists():
            raise ValidationError('Overlapping reservation')

    def clean(self):
        self._validate_no_overlapping_reservations_within_same_rental()

    def __str__(self):
        return f'{self.rental.name} ({self.check_in} - {self.check_out})'

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='check_in_before_check_out',
                check=Q(check_in__lt=F('check_out'))
            )
        ]
