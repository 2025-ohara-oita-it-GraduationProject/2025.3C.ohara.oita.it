from django.db import models

class MeetingRoom(models.Model):
    name = models.CharField('会議室名', max_length=100)
    def __str__(self):
        return self.name

class Booking(models.Model):
    room = models.ForeignKey(MeetingRoom, verbose_name='会議室', on_delete=models.CASCADE)
    start_time = models.DateTimeField('開始時間')
    end_time = models.DateTimeField('終了時間')
    booker_name = models.CharField('予約者名', max_length=100)
    def __str__(self):
        return f'{self.room} : {self.start_time} - {self.end_time} ({self.booker_name})'