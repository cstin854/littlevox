from django.shortcuts import render
from django.http import HttpResponse
from .models import Child, Word, ItemListObject, Message
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from math import ceil as ceiling
from .simple_search import get_matches
from random import sample
from django.views.decorators.cache import cache_control
from .helper_functions import easy_today
from .models import *
import time
from dateutil import parser  #Used to convert string time to datetime object

def index(request, context={}):
    if request.user.username:
        return redirect('outline:user_splashpage', user=request.user.username)
    else:
        return redirect('outline:login_view')


def addchild(request):
    return index(request, context={'error_message': 'This view is not hooked up yet.'})


# TODO: This is just a temp view to show all word objects.
def word_test(request):
    html = ''
    words = Word.objects.all()
    for word in words:
        html += '<br><h1>Word: ' + str(word.word) + '</h1>'
        html += '<br><h2>id: ' + str(word.id) + '</h2>'
        html += '<br><h3>Date: ' + str(word.date) + '</h3>'
        html += '<br>Etymology: ' + str(word.etymology) + '<hr>'
    return HttpResponse(html)


def logout_view(request):
    username = request.user.username
    if not username:
        username = ''
    logout(request)
    context = dict()
    context['error_title'] = username
    context['error_message'] = 'You have been logged out.'
    return index(request, context)


def remove_viewer(request, user):
    if request.POST:  # if POSt data received
        if 'revoke' in request.POST:  # if the requester confirmed removing "viewer" from auth'd viewers:
            disintegrate_friendship(request.user.username, request.POST['viewer'])

        # either way, redirect to user dashboard view
        return redirect('outline:user_splashpage', user=request.user.username)

    else:  # if no POST data...

        if request.user.username:
            context = dict()
            requester = User.objects.get(username=request.user.username)
            try:
                viewer = requester.viewer_set.get(viewer=user)
            except:
                request.session['error_message'] = "Privileges cannot be revoked because that user does not have" \
                                                   " permissions to view your profile."
                return redirect('outline:user_splahspage', user=requester)

            context['viewer'] = viewer
            context['requester'] = requester
            context['dashboard_active'] = True

            return render(request, 'outline/remove_viewer_template.html', context)

        else:
            return redirect('outline:index')


# TODO: get_object_or_404 with user
# this view is just used for testing permissions stuff.
# Can eventually be deleted.
def user_splashpage(request, user):
    context = dict()

    if 'error_message' in request.session:
        context['error_message'] = request.session['error_message']
        del request.session['error_message']
        if 'error_title' in request.session:
            context['error_title'] = request.session['error_title']
            del request.session['error_title']
        else:
            context['error_title'] = 'Error'
        request.session.modified = True

    # If the page requested via POST
    if request.POST:
        request.session['error_title'] = "Processing test."
        msg = ''
        for key, val in request.POST.items():
            msg += "Key = " + key + "<br>"
            msg += "------Val = " + val + "<hr>"
        request.session['error_message'] = msg
        return redirect('outline:user_splashpage', user=request.user.username)

    # If the page requested via GET
    else:

        try:
            user = User.objects.get(username=user)
        except:
            request.session['error_message'] = "That user does not exist."
            return redirect('outline:users')

        if 'error_message' in request.session:
            context['error_message'] = request.session['error_message']
            del request.session['error_message']
            request.session.modified = True

        if 'error_title' in request.session:
            context['error_title'] = request.session['error_title']
            del request.session['error_title']
            request.session.modified = True

        context['dashboard_active'] = True
        context['user'] = user.username

        # If this is user's own dashboard.
        if request.user.username == user.username:

            try:
                context['viewer_list'] = list(user.viewer_set.all())
            except:
                context['viewer_list'] = False

            try:
                context['child_list'] = list(user.child_set.all())
            except:
                context['child_list'] = False

            try:
                context['messages'] = list(user.message_set.all())
                context['number_of_messages'] = len(context['messages'])
            except:
                context['messages'] = False
                context['number_of_messages'] = False

            context['dashboard_header'] = "Welcome! This is your dashboard."
            context['is_owner'] = True

            return render(request, 'outline/dashboard.html', context)

        # If this is not the user's dashboard.
        else:

            try:
                context['child_list'] = list(user.child_set.all())
            except:
                context['child_list'] = False

            context['dashboard_header'] = "Welcome! You are viewing " + user.username + "'s dashboard."
            context['is_owner'] = False

            # Eventually, this should be its own template, dashboard_visitor.html
            return render(request, 'outline/dashboard.html', context)


def friend_request(request, recipient):
    context = dict()
    context['users_active'] = True

    if request.POST:
        message = Message()
        message.date = request.POST['date']
        message.recipient = User.objects.get(username=request.POST['recipient'])
        message.sender = request.POST['sender']
        message.message = request.POST['message']
        message.type = 'friend request'
        is_valid = message.is_valid()
        if is_valid[0]:
            message.save()
            request.session['error_title'] = "Thank you!"
        else:
            request.session['error_title'] = "Message not processed."
        request.session['error_message'] = is_valid[1]
        return redirect('outline:user_splashpage', user=request.user.username)
    else:
        context['recipient'] = recipient
        context['user_active'] = True
        context['date'] = easy_today()
        context['sender'] = request.user.username
        return render(request, 'outline/frrq.html', context)


