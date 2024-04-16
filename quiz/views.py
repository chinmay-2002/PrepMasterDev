from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from teacher import models as TMODEL
from student import models as SMODEL
from teacher import forms as TFORM
from student import forms as SFORM
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseNotFound
from django.urls import reverse



def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'quiz/index.html')


def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def afterlogin_view(request):
    if is_student(request.user):      
        return redirect('student/student-dashboard')
                
    elif is_teacher(request.user):
        accountapproval=TMODEL.Teacher.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('teacher/teacher-dashboard')
        else:
            return render(request,'teacher/teacher_wait_for_approval.html')
    else:
        return redirect('admin-dashboard')



def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
    'total_student':SMODEL.Student.objects.all().count(),
    'total_teacher':TMODEL.Teacher.objects.all().filter(status=True).count(),
    'total_course':models.Course.objects.all().count(),
    'total_question':models.Question.objects.all().count(),
    }
    return render(request,'quiz/admin_dashboard.html',context=dict)

@login_required(login_url='adminlogin')
def admin_teacher_view(request):
    dict={
    'total_teacher':TMODEL.Teacher.objects.all().filter(status=True).count(),
    'pending_teacher':TMODEL.Teacher.objects.all().filter(status=False).count(),
    'salary':TMODEL.Teacher.objects.all().filter(status=True).aggregate(Sum('salary'))['salary__sum'],
    }
    return render(request,'quiz/admin_teacher.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_teacher_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=True)
    return render(request,'quiz/admin_view_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def update_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=TMODEL.User.objects.get(id=teacher.user_id)
    userForm=TFORM.TeacherUserForm(instance=user)
    teacherForm=TFORM.TeacherForm(request.FILES,instance=teacher)
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=TFORM.TeacherUserForm(request.POST,instance=user)
        teacherForm=TFORM.TeacherForm(request.POST,request.FILES,instance=teacher)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacherForm.save()
            return redirect('admin-view-teacher')
    return render(request,'quiz/update_teacher.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-teacher')




@login_required(login_url='adminlogin')
def admin_view_pending_teacher_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=False)
    return render(request,'quiz/admin_view_pending_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def approve_teacher_view(request,pk):
    teacherSalary=forms.TeacherSalaryForm()
    if request.method=='POST':
        teacherSalary=forms.TeacherSalaryForm(request.POST)
        if teacherSalary.is_valid():
            teacher=TMODEL.Teacher.objects.get(id=pk)
            teacher.salary=teacherSalary.cleaned_data['salary']
            teacher.status=True
            teacher.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-pending-teacher')
    return render(request,'quiz/salary_form.html',{'teacherSalary':teacherSalary})

@login_required(login_url='adminlogin')
def reject_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-pending-teacher')

@login_required(login_url='adminlogin')
def admin_view_teacher_salary_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=True)
    return render(request,'quiz/admin_view_teacher_salary.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def admin_student_view(request):
    dict={
    'total_student':SMODEL.Student.objects.all().count(),
    }
    return render(request,'quiz/admin_student.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'quiz/admin_view_student.html',{'students':students})



@login_required(login_url='adminlogin')
def update_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=SMODEL.User.objects.get(id=student.user_id)
    userForm=SFORM.StudentUserForm(instance=user)
    studentForm=SFORM.StudentForm(request.FILES,instance=student)
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=SFORM.StudentUserForm(request.POST,instance=user)
        studentForm=SFORM.StudentForm(request.POST,request.FILES,instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            studentForm.save()
            return redirect('admin-view-student')
    return render(request,'quiz/update_student.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect('/admin-view-student')


@login_required(login_url='adminlogin')
def admin_course_view(request):
    return render(request,'quiz/admin_course.html')


@login_required(login_url='adminlogin')
def admin_add_course_view(request):
    courseForm=forms.CourseForm()
    if request.method=='POST':
        courseForm=forms.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-course')
    return render(request,'quiz/admin_add_course.html',{'courseForm':courseForm})


@login_required(login_url='adminlogin')
def admin_view_course_view(request):
    courses = models.Course.objects.all()
    return render(request,'quiz/admin_view_course.html',{'courses':courses})

@login_required(login_url='adminlogin')
def delete_course_view(request,pk):
    course=models.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/admin-view-course')



@login_required(login_url='adminlogin')
def admin_question_view(request):
    return render(request,'quiz/admin_question.html')


@login_required(login_url='adminlogin')
def admin_add_question_view(request):
    questionForm=forms.QuestionForm()
    if request.method=='POST':
        questionForm=forms.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=models.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        else:
            print("form is invalid")
        #return HttpResponseRedirect('/quiz/')
    return render(request,'quiz/admin_add_question.html',{'questionForm':questionForm})


@login_required(login_url='adminlogin')
def admin_view_question_view(request):
    courses= models.Course.objects.all()
    return render(request,'quiz/admin_view_question.html',{'courses':courses})

@login_required(login_url='adminlogin')
def view_question_view(request,pk):
    questions=models.Question.objects.all().filter(course_id=pk)
    return render(request,'quiz/view_question.html',{'questions':questions})

@login_required(login_url='adminlogin')
def delete_question_view(request,pk):
    question=models.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/admin-view-question')

@login_required(login_url='adminlogin')
def admin_view_student_marks_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'quiz/admin_view_student_marks.html',{'students':students})

@login_required(login_url='adminlogin')
def admin_view_marks_view(request,pk):
    courses = models.Course.objects.all()
    response =  render(request,'quiz/admin_view_marks.html',{'courses':courses})
    response.set_cookie('student_id',str(pk))
    return response

@login_required(login_url='adminlogin')
def admin_check_marks_view(request, pk):
    course = models.Course.objects.get(id=pk)
    student_id = request.COOKIES.get('student_id')
    student = SMODEL.Student.objects.get(id=student_id)

    results = models.Result.objects.filter(exam=course, student=student)

    # Retrieve all results for the given course
    all_results = models.Result.objects.filter(exam=course)

    # Sort results by marks
    sorted_results = sorted(all_results, key=lambda x: x.marks, reverse=True)

    # Calculate rank positions
    highest_marks = sorted_results[0].marks if sorted_results else 0
    medium_marks = sorted_results[len(sorted_results) // 2].marks if sorted_results else 0
    lowest_marks = sorted_results[-1].marks if sorted_results else 0

    return render(request, 'quiz/admin_check_marks.html', {
        'results': results,
        'all_results':all_results,
        'highest_marks': highest_marks,
        'medium_marks': medium_marks,
        'lowest_marks': lowest_marks,
        'course': course  # Pass the course object to the template
    })




def aboutus_view(request):
    return render(request,'quiz/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'quiz/contactussuccess.html')
    return render(request, 'quiz/contactus.html', {'form':sub})

from django.db.models import Avg

@login_required(login_url='adminlogin')
def admin_rank_board_view(request):
    all_results = models.Result.objects.all()

    # Group results by student
    results_by_student = {}
    for result in all_results:
        if result.student.id not in results_by_student:
            results_by_student[result.student.id] = {
                'student': result.student,
                'marks_list': [],
            }
        results_by_student[result.student.id]['marks_list'].append(result.marks)

    # Calculate average marks for each student
    for student_id, data in results_by_student.items():
        data['average_marks'] = sum(data['marks_list']) / len(data['marks_list'])

    # Sort students based on their average marks
    sorted_students = sorted(results_by_student.values(), key=lambda x: x['average_marks'], reverse=True)

    return render(request, 'quiz/admin_rank_board.html', {
        'sorted_students': sorted_students
    })



def rank_board_view(request):
    all_results = models.Result.objects.all()

    # Group results by student
    results_by_student = {}
    for result in all_results:
        if result.student.id not in results_by_student:
            results_by_student[result.student.id] = {
                'student': result.student,
                'marks_list': [],
            }
        results_by_student[result.student.id]['marks_list'].append(result.marks)

    # Calculate average marks for each student
    for student_id, data in results_by_student.items():
        data['average_marks'] = sum(data['marks_list']) / len(data['marks_list'])

    # Sort students based on their average marks
    sorted_students = sorted(results_by_student.values(), key=lambda x: x['average_marks'], reverse=True)

    return render(request, 'quiz/rank_board.html', {
        'sorted_students': sorted_students
    })



from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm



@login_required(login_url='adminlogin')
def admin_job(request):
    return render(request,'quiz/admin_job.html')

def upload_job_view(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user  # Assign the currently logged-in user
            job.save()
            return redirect('job_list')
    else:
        form = JobForm()
    return render(request, 'quiz/upload_job.html', {'form': form})

def job_list_view(request):
    jobs = Job.objects.all()
    return render(request, 'quiz/job_list.html', {'jobs': jobs})



def update_job_view(request, pk):
    job = Job.objects.get(id=pk)
    jobForm = JobForm(instance=job)
    if request.method == 'POST':
        jobForm = JobForm(request.POST, instance=job)
        if jobForm.is_valid():
            jobForm.save()
            return redirect('job_list')  # Redirect to the job list page after updating
    return render(request, 'quiz/update_job.html', {'jobForm': jobForm})



def delete_job_view(request, pk):
    # Assuming you have a Job model and you want to delete an instance with the given pk
    try:
        job = Job.objects.get(pk=pk)
        job.delete()
        # Redirect to a success URL after deletion
        return HttpResponseRedirect(reverse('job_list'))
    except Job.DoesNotExist:
        # Handle case where the job instance does not exist
        return HttpResponseNotFound("The job you are trying to delete does not exist.")

def job_applications_view(request):
    applications = JobApplication.objects.all()
    return render(request, 'quiz/job_applications.html', {'applications': applications})

def manage_application_view(request, application_id):
    application = JobApplication.objects.get(id=application_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        application.status = new_status
        application.save()
        return redirect('job_applications')
    return render(request, 'quiz/manage_application.html', {'application': application})
# @login_required
# def apply_job_view(request, job_id):
#     job = Job.objects.get(pk=job_id)
#     if request.method == 'POST':
#         form = JobApplicationForm(request.POST)
#         if form.is_valid():
#             application = form.save(commit=False)
#             application.job = job
#             application.applicant = request.user
#             application.save()
#             return redirect('job_list')
#     else:
#         form = JobApplicationForm()
#     return render(request, 'quiz/apply_job.html', {'form': form, 'job': job})