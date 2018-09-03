import calendar

from django.db import models

DAYS_OF_WEEK = [(day, day) for day in calendar.day_name]


class AbstractEntity(models.Model):
    create_ts = models.DateTimeField(auto_now_add=True)
    update_ts = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('create_ts',)


class Shop(AbstractEntity):
    owner = models.ForeignKey('auth.User', related_name='shops', on_delete=models.CASCADE)
    title = models.CharField(max_length=127, blank=False)

    class Meta:
        db_table = 'dh_shop'


class Schedule(AbstractEntity):
    day_of_week = models.CharField(choices=DAYS_OF_WEEK, max_length=16)
    shop = models.ForeignKey('Shop', related_name='schedules', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dh_schedule'


class TimeRange(AbstractEntity):
    from_t = models.TimeField(null=False)
    to_t = models.TimeField(null=False)

    is_open = models.BooleanField()
    reason = models.CharField(max_length=127, blank=True)

    schedule = models.ForeignKey('Schedule', related_name='time_ranges', on_delete=models.CASCADE)

    class Meta:
        db_table = 'dh_time_range'
