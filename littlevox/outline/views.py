from django.shortcuts import render
from django.http import HttpResponse
from .models import Child, Word, ItemListObject
from django.contrib.auth.models import User
from django.views.generic import View
from .forms import UserForm, UserLogin
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from math import ceil as ceiling
from .simple_search import get_matches
from random import sample


# Create your views here.

# TODO: Clearly this needs to be cleaned up!
def index(request, context={}):
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


def logout_view(request):
    username = request.user.username
    if not username:
        username = 'Logout'
    context = {}
    context['error_title'] = username
    context['error_message'] = 'You have been logged out.'
    logout(request)
    return index(request, context)


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


# As of now, this defines a view showing all users.
# Eventually, this should be changed to have a search function, which should, in turn, utilize
# the functionality of simple_search.py.
def users(request):
    # If landing on the page with GET method

    DEFAULT_SEARCH_RESULTS = 15

    if not request.POST:
        # TODO: Change this next line when Users have an attribute for 'searchable'
        folks = sample(list(User.objects.all()), 12)  # Getting a list of all User objects
        user_items = []  # Initializing an empty list to all ItemListObject representations of Users.
        for folk in folks:
            user_items.append(user_to_itemlist_item(folk))
        context = dict()
        context['num_per_row'] = 4
        context['title'] = 'All users'
        context['intro_text'] = 'List of all users.'
        context['list_of_items'] = user_items
        context['search_bar'] = True
        return itemlist(request, context)
    # Otherwise, if requesting the page with POST:
    else:
        context = dict()
        context['number_per_row'] = 3
        context['title'] = 'Search results (' + request.POST['query'] + ')'
        matches = get_matches(request.POST['query'], User.objects.all(), DEFAULT_SEARCH_RESULTS)
        context['content'] = 'Stubby stub.'
        context['search_bar'] = True
        context['list_of_items'] = []
        for match in matches:
            context['list_of_items'].append(user_to_itemlist_item(match))

        return itemlist(request, context)


def user_to_itemlist_item(user):
    title = user.username
    imgsrc = False  # Could do profile picture at some point.
    text = user.email
    link = '/outline/user/' + user.username + '/'
    link_text = 'View Profile'
    return ItemListObject(title=title, imgsrc=imgsrc, text=text, link=link, link_text=link_text)


def register(request):
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
            return render(request, 'outline/registration_form.html', {'error_message': error_message})
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
        return render(request, 'outline/registration_form.html')


# Used to R&D the item_list display. Just makes dummy data for display.
def blank_item_list(request):
    # Generating a dummy list of items to display, if none is provided:
    context = dict()
    context['error_message'] = 'Empty itemlist requested. Showing dummy content.'
    context['error_title'] = 'No items requested'
    context['num_per_row'] = 3
    context['list_of_items'] = []
    for k in range(72):
        title = 'Title of item #' + str(k + 1)
        if k % 4 == 0:
            imgsrc = False
        elif k % 5 == 0:
            imgsrc = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/"
            imgsrc += "Danny_DeVito_by_Gage_Skidmore.jpg/170px-Danny_DeVito_by_Gage_Skidmore.jpg"
        else:
            imgsrc = "https://img.cinemablend.com/cb/9/1/9/4/f/f/9194ff31206ae73db1cc2ae3c8ba0647"
            imgsrc += "d71fc6f8c0a4ef9f5ed223fec4bc6cba.jpg"

        if k % 4 != 0:
            text = "Some other explanatory text."
        else:
            text = False

        if k % 10 == 0:
            link_text = "Text 4 buttonz"
        else:
            link_text = "Click!"

        link = "http://www.amazon.com/"
        context['list_of_items'].append(ItemListObject(title=title, imgsrc=imgsrc, text=text,
                                                       link_text=link_text,
                                                       link=link))  # TODO: Purpose of the following view is to have a nice way to display a set of objects. Made good strides.
    return itemlist(request, context)


def itemlist(request, context={}):
    if context == {}:
        return index(request)

    # number per row must be a factor of 12 for the Bootstrap gridding system to work. If provided with a number per
    # row value that is not a factor of 12, set num_per_row to 3 by default. Also set the highest number per row
    # at 4 (at 6, buttons become "crunched").

    try:
        context['num_per_row']
    except KeyError:
        context['num_per_row'] = 3

    if 12 % context['num_per_row'] != 0 or context['num_per_row'] > 4:
        context['num_per_row'] = 3

    # Using itemlist_gridder to create a 2d list
    context['itemlist'] = itemlist_gridder(context['list_of_items'], context['num_per_row'])

    # Setting the column width for display based on the number of items expected per row.
    context['itemlist_col_width'] = int(12 / context['num_per_row'])

    return render(request, 'outline/list_template.html', context)


def all_child_list(request):
    children = Child.objects.all()
    child_items = []
    for child in children:
        child_items.append(child.as_itemlist_item())
    return itemlist(request, num_per_row=2, title='All children',
                    intro_text="List of all children", list_of_items=child_items)


# This function creates a grid of ItemListObject(s), given a list of ItemListObject(s).
def itemlist_gridder(itemlist, num_per_row=3):
    k = len(itemlist)
    # print('len = ',k)
    # print('num per row = ',num_per_row)
    new_list = []
    num_rows = ceiling(k / num_per_row)
    # print('num rows = ',num_rows)
    blanks = num_rows * num_per_row - k
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


def get_list_all_users():
    users = User.objects.all()
    user_list = []
    for user in users:
        user_list.append(user.username)
    return user_list
