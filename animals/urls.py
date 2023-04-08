from django.urls import path
from animals import views

urlpatterns = [
    path('', views.animals, name='animals'),
    path('getimage/', views.getimage, name='getimage'),
    path('kirjallisuus/', views.kirjallisuus, name='kirjallisuus'),
    path('stars/', views.stars, name='stars'),
    path('askanything/', views.askanything, name='askanything'),
    path('kysymys/', views.kysymys, name='kysymys'),
    path('tyylitaulu/', views.tyylitaulu, name='tyylitaulu'),
    path('codepython/', views.codepython, name='codepython'),
    path('askbuffet/', views.askbuffet, name='askbuffet'),
    path('schufflecards/', views.schufflecards, name='schufflecards'),
    path('turbomode/', views.turbomode, name='turbomode'),
    path('flushchat/', views.flushchat, name='flushchat'),
    path('chatstories/', views.chatstories, name='chatstories'),
    path('chatmodal/<id>', views.chatmodal, name='chatmodal'),
    path('chatimage/<chat_id>', views.chatimage, name='chatimage'),
    path('rolldicies/', views.rolldicies, name='rolldicies'),
    path('storycubesstory/', views.storycubesstory, name='storycubesstory'),
    path('readoutloud/', views.readoutloud, name='readoutloud'),
    path('storycubesimage/', views.storycubesimage, name='storycubesimage'),
    path('savestory/', views.savestory, name='savestory'),
    path('getscience/', views.getscience, name='getscience'),
    path('justdraw/', views.justdraw, name='justdraw'),
    path('comparedocs/', views.comparedocs, name='comparedocs'),
]
