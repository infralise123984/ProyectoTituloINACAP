from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')
def login(request):
    return render(request, 'login.html')
def enviar(request):
    return render(request, 'enviar.html')
def buscar(request):
    return render(request, 'buscar.html')