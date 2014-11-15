from django.db import models

import programs.models as program_models
from django.utils.datetime_safe import strftime
# Create your models here.

class DayRegister(models.Model):
    day_program = models.ForeignKey(program_models.DayProgram)
    start_time = models.DateTimeField()
    end_time = models.DateField(null=True)

    

class ExcerciseRegister(models.Model):
    day_excersice = models.ForeignKey(program_models.DayExcersice)
    day_register = models.ForeignKey(DayRegister)
    set_number = models.IntegerField()
    reps = models.IntegerField()
    weight = models.TextField(max_length=128)
    note = models.TextField(max_length=128, blank=True)