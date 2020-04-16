from django.contrib import admin

from .models import Profile, ProfileFile


class ProfileFileInline(admin.TabularInline):
    model = ProfileFile
    extra = 1


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_digital']
    inlines = [ProfileFileInline]
    class Meta:
        model = Profile

admin.site.register(Profile, ProfileAdmin)