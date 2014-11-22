# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from programs import forms
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from account.models import UserProfile
from programs.models import BaseExercise, Program, Week, DayProgram
import datetime
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView, View
from django.views.generic.base import TemplateView
from BO import WeekService
from viewmodels import MyProgramsViewModel, ShowDayViewModel
from django.template.base import kwarg_re
from django.utils.decorators import method_decorator

weekService = WeekService()
def get_user(request):
    return UserProfile.objects.get(user=request.user)

@login_required
def new_program(request):
    view = 'Programs/new_program.html'
    context = RequestContext(request)
    dictonary = {}
    if request.method == 'GET':
        return render_to_response(view, dictonary, context)
    else:
        program = Program()
        program.user = UserProfile.objects.get(user=request.user)
        program.name = request.POST.get('name', False)
        program.date = datetime.datetime.now()
        number_of_weeks = request.POST.get('weeks', False)
        try:
            int(number_of_weeks)
        except:
            dictonary['error'] = 'Antall uker må være et nummer'
            return render_to_response(view, dictonary, context)
        if not program.name:
            dictonary['error'] = 'Navn må fylles inn'
            return render_to_response(view, dictonary, context)
        elif not number_of_weeks:
            dictonary['error'] = 'Antall uker må fylles inn'
            return render_to_response(view, dictonary, context)
        else:            
            program.save()
            for i in range(int(number_of_weeks)):
                week = Week()
                
                week.program = program
                week.name = 'Uke %s' % (i + 1)
                week.save()
            return redirect('/programs/add_week/%d' % program.id)


@login_required
def index(request):
    view = 'Programs/index.html'
    context = RequestContext(request)
    dictionary = {}
    if request.method == 'GET':
        dictionary['programs'] = Program.objects.filter(user=get_user(request))
        programs = []
        for program in dictionary["programs"]:
            programs.append(MyProgramsViewModel(program.id))
        dictionary['program_list'] = programs
        print len(dictionary['program_list'])
        return render_to_response(view, dictionary, context)

@login_required
def create_exercise(request):
    view = 'Programs/create_exercise.html'
    context = RequestContext(request)
    dictionary = {}
    dictionary['form'] = forms.ExcersiceForm()
    if request.method == 'GET':
        return render_to_response(view, dictionary, context)
    elif request.method == 'POST':
        excercise_form = forms.ExcersiceForm(data=request.POST)
        #excercise_form.user = UserProfile.objects.get(user=request.user)
        dictionary['form'] = excercise_form
        if excercise_form.is_valid():
            excercise = excercise_form.save(commit=False)
            excercise.user = UserProfile.objects.get(user=request.user)
            try:
                excercise.save()
            except:
                dictionary['error'] = "Ovelsen eksisterer allerede"
                return  render_to_response(view, dictionary,context)
            add_another = request.POST.get('other', False)
            if add_another:
                return render_to_response(view, {'form' : forms.ExcersiceForm()}, context)
            else:
                return redirect('/programs/')
        else:

            return render_to_response(view, dictionary,context)
        return  render_to_response(view, dictionary,context)

@login_required
def show_excercises(request):
    view = 'Programs/show_excercises.html'
    context = RequestContext(request)
    dictionary = {}
    excercises = BaseExercise.objects.filter(user=get_user(request)).order_by('muscle_group')#.all()
    dictionary['excercises'] = excercises
    return render_to_response(view, dictionary, context)


class ProgramWeeks(TemplateView):
    template_name = 'Programs/program_week.html'
    
    @method_decorator(login_required(login_url='account/login/'))
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        context = {'program' : Program.objects.get(pk=kwargs['program_id']),
                   'weeks' : Week.objects.filter(program_id=kwargs['program_id'])
                   }
        return render(request, self.template_name, context)
   


class AddDayProgram(TemplateView):
    template_name = 'Programs/add_day.html'
    
    @method_decorator(login_required)
    def get(self,request, *args, **kwargs):    
        return render(request, self.template_name, {'week' : kwargs['week_id']})
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        day = DayProgram(name=request.POST["name"], week = Week.objects.get(pk=kwargs['week_id']))
        day.save()
        return redirect('/programs/')

    
class AddExerciseToDay(FormView):
    template_name = 'Programs/add_exercise_to_day.html'
    form_class = forms.DayExerciseForm
    success_url = '/programs/'
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        print "get"
        day_id = kwargs['day_id']
        """form = self.form_class(
                initial={'day_program' : day_id}
            )"""
        print "return"
        return render(request, self.template_name, self.get_dictonary(day_id))
            
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        day_id = kwargs['day_id']
        another = request.POST.get('anohter', False)        
        if form.is_valid():            
            form = form.save(commit=True)
            if another:
                return redirect('/programs/add_exercise_to_day/%s' % day_id)
            return redirect(self.success_url)
        else:
            print "form not valid"
            return render(request, self.template_name, {'form' : form})
        return render(request, self.template_name, {'form' : form})


    def get_dictonary(self, day_id):
        form = self.form_class(
                initial={'day_program' : day_id}
            )
        return {'form' : form}

class ShowDayPartialView(TemplateView):
    template_name = 'Programs/show_day.html'
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        day_id = kwargs['day_id']
        model = ShowDayViewModel(day_id)
        
        return render(request, self.template_name, {'model' : model})
        
    
        
        
        
        
        

    