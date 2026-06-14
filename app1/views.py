import json
from urllib import request, response

from django.db.models import Model
from django.http import JsonResponse, HttpResponse
from openpyxl import workbook

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .decoraters import api_details
from app1.models import School, Student, Marks
import pandas as pd


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the app index page.")

@csrf_exempt
def add_school(request):

    if request.method == "POST":

        data = json.loads(request.body)

        try:
            school, created = School.objects.get_or_create(
                school_name=data['name']
            )
            return JsonResponse({
                "id": school.id,
                "school_name": school.school_name,
                "created": created
            })
        except Exception as e:
            return JsonResponse({
                "error": str(e)
            }, status=400)

    return JsonResponse({
        "error": "Invalid request method"
    })

@csrf_exempt
def add_student(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            try:
                reg_no=Student.objects.get(
                    reg=data["reg"]
                )
            except Student.DoesNotExist:
                school = School.objects.get(id=data["school_id"])
                student = Student.objects.create(
                    name=data['name'],
                    age=data['age'],
                    reg=data['reg'],
                    school=school
                )
                return JsonResponse({
                    'id': student.id,
                    'name': student.name,
                    'age': student.age,
                    'reg': student.reg,
                    'school': student.school.school_name
                })
        except School.DoesNotExist:
            return JsonResponse({"error": "School does not exist"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({
        'error': 'Only POST allowed'
    }, status=405)

@csrf_exempt
def add_mark(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            student=Student.objects.get(id=data["std_id"])
            school = School.objects.get(id=data["school_id"])
            if Marks.objects.filter(student=student).exists():
                return JsonResponse({
                    "message": "Marks already exist",
                    "error": "Marks already entered for this student"
                }, status=400)
            Marks.objects.create(
                student=student,
                school=school,
                tamil=data['tamil'],
                english=data['english'],
                maths=data['maths'],
                science=data['science'],
                social=data['social'],
                total=data['tamil']+data['english']+data['maths']+data['science']+data['social'],
                avg=(data['tamil']+data['english']+data['maths']+data['science']+data['social'])/5
            )
            return JsonResponse({'message': 'Marks added successfully'})
        except Student.DoesNotExist:
            return JsonResponse({"error": "Student does not exist"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({
        'error': 'Only POST allowed'
    })


def get_by_reg(request):

    reg = request.GET.get("reg")
    if not reg:
        return JsonResponse(
            {"error": "reg parameter is required"},
            status=400
        )
    try:
        student = Student.objects.get(
            reg=reg
        )
        mark = Marks.objects.get(
            student=student
        )
        data = {
            "id": student.id,
            "name": student.name,
            "reg": student.reg,
            "total": mark.total,
            "avg": mark.avg,
            "school": student.school.school_name
        }

        return JsonResponse(data)
    except Student.DoesNotExist:
        return JsonResponse( {"error": "Student does not exist"},status=404)
    except Marks.DoesNotExist:
        return JsonResponse({"error": "Marks not found for this student"},status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)},status=400)


@csrf_exempt
@api_details("Creating new datas for all tables")
def add_all(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            school, _ = School.objects.get_or_create( school_name=data['school_name'])
            student, _ = Student.objects.get_or_create(reg=data['reg'],
                defaults={
                    "name": data['name'],
                    "age": data['age'],
                    "school": school
                })
            if Marks.objects.filter(student=student).exists():
                return JsonResponse({"error": "Marks already entered for this student"}, status=400)
            total = (data['tamil'] +data['english'] +data['maths'] +data['science'] +data['social'])
            avg = total / 5
            mark = Marks.objects.create(
                student=student,
                school=school,
                tamil=data['tamil'],
                english=data['english'],
                maths=data['maths'],
                science=data['science'],
                social=data['social'],
                total=total,
                avg=avg
            )
            return JsonResponse({
                "message": "Data added successfully",
                "school_id": school.id,
                "student_id": student.id,
                "mark_id": mark.id
            })
        except Exception as e:
               return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

@csrf_exempt
def update_by_id(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        student_id = data.get("id")
        if not student_id:
            return JsonResponse({"error": "student_id is required"}, status=400)
        try:
            std=Student.objects.get(id=student_id)
            std.name = data["name"]
            std.age = data["age"]
            std.save()
            return JsonResponse({"message": "Student updated successfully"})
        except Student.DoesNotExist:
            return JsonResponse({"error": "Student not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only PUT allowed"}, status=405)

@csrf_exempt
def delete_by_reg(request):
    if request.method == "DELETE":
        reg = request.GET.get("reg")
        if not reg:
            return JsonResponse({"error": "reg is required"}, status=400)
        try:
            student = Student.objects.get(reg=reg).delete()
            return JsonResponse({"message": "Student deleted successfully","reg":reg})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only DELETE allowed"}, status=405)

@csrf_exempt
def update_by_excel(request):

    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            return JsonResponse({
                "error": "No file uploaded"
            }, status=400)
        try:
            df = pd.read_excel(file)
            success_count = 0
            failed_rows = []
            for index, row in df.iterrows():
                Error = []
                try:
                    school = School.objects.get(
                        id=row["school_id"]
                    )
                    name = row["name"]
                    Age = row["age"]
                    reg = row["reg"]
                    tamil = row["tamil"]
                    english = row["english"]
                    maths = row["maths"]
                    science = row["science"]
                    social = row["social"]
                    total = (tamil +english +maths +science +social)
                    avg = total / 5
                    if pd.isna(name):
                        Error.append("Name is not valid")
                    if pd.isna(reg):
                        Error.append("Reg is not valid")
                    try:
                        Age = int(Age)
                        if Age < 0 or Age > 100:
                            Error.append("Age is not valid")
                    except:
                        Error.append("Age is not valid")
                    try:
                        tamil = float(tamil)
                        if tamil < 0 or tamil > 100:
                            Error.append("Tamil mark is not valid")
                    except:
                        Error.append("Tamil mark is not valid")
                    try:
                        english = float(english)
                        if english < 0 or english > 100:
                            Error.append("English mark is not valid")
                    except:
                        Error.append("English mark is not valid")
                    try:
                        maths = float(maths)
                        if maths < 0 or maths > 100:
                            Error.append("Maths mark is not valid")
                    except:
                        Error.append("Maths mark is not valid")
                    try:
                        science = float(science)
                        if science < 0 or science > 100:
                            Error.append("Science mark is not valid")
                    except:
                        Error.append("Science mark is not valid")
                    try:
                        social = float(social)
                        if social < 0 or social > 100:
                            Error.append("Social mark is not valid")
                    except:
                        Error.append("Social mark is not valid")
                    if Student.objects.filter(reg=reg).exists():
                        failed_rows.append({
                            "row": index + 2,
                            "error": "Student already exists"
                        })
                        continue
                    if len(Error) == 0:
                        student = Student.objects.create(
                            name=name,
                            age=Age,
                            reg=reg,
                            school=school
                        )
                        Marks.objects.create(
                            student=student,
                            school=school,
                            tamil=tamil,
                            english=english,
                            maths=maths,
                            science=science,
                            social=social,
                            total=total,
                            avg=avg
                        )
                        success_count += 1

                    else:

                        failed_rows.append({
                            "row": index + 2,
                            "error": Error
                        })
                except School.DoesNotExist:
                    failed_rows.append({ "row": index + 2, "error": "School does not exist"})
                except Exception as e:
                    failed_rows.append({"row": index + 2,"error": str(e)})
            return JsonResponse({
                "message": "Excel processed",
                "success_count": success_count,
                "failed_count": len(failed_rows),
                "failed_rows": failed_rows
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)




def export_by_excel(request):
    if request.method == "GET":
        members = Marks.objects.all().order_by(
            "student__reg"
        ).values(
            "student__id",
            "student__name",
            "student__age",
            "student__reg",
            "school__school_name",
            "tamil",
            "english",
            "maths",
            "science",
            "social",
            "total",
            "avg"
        )
        df = pd.DataFrame(members)
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = ("attachment; filename=students_Mark.xlsx")
        df.to_excel(response,index=False,sheet_name="Students")
        print("File exported")
        return response
    return JsonResponse({"error": "Only GET allowed"}, status=405)













