from django.shortcuts import render
from django.http import HttpResponse
from .models import Word, Child
from django.contrib.auth.models import User
from django.views.generic import View
from .forms import UserForm, UserLogin
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from math import ceil as ceiling
import time


# Create your views here.

# TODO: Clearly this needs to be cleaned up!
def index(request):
    context = {}
    context['title'] = 'Splashscreen'
    context['subtitle'] = 'Here be dragons.'
    context['content'] = 'Yo whaddup son?'
    return render(request, 'outline/simple_output.html', context)


# TODO: This is just a temp view to show all word objects.
def word_test(request):
    html = ''
    words = Word.objects.all()
    for word in words:
        html += '<br><h1>Word: ' + str(word.word) + '</h1>'
        html += '<br><h3>Date: ' + str(word.date) + '</h3>'
        html += '<br>Etymology: ' + str(word.etymology)
    return HttpResponse(html)


# TODO: get_object_or_404 with user
# this view is just used for testing permissions stuff.
# Can eventually be deleted.
def user_junk(request, user, child=None, word=None):
    html = ''
    for dude in User.objects.all():
        html += '<br><h1>' + str(dude) + '</h1>'
        if dude.viewer_set.all():
            html += '<br>Restricted profile!'
            html += ' Can ' + str(user) + ' access? '
            for viewer in dude.viewer_set.all():
                html += str(user in str(viewer.viewer))
        else:
            html += 'Unrestricted profile!'
    return HttpResponse(html + '<br><br><h1>User accessing content: ' + str(user) + '</h1>')


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

        return render(request, self.template_name, {'form': form, 'error_message': self.get_errors(form)})

    def get_errors(self, form):
        message = ''
        for key, value in form.errors.items():
            message += value
        return message


def register_test(request):
    if request.POST:

        retry_flag = False
        error_message = ''

        # Handles validation of username
        if request.POST['username']:
            # If the username is not alpha-numerical, return user to same registration screen with a modal
            # error message.
            if easy_clean(request.POST['username']) != request.POST['username']:
                retry_flag = True
                error_message += 'Username must be alpha numerical.'
            else:
                username = easy_clean(request.POST['username'])
                try:
                    User.objects.get(username=username)
                except User.DoesNotExist:
                    pass
                else:
                    error_message += 'Username is taken. Please try a different username. '
        else:
            retry_flag = True
            error_message += 'Enter a username. '

        # Handles validation of password
        if request.POST['password'] and request.POST['password2']:
            if request.POST['password'] != request.POST['password2']:  # passwords don't match.
                retry_flag = True
                error_message += 'Passwords do not match. '
        else:  # password not entered
            retry_flag = True
            error_message += 'Password not entered'

        # Handles validation of e-mail.
        if request.POST['email']:
            if not email_valid(request.POST['email']):
                retry_flag = True
                error_message += 'Please enter a valid e-mail address. '
        else:
            retry_flag = True
            error_message += 'Please enter an e-mail address to associate with this account. '

        # if retry_flag = True, jump back to registration page with error_message in the context
        # else, save and login user, then redirect to a splash page.
        if retry_flag:
            return render(request, 'outline/registration_form_02.html', {'error_message': error_message})
        else:
            # TODO: (1) Actually register the user, (2) Send to a splash page
            user = User()
            user.username = request.POST['username']
            user.set_password(request.POST['password'])
            user.email = request.POST['email']
            user.save()
            print('Password = ', request.POST['password'])

            # returns User object if credentials are valid
            user = authenticate(username=user.username, password=request.POST['password'])
            print(user)

            if user is not None and user.is_active:
                login(request, user)
                return redirect('outline:index')

            # return render(request, 'outline/registration_form_02.html', {'error_message': 'Valid registration!'})

    else:
        return render(request, 'outline/registration_form_02.html')


