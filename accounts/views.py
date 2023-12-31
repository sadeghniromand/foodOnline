from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib import messages, auth
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from vendor.forms import VendorForm
from . import forms, models
from .utils import detect_user, send_verification_email, send_password_reset_email


# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return 2
    else:
        raise PermissionDenied


""" Create Customer user using func and model form """


def register_user(request):
    if request.method == "POST":
        form = forms.UserForm(request.POST)
        if form.is_valid():
            """ Create the user using the form """

            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = models.User.CUSTOMER
            user.save()
            send_verification_email(request, user)
            messages.success(request, 'Your account has been registered successfully')
            """ Create the user using create_user method """

            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # username = form.cleaned_data['username']
            # email = form.cleaned_data['email']
            # password = form.cleaned_data['password']
            # user = models.User.objects.create_user(first_name, last_name, username, email, password)
            # user.role = models.User.CUSTOMER
            # user.save()
            return redirect('registerUser')
    else:
        form = forms.UserForm()
    return render(request, 'accounts/register_user.html', context={'form': form})


""" Create customer user using class and django create user form """


class CreateUserRegisterView(CreateView):
    form_class = forms.CustomUserCreationForm
    template_name = 'accounts/register_user.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = models.User.CUSTOMER
        user.save()
        return super().form_valid(user)

    def get_success_url(self):
        return redirect('registerUser')


def register_vendor(request):
    if request.method == "POST":
        form = forms.UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = models.User.Vendor
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = user.userprofile
            vendor.save()
            send_verification_email(request, user)
            messages.success(request, 'Your account has been registered successfully! Please wait for the approval.')
            return redirect('registerVendor')
    else:
        form = forms.UserForm()
        v_form = VendorForm()

    return render(request, 'accounts/register_vendor.html', context={'form': form, 'v_form': v_form})


def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = models.User._default_manger.get(pk=uid)
    except(TypeError, ValueError, OverflowError, models.User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! your account is activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'invalid activation link.')
        return redirect('myAccount')


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged.")
            return redirect('myAccount')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')


# <-------------------------------------------------------------------------------------------->
""" DASHBOARD VIEWS """


@login_required(login_url='login')
def my_account(request):
    user = request.user
    redirect_url = detect_user(user)
    return redirect(redirect_url)


@login_required(login_url='login')
@user_passes_test(check_role_customer, )
def cust_dashboard(request):
    return render(request, 'accounts/cust_dashboard.html')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    return render(request, 'accounts/vendor_dashboard.html')


# <-------------------------------------------------------------------------------------------->
""" FORGET PASSWORD VIEWS """


def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        if models.User.objects.filter(email=email).exists():
            user = models.User.objects.get(email__exact=email)
            send_password_reset_email(request, user)
            messages.success(request, 'Password reset link has been send to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = models.User._default_manger.get(pk=uid)
    except(TypeError, ValueError, OverflowError, models.User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('myAccount')


def reset_password(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            if pk:
                user = models.User.objects.get(pk=pk)
                user.set_password(password)
                user.is_active = True
                user.save()
                messages.success(request, 'Password reset successfully.')
                return redirect('login')
            else:
                return redirect('myAccount')

        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
