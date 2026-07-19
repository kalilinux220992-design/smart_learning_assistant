from django.db import models


class Student(models.Model):
    STATUS_PLACED = "placed"
    STATUS_IN_PROGRESS = "in-progress"
    STATUS_NOT_PLACED = "not-placed"

    STATUS_CHOICES = [
        (STATUS_PLACED, "Placed"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_NOT_PLACED, "Not Placed"),
    ]

    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=50)
    year = models.PositiveSmallIntegerField()
    company_name = models.CharField(max_length=120, blank=True, default="")
    package_lpa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