def child_dashboard(request, childid):
    context = dict()
    try:
        context['child'] = Child.objects.get(id=childid)
    except:
        request.session['error_title'] = 'Error'
        request.session['error_message'] = 'Child not found.'
        return redirect('outline:user_splashpage', user=request.user.username)
    context['vocabulary'] = context['child'].word_set.all()
    return render(request, 'outline/child_dashboard.html', context)


def process_message(request):
    if request.POST:
        if request.POST['message_option'] == 'accept':
            initiate_friendship(recipient, sender)
            msg.delete()
        elif request.POST['message_option'] == 'deny':
            msg.delete()
        elif request.POST['message_option'] == 'blockuser':
            initiate_block(recipient, sender)
            msg.delete()

    return redirect('outline:user_splashpage', user=request.user.username)


def blocked_users(request):
    blocked_users_queryset = request.user.viewer_set.filter(is_blocked = True)
    context = dict()
    context['blocked_users'] = blocked_users_queryset
    context['users_active'] = True
    return render(request, 'outline/blocked.html', context)


def unblock(request, user_to_unblock):
    worked = remove_block(request.user.username, user_to_unblock)
    if worked:
        request.session['error_title'] = user_to_unblock + ' unblocked.'
        msg = 'To add this user as a friend, search username ' + user_to_unblock
        msg += ' on the "Users" page.'
        request.session['error_message'] = msg
    else:
        request.session['error_title'] = 'Action unsuccessful.'
        request.session['error_message'] = 'Your last action was unsuccessful. If you believe you are receiving this message in error, please contact us.'
    return redirect('outline:user_splashpage', user=request.user.username)


def addword(request):
    context = dict()
    context['addword_active'] = True

    if request.POST:
        user = request.user
        child = user.child_set.get(name = request.POST['child'])
        date = parser.parse(request.POST['date'])
        word = Word()
        word.child = child
        word.date = date
        word.word = request.POST['word']
        word.note = request.POST['notes']
        worked = word.custom_save()
        #TODO: If the word saved successfully, should redirect to that child-word's page
        if worked:
            request.session['error_title'] = "Word " + word.word + " successfully added."
            request.session['error_message'] = user.username + ' ' + child.name + ' ' + str(date) + ' ' + word.note
            return redirect('outline:child_word', wordid = word.id)
        else:
            request.session['error_title'] = "Word " + word.word + " could not be added."
            request.session['error_message'] = "This word is already in " + child.name + "'s vocabulary."
            return redirect('outline:user_splashpage', user = request.user.username)

    #Creates a list of the user's children to be passed through context.
    children_sorted = []
    children = request.user.child_set.all()
    #Makes the default child appear first in the list
    for child in children:
        if child.is_default:
            children_sorted.append(child)
    #Followed by any other children
    for child in children:
        if not child.is_default:
            children_sorted.append(child)

    context['children'] = children_sorted
    context['today'] = time.strftime("%m/%d/%Y")
    return render(request, 'outline/add_word.html', context)


#Allows a user to edit a word
def edit_word(request, wordid):
    #Creates the context dict to be passed to the template
    context = dict()
    context['addword_active'] = True

    #If the user requests the page via POST
    if request.POST:
        postData = dict(request.POST)
        context['keys'] = str(postData.keys())
        context['values'] = str(postData.values())

    word = Word.objects.get(id=wordid)
    context['word'] = word
    context['date'] = word.get_date()

    return render(request, 'outline/edit_word.html', context)

#This should be a view that shows information about the word-child connection.
def child_word(request, wordid):
    context = dict()
    if 'error_message' in request.session:
        context['error_message'] = request.session['error_message']
        del request.session['error_message']
        request.session.modified = True

    if 'error_title' in request.session:
        context['error_title'] = request.session['error_title']
        del request.session['error_title']
        request.session.modified = True
    try:
        word = Word.objects.get(id=wordid)
    except:
        request.session['error_title'] = "Error"
        request.session['error_message'] = "Word not found."
        return redirect('outline:user_splashpage', user = request.user.username)
    context['word'] = word
    return render(request, 'outline/word_display.html', context)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def users(request):
    DEFAULT_SEARCH_RESULTS = 15
    context = dict()
    context['users_active'] = True

    if 'error_message' in request.session:
        context['error_message'] = request.session['error_message']
        del request.session['error_message']
        request.session.modified = True

    # If landing on the page with GET method
    if not request.POST:
        all_users = list(User.objects.all())
        number_of_users = len(all_users)
        sample_size = min(12, number_of_users)
        folks = sample(all_users, sample_size)  # Getting a sample of User objects
        user_items = []  # Initializing an empty list to all ItemListObject representations of Users.
        for folk in folks:
            #Checks to see if there is a block between the requesting user and the
            #user in the returned set. If not, then make an itemlist view to display
            if not check_relationship(User.objects.get(username=request.user.username), folk)['block']:
                user_items.append(user_to_itemlist_item(folk, viewer=request.user.username))
        context['num_per_row'] = 4
        context['title'] = 'All users'
        context['intro_text'] = 'List of all users.'
        context['list_of_items'] = user_items
        context['search_bar'] = True
        return itemlist(request, context)
    # Otherwise, if requesting the page with POST:
    else:
        context['number_per_row'] = 3
        context['title'] = 'Search results (' + request.POST['query'] + ')'
        matches = get_matches(request.POST['query'], User.objects.all(), DEFAULT_SEARCH_RESULTS)
        context['search_bar'] = True
        context['list_of_items'] = []
        for match in matches:
            #Checks to see if there is a block between the requesting user and the
            #user in the returned set. If not, then make an itemlist view to display
            if not check_relationship(User.objects.get(username=request.user.username), match)['block']:
                context['list_of_items'].append(user_to_itemlist_item(match, viewer=request.user.username))

        return itemlist(request, context)


