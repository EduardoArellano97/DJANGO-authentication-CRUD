from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField(blank = True)
    creation_date = models.DateTimeField(auto_now_add = True)
    completion_date = models.DateTimeField(null = True, blank = True)
    important = models.BooleanField(default = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE) #En este caso, no es ya necesario crear otro modelo para la entidad User, debido a que se ha estado usando con la libreria. Así es como la relacionaremos con su llame foránea
    
    #creamos esta tabla con python manage.py makemigrations, posteriormente ejecutamos python manage.py migrate
    
    #al entrar en admin/ notaremos que ahora Task es accesible y se pueden crear tareas, para registrar el nombre con el title usaremos ...
    def __str__(self):
        return self.title + ' - created by : ' + self.user.username
    
    
