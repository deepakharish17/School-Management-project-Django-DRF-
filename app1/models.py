from django.db import models
from django.db.models.fields import CharField, DateTimeField


class School(models.Model):
    school_name = models.CharField(max_length=100)

    def __str__(self):
        return self.school_name


class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    reg = models.CharField(max_length=100, unique=True)

    school = models.ForeignKey  (School,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "students"
        ordering = ["name"]


class Marks(models.Model):
    tamil = models.IntegerField()
    english = models.IntegerField()
    maths = models.IntegerField()
    science = models.IntegerField()
    social = models.IntegerField()
    total = models.IntegerField()
    avg = models.IntegerField()
    school = models.ForeignKey(School,on_delete=models.CASCADE)
    student = models.ForeignKey(Student,on_delete=models.CASCADE )
    def __str__(self):
        return f"{self.student.name} Marks"

    class Meta:
        db_table = "marks"

class Decorator(models.Model):
    API_name=CharField(max_length=500)
    API_Method=CharField(max_length=500)
    API_use=CharField(max_length=500)
    Start_time=models.DateTimeField()
    Status=CharField(max_length=500)
    End_time=models.DateTimeField()
    Duration=CharField(max_length=500)

    def __str__(self):
        return self.API_name
    