def user_to_itemlist_item(user, viewer=False):
    title = user.username
    imgsrc = False  # Could do profile picture at some point.
    try:
        viewer = User.objects.get(username=viewer)
    except:
        viewer = False
    print('Viewer = ', viewer)
    try:
        set = User.objects.get(username=user).viewer_set.get(viewer=viewer)
    except:
        if user == viewer:
            can_view = True
        else:
            can_view = False
    else:
        can_view = True
    # print('--------viewerset = ', set)
    # print('Can view? ', can_view, '\n')
    if can_view:
        link = '/outline/user/' + user.username + '/'
        link_text = 'View Profile'
    else:
        link = '/outline/frrq/' + user.username + '/'
        link_text = 'Friend request!'
    return ItemListObject(title=title, imgsrc=imgsrc, text='', link=link, link_text=link_text)


def login_view(request):
    # If POST
    if request.POST:

        # Gets username and password from POST data.
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        # If the user exists and is active, redirect to index with welcome message.
        if user is not None and user.is_active:
            # TODO: This is not working!
            if not request.POST.get('remember_me', None):
                print('Do something! User requested not to be remembered.')
            else:
                print('Do something! Used requested to be remembered.')
            # Logs the user in.
            login(request, user)
            return index(request,
                         {'error_title': 'Welcome ' + username + '!', 'error_message': 'You have been logged in.'})
        # Otherwise, redirect back to the login screen with an error message.
        else:
            error_message = 'There was an error with your login attempt. Please check your username and '
            error_message += 'password again. If you believe you are receiving this message in error, '
            error_message += 'please contact us.'
            return render(request, 'outline/login_form.html', {'error_message': error_message,
                                                               'loginout_active': True})
    # If GET
    else:
        # If the user is already logged in, prompt the user to logout or contact admin.
        if request.user.username:
            context = {}
            error_message = 'You are already logged in as user ' + request.user.username
            error_message += '. Please log out if you believe this is in error or '
            error_message += 'if you would like to log in as another user.'
            context['error_message'] = error_message
            context['error_title'] = 'Already logged in:'
            return index(request, context)
        # Otherwise, render the login_form.
        return render(request, 'outline/login_form.html', {'loginout_active': True})


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
            return render(request, 'outline/registration_form.html', {'error_message': error_message,
                                                                      'loginout_active': True})
        else:
            # TODO: (1) Actually register the user, (2) Send to a splash page
            user = User()
            user.username = request.POST['username']
            user.set_password(request.POST['password'])
            user.email = request.POST['email']
            user.save()

            # returns User object if credentials are valid
            user = authenticate(username=user.username, password=request.POST['password'])

            if user is not None and user.is_active:
                login(request, user)
                return redirect('outline:index')

                # return render(request, 'outline/registration_form_02.html', {'error_message': 'Valid registration!'})

    else:
        return render(request, 'outline/registration_form.html', {'loginout_active': True})


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
        context['num_per_row'] = context['num_per_row']
    except KeyError:
        context['num_per_row'] = 3

    if 12 % int(context['num_per_row']) != 0 or int(context['num_per_row']) > 4:
        context['num_per_row'] = 3

    # Using itemlist_gridder to create a 2d list
    context['itemlist'] = itemlist_gridder(context['list_of_items'], context['num_per_row'])

    # Setting the column width for display based on the number of items expected per row.
    context['itemlist_col_width'] = int(12 / context['num_per_row'])

    return render(request, 'outline/list_template.html', context)

#TODO: This is a temporary view for development only.
def all_child_list(request):
    children = sample(list(Child.objects.all()), min(20, len(Child.objects.all())))
    child_items = []
    for child in children:
        child_items.append(child.as_itemlist_item())
    context = dict()
    context['num_per_row'] = 3
    context['title'] = 'All children'
    context['intro_text'] = 'List of all children. For development only.'
    context['list_of_items'] = child_items
    return itemlist(request, context)


# This function creates a grid of ItemListObject(s), given a list of ItemListObject(s).
def itemlist_gridder(itemlist, num_per_row=3):
    k = len(itemlist)
    # print('len = ',k)
    # print('num per row = ',num_per_row)
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
