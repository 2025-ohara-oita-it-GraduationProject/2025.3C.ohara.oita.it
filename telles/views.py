from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic.base import TemplateView
from .forms import SignupForm
# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'
    
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            teacher_password = form.cleaned_data.get('teacher_password')

            # 教師判定
            if teacher_password == "teachpass123":
                user.is_staff = True

            user.save()
            login(request, user)
            return redirect('/')  # または redirect('index')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})
