from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from teacher import models as TMODEL


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

from django.shortcuts import get_object_or_404

from django.shortcuts import redirect
from datetime import timedelta
from django.shortcuts import redirect

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user=request.user)

    # Check if the student has already attempted the exam for this course
    if QMODEL.Result.objects.filter(exam=course, student=student).exists():
        # Redirect the student to a page indicating they have already attempted the exam
        return redirect('view-result')

    questions = QMODEL.Question.objects.filter(course=course)

    # Calculate total time required for the exam (1 minute per question)
    total_minutes = len(questions)
    total_seconds = total_minutes * 60
    print(total_minutes,total_seconds)

    if request.method == 'POST':
        pass

    response = render(request, 'student/start_exam.html', {'course': course, 'questions': questions,
                                                           'total_minutes': total_minutes,
                                                           'total_seconds': total_seconds})
    response.set_cookie('course_id', course.id)
    return response


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course = QMODEL.Course.objects.get(id=course_id)
        total_marks = 0

        # Get all questions for the current course
        questions = QMODEL.Question.objects.filter(course=course)

        # Loop through each question to check the submitted answer
        for i, question in enumerate(questions, start=1):
            selected_ans = request.POST.get(str(i))  # Get the selected answer for this question
            actual_answer = question.answer
            if selected_ans == actual_answer:
                total_marks += question.marks

        # Save the total marks to the database
        student = request.user.student
        result = QMODEL.Result.objects.create(
            exam=course,
            student=student,
            marks=total_marks
        )

      

        return HttpResponseRedirect('view-result')



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)

    # Retrieve all results for the given course
    all_results = QMODEL.Result.objects.filter(exam=course)

    # Sort results by marks
    sorted_results = sorted(all_results, key=lambda x: x.marks, reverse=True)

    # Calculate rank positions
    highest_marks = sorted_results[0].marks if sorted_results else 0
    medium_marks = sorted_results[len(sorted_results) // 2].marks if sorted_results else 0
    lowest_marks = sorted_results[-1].marks if sorted_results else 0

    return render(request, 'student/check_marks.html', {
        'results': results,
        'all_results': all_results,
        'highest_marks': highest_marks,
        'medium_marks': medium_marks,
        'lowest_marks': lowest_marks,
        'course': course  # Pass the course object to the template
    })
   # return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def job_list_view(request):
    jobs = QMODEL.Job.objects.all()
    return render(request, 'student/apply_job.html', {'jobs': jobs})



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def apply_job_view(request, pk):
    job = QMODEL.Job.objects.get(id=pk)
    applicant = request.user
    application = QMODEL.JobApplication(job=job, applicant=applicant)
    application.save()
    return redirect('student-dashboard')


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def job_apply_views(request):
    return render(request,'student/student_job.html')


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def my_job_applications_view(request):
    applications = QMODEL.JobApplication.objects.filter(applicant=request.user)
    return render(request, 'student/my_job_applications.html', {'applications': applications})