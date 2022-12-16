from django.db import models


# Create your models here.
class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Rental(TimeStampMixin):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Reservation(TimeStampMixin):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f'{self.rental.name} ({self.check_in} - {self.check_out})'
