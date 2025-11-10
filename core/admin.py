from django.contrib import admin
from userauths.models import User

#remember to pip instal django-jazzmin
#super user info: user: crowofvictoria@gmail.com, pass: password123
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