# TODO: Purpose of the following view is to have a nice way to display a set of objects. Made good strides.
def itemlist(request, num_per_row=3, title='List of items.', subtitle="", intro_text="Here are your items:",
             list_of_items=[]):
    # number per row must be a factor of 12 for the Bootstrap gridding system to work. If provided with a number per
    # row value that is not a factor of 12, set num_per_row to 3 by default.
    if 12 % num_per_row != 0 or num_per_row > 6:
        num_per_row = 3
    context = {}
    context['title'] = title
    context['subtitle'] = subtitle
    context['intro_text'] = intro_text
    # Generating a dummy list of items to display, if none is provided:
    if len(list_of_items) == 0:
        num_per_row = 4
        if 12 % num_per_row != 0 or num_per_row > 6:
            num_per_row = 3
        for k in range(72):
            title = 'Title of item #' + str(k+1)
            if k%3 == 0:
                imgsrc = False
            else:
                imgsrc = "https://img.cinemablend.com/cb/9/1/9/4/f/f/9194ff31206ae73db1cc2ae3c8ba0647d71fc6f8c0a4ef9f5ed223fec4bc6cba.jpg"
            text = "And here's the explanatory text that goes under the thing."
            link = "http://www.amazon.com/"
            link_text = "Click!"
            list_of_items.append(ItemListObject(title=title, imgsrc=imgsrc, text=text,
                                                link_text=link_text, link=link))

    # Using itemlist_gridder to create a 2d list
    context['itemlist'] = itemlist_gridder(list_of_items, num_per_row)
    # Setting the column width for display based on the number of items expected per row.
    context['itemlist_col_width'] = int(12 / num_per_row)

    return render(request, 'outline/list_template.html', context)


class ItemListObject():

    def __init__(self, title="", imgsrc="", text="", link='#', link_text='Click here for details.'):
        self.title = title
        self.imgsrc = imgsrc
        self.text = text
        self.link = link
        self.link_text = link_text
        if title == "" and imgsrc == "" and text == "":
            self.has_content = False
        else:
            self.has_content = True


# This function creates a grid of ItemListObject(s), given a list of ItemListObject(s).
def itemlist_gridder(itemlist, num_per_row=3):
    k = len(itemlist)
    # print('len = ',k)
    # print('num per row = ',num_per_row)
    new_list = []
    num_rows = ceiling(k/num_per_row)
    # print('num rows = ',num_rows)
    blanks = num_rows*num_per_row - k
    # print('num of blanks = ',blanks)
    for jimmy in range(blanks):
        itemlist.append(ItemListObject())
    # print('new len = ',len(itemlist))
    rows = []
    for jimmy in range(num_rows):
        row = []
        for johnny in range(num_per_row):
            row.append(itemlist.pop(0))
        rows.append(row)
    return rows


# Simplistic e-mail address validation.
def email_valid(email):
    email = str(email)
    if '@' not in email:
        return False
    split = email.rfind('@')
    right = email[split + 1:]
    if '.' not in right:
        return False
    return True


def is_alpha(string):
    string = string.lower()
    if string == 'a' or string == 'b' or string == 'c' or string == 'd' or string == 'e' or string == 'f' or string == 'g':
        return True
    elif string == 'h' or string == 'i' or string == 'j' or string == 'k' or string == 'l' or string == 'm':
        return True
    elif string == 'n' or string == 'o' or string == 'p' or string == 'q' or string == 'r' or string == 's':
        return True
    elif string == 't' or string == 'u' or string == 'v' or string == 'w' or string == 'x' or string == 'y' or string == 'x':
        return True
    return False


def is_numeral(char):
    char = str(char).strip()
    if char == '1' or char == '2' or char == '3' or char == '4' or char == '5' or char == '6' or char == '7' or char == '8':
        return True
    elif char == '0' or char == '9':
        return True
    return False


def easy_clean(string):
    string = string.strip().lower()
    cleaned = ''
    for char in string:
        if is_alpha(char) or is_numeral(char):
            cleaned += char
    return cleaned
