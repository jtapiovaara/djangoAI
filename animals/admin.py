from django.contrib import admin
from animals.models import Chat, Personality, Story, Completestory, Djangoaiuser


class ChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'personality', 'timestamp')
    list_editable = ('personality', )


class StoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'temp')
    list_editable = ('temp',)


admin.site.register(Chat, ChatAdmin)
admin.site.register(Personality)
admin.site.register(Story, StoryAdmin)
admin.site.register(Completestory)
admin.site.register(Djangoaiuser)
