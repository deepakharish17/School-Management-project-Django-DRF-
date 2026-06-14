from django.urls import path
from app1 import views
# from django.http import HttpResponse


urlpatterns = [
    path('', views.index, name='index'),
    path('add_school',views.add_school,name='add_school'),
    path('add_student',views.add_student,name='add_student'),
    path('add_mark',views.add_mark,name='add_mark'),
    path('get_by_reg/',views.get_by_reg,name='get_by_reg'),
    path('add_all/',views.add_all,name='add_all'),
    path('update_by_id/',views.update_by_id,name='update_by_id'),
    path('delete_by_reg/',views.delete_by_reg,name='delete_by_reg'),
    path('update_by_excel/',views.update_by_excel,name='update_by_excel'),
    path('export_by_excel/',views.export_by_excel,name='update_by_excel'),

]