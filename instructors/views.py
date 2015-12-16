from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.http import Http404
from .models import Instructor, Appointment, Announcement
from courses.models import Grade, GradeColumn
from .forms import GradeColumnEditForm, AppointmentForm, AnnouncementForm


# Create your views here.

@login_required
def instructor_view(request, pk=None):

    if request.user.is_instructor() == False:
        raise Http404

    if pk:
        obj = get_object_or_404(Instructor, pk=pk)
    else:
        obj = get_object_or_404(Instructor, pk=request.user.pk)
    return render(
        request,
        'instructor_profile.html',
        {
            'instructor': obj,
            'announcements': obj.announcement_set.all(),
        })


class InstructorCreate(CreateView):
    model = Instructor
    fields = '__all__'
    template_name = 'instructor_create_profile.html'


class InstructorEditProfile(UpdateView):
    model = Instructor
    fields = ['phone', 'email', 'office_hours', 'twitter_id', ]
    template_name = 'instructor_profile_edit.html'
    context_object_name = "instructor"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_instructor() == False:
            raise Http404
        else:
            return super(InstructorEditProfile, self).dispatch(*args, **kwargs)




def appointment_create(request, pk):
    inst = get_object_or_404(Instructor, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(initial={'instructor': inst, })
    return render(
        request,
        'take_appointment.html',
        {
            'instructor': inst,
            'form': form,
        })


def intructor_student_can_view_appoinment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    return render(request,
                  'appointment_details.html',
                  {
                      'appointment': appointment,
                  })


class AppointmentList(ListView):
    model = Appointment
    template_name = "appointment_list.html"
    context_object_name = "appointments"


def create_general_announcment(request, instructor_id):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('instructor_view', kwargs={'pk': instructor_id}))
    else:
        form = AnnouncementForm(initial={'instructor': instructor_id, })
    return render(
        request,
        'create_general_announcment.html',
        {
            'form': form,
            'instructor_id': instructor_id,
        })


class AppointmentEdit(UpdateView):
    model = Appointment
    template_name = 'appointment_edit.html'
    context_object_name = 'appointment'
    fields = ('name', 'date_time', 'reason', 'email', 'twitter_id', 'phone')


def appointment_view(request, pk):
    inst = get_object_or_404(Instructor, pk=pk)
    appoint = Appointment.objects.filter()
    return render(
        request,
        'appointment_list.html',
        {
            'instructor': inst,
            'appointments': appoint
        })


def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.delete()
    messages.success(request, 'appointment was successfully deleted')
    return redirect(reverse('appointment_list'))


class AnnouncementEdit(UpdateView):
    model = Announcement
    template_name = 'edit_general_announcement.html'
    context_object_name = 'announcement'
    fields = ('name', 'comment')


def appointment_approve(request, pk):
    appo = get_object_or_404(Appointment, pk=pk)
    appo.approved = True
    appo.save()
    messages.success(request, '%s appointment approved' % appo.name)
    return redirect(reverse('appointment_details', kwargs={
        'appointment_id': appo.pk,
    }))


def appointment_decline(request, pk):
    appo = get_object_or_404(Appointment, pk=pk)
    appo.approved = False
    appo.save()
    messages.success(request, '%s appointment declined' % appo.name)
    return redirect(reverse('appointment_details', kwargs={
        'appointment_id': appo.pk,
    }))
