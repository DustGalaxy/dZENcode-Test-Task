from django.contrib import admin

from .models import User, Comment, CommentAttachment


# Register your models here.
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(CommentAttachment)
