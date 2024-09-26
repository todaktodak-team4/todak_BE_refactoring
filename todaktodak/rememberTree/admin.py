from django.contrib import admin

# Register your models here.

from .models import rememberTree,Photo,Question,UserQuestionAnswer, Letters

# Register your models here.
admin.site.register(rememberTree)
admin.site.register(Photo)
admin.site.register(Question)
admin.site.register(UserQuestionAnswer)
admin.site.register(Letters)