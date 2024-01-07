from django.shortcuts import render


def home(request):
    return render(request, 'core/main.html')

    
def about(request):
    pass


def terms(request):
    pass