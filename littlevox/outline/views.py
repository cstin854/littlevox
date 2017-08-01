from django.shortcuts import render
from django.http import HttpResponse
from .models import Word, Child
from django.contrib.auth.models import User
from django.views.generic import View
from . forms import UserForm, UserLogin
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login

# Create your views here.

# TODO: Clearly this needs to be cleaned up!
def index(request):
    return HttpResponse("<h1>Hello world!</h1>")

# TODO: This is just a temp view to show all word objects.
def word_test(request):
    html = ''
    words = Word.objects.all()
    for word in words:
        html += '<br><h1>Word: '+ str(word.word) +'</h1>'
        html += '<br><h3>Date: ' + str(word.date) + '</h3>'
        html += '<br>Etymology: ' + str(word.etymology)
    return HttpResponse(html)

# TODO: get_object_or_404 with user
# this view is just used for testing permissions stuff.
# Can eventually be deleted.
def user_junk(request, user, child=None, word=None):
    html = ''
    for dude in User.objects.all():
        html+= '<br><h1>'+str(dude)+'</h1>'
        if dude.viewer_set.all():
            html += '<br>Restricted profile!'
            html += ' Can '+str(user)+' access? '
            for viewer in dude.viewer_set.all():
                html += str(user in str(viewer.viewer))
        else:
            html += 'Unrestricted profile!'
    return HttpResponse(html+'<br><br><h1>User accessing content: '+str(user)+'</h1>')


class UserFormView(View):
    form_class = UserForm
    template_name = 'outline/registration_form.html'

    # Displays a blank form for a user that isn't signed up
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # Process form data:
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # normalized data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # returns User object if credentials are valid
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('outline:index')

        return render(request, self.template_name, {'form':form, 'error_message':self.get_errors(form)})

    def get_errors(self, form):
        message = ''
        for key, value in form.errors.items():
            message += value
        return message


def register_test(request):

    if request.POST:
        return render(request, 'outline/post_test.html', {'error_message':'This is only a test!'})

    else:
        return render(request, 'outline/registration_form_02.html')
