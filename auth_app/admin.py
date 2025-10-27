from django.contrib import admin
from auth_app.models import Post  # ✅ Correct import

# Register your models here.
admin.site.register(Post)
