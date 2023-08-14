from store.models import User 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from store.models import Product
from django.views.generic import ListView
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import CreateView

def is_admin(user):
    return user.is_authenticated and user.is_staff  # Modify this logic based on your user roles


@user_passes_test(is_admin, login_url='store:login')
def dashboard(request):
    user_count = User.objects.count()
    

    context = {
        'user_count': user_count,
        # Include other data needed for charts
    }

    return render(request, 'custom_admin/dashboard.html', context)


@user_passes_test(lambda u: u.is_superuser)  # Restrict access to admin users only
def manage_users(request):
    users = User.objects.all()
    return render(request, 'custom_admin/manage_users.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser)  # Restrict access to admin users only
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = UserChangeForm(instance=user)

    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect('custom_admin:manage_users')

    return render(request, 'custom_admin/edit_user.html', {'form': form, 'user': user})

@user_passes_test(lambda u: u.is_superuser)  # Restrict access to admin users only
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User '{user.username}' deleted successfully.")
        return redirect('custom_admin:manage_users')

    return render(request, 'custom_admin/delete_user.html', {'user': user})

@user_passes_test(lambda u: u.is_superuser)  # Restrict access to admin users only
def change_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = PasswordChangeForm(user)

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Update session authentication hash
            messages.success(request, f"Password for '{user.username}' changed successfully.")
            return redirect('custom_admin:manage_users')

    return render(request, 'custom_admin/change_password.html', {'form': form, 'user': user})

class ProductListView(ListView):
    model = Product
    template_name = 'custom_admin/product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    fields = ['title', 'slug', 'sku', 'short_description', 'popularity', 'detail_description', 'product_image', 'price', 'category', 'is_active', 'is_featured']
    template_name = 'custom_admin/create_product_form.html'
    success_url = reverse_lazy('custom_admin:product-list')

class ProductUpdateView(UpdateView):
    model = Product
    fields = ['title', 'slug', 'sku', 'short_description', 'popularity', 'detail_description', 'product_image', 'price', 'category', 'is_active', 'is_featured']
    template_name = 'custom_admin/edit_product.html'
    success_url = reverse_lazy('custom_admin:product-list')


from store.models import Product

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'custom_admin/product_confirm_delete.html'
    success_url = reverse_lazy('custom_admin:product-list')