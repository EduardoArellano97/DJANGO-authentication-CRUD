from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required #Nos servirá para especificar cuáles direcciones requieren estar logeado 

# Create your views here.

def home(request):
    return render(request, 'home.html')


def log_in(request):
    if request.method == 'GET':
        return render(request,'login.html', {
            'form': AuthenticationForm
            })
    else:
        user = authenticate(request, username=request.POST['username'], password= request.POST['password'] )
        if user is None:
            return render(request,'login.html', {
            'form': AuthenticationForm,
            'error': "Username or password is not correct"
            })
        else:
            login(request, user) #recordar que, si el usuario es autenticado, es necesario guardar la sesión.
            return redirect('tasks')

        
def signup(request):
    # if request.method == 'GET': #De esta forma comprobamos que al ingresar al sitio web se está haciendo un GET de los datos
    #     print('method get has been used')
    # if request.POST: #De esta forma podemos comprobar que SÍ se envían datos
    #     print(request.POST) #imprimimos un diccionario donde se encuentran el name de los inputs y los valores... 
        
    #     print('method post has been used')
    
    if request.method == 'GET': 
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else: 
        if request.POST['password1'] == request.POST['password2']:
            #si ambas contraseñas coinciden debe REGISTRARSE UN USUARIO. 
            try:
                user = User.objects.create_user(username= request.POST['username'], password= request.POST['password1'])
                user.save() #guarda el usuario
                login(request, user) #crea una cookie 
                return redirect('tasks')
            except IntegrityError : 
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'User already exists'
                })  
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Passwords do not match'
        })  

@login_required
def tasks(request):
    #tasks = Task.objects.all() Trae todas las tareas, pero si quisieramos filtrarlo por usuario loggeado se haría asi:
    tasks = Task.objects.filter(user = request.user, completion_date__isnull = True) #Donde el usuario sea el mismo que el de la sesión activa
    #tasks = Task.objects.filter(user = request.user, completion_date__isnull=True) #Donde el usuario sea el mismo que el de la sesión activa y además no esté completado
    
    return render(request,'tasks.html', {
        'tasks': tasks
    })

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user = request.user, completion_date__isnull = False ).order_by('-completion_date')
    return render(request, 'completed_tasks.html',{ #En este caso, filtramos las tareas completadas y las ordenamos por más viejas
        'tasks':tasks
    })

@login_required
def create_task(request):
    if request.method == 'GET': 
        return render(request, 'create_task.html', {
        'form': TaskForm
    })
    else:
        try:
            form = TaskForm(request.POST) #Guardamos los valores de los inputs en false
            new_task = form.save(commit=False) #Evitamos que guarde una instancia
            new_task.user = request.user #El model pide un user, le adjuntamos el de la sesión
            # print(new_task), devuelve:  Hello From the Front-end - created by : eduardo
            new_task.save() #Guarda los datos y comprobamos desde admin
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Valid data not correctly provided'
                })

@login_required
def task_detail(request, task_id):
    # print(task_id) hasta este punto, redirigirá a task_detail sin importar el número de consulta 
    # task = Task.objects.get(pk= task_id) El conflicto se encuentra cuandp no existe un pk y tumba el servidor, para eso usamos get_object_or_404 de shortcuts
    if request.method == 'GET':
        task = get_object_or_404(Task, pk = task_id, user = request.user) #se añadió el user = request. user para evitar poder entrar a tareas que NO son propiedad del usuario en sesión
        form = TaskForm(instance = task)
        return render(request, 'task_detail.html',{
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task, pk = task_id, user = request.user)
            form = TaskForm(request.POST , instance= task)
            form.save()
            return redirect ('tasks')
        except ValueError:
            return render(request, 'task_detail.html',{
            'task': task,
            'form': form,
            'error': 'Error trying to update data'
        })

@login_required        
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk = task_id, user = request.user)
    if request.method == 'POST':
        task.completion_date = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk = task_id, user = request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
        
@login_required
def log_out(request):
    logout(request)
    return redirect('home')