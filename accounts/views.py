from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib import messages

from vendor.forms import VendorForm
from . import forms, models

# Create your views here.

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
            messages.success(request, 'Your account has been registered successfully! Please wait for the approval.')
            return redirect('registerVendor')
    else:
        form = forms.UserForm()
        v_form = VendorForm()

    return render(request, 'accounts/register_vendor.html', context={'form': form, 'v_form': v_form})
