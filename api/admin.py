from django.contrib import admin
from .models import LeaderBoard, User, Token, Question

admin.site.register(User)
admin.site.register(Token)
admin.site.register(Question)
admin.site.register(LeaderBoard)
