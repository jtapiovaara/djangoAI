import uuid
from pathlib import Path
from django.db import models
from django.urls import reverse
from djangoAI.settings import MEDIA_URL


class Personality(models.Model):
    name = models.CharField(max_length=32)
    character = models.TextField()

    def __str__(self):
        return self.name


class Chat(models.Model):
    name = models.CharField(max_length=64)
    dialoque = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    personality = models.ForeignKey(Personality, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @classmethod
    def talteen(cls, name, dialoque, personality):
        chat = cls(name=name, dialoque=dialoque, personality_id=Personality.objects.get(name__exact=personality).id)
        return chat


class Story(models.Model):
    name = models.CharField(max_length=32)
    styles = models.CharField(max_length=64)
    temp = models.DecimalField(max_digits=2, decimal_places=1)

    def __str__(self):
        return self.name


def image_path(instance, filename):
    path = Path(filename)
    return "images/{}{}".format(
        uuid.uuid4(),
        path.suffix
    )


class Completestory(models.Model):
    name = models.CharField(max_length=64)
    content = models.TextField()
    rolls = models.CharField(max_length=128)
    image = models.ImageField(upload_to=image_path, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('image')

    @classmethod
    def completestorytalteen(cls, name, content, rolls, image):
        completestory = cls(name=name, content=content, rolls=rolls, image=image)
        return completestory


class Djangoaiuser(models.Model):
    firstname = models.CharField(max_length=32, blank=True)
    lastname = models.CharField(max_length=32, blank=True)
    username = models.CharField(max_length=24)
    openaikey = models.CharField(max_length=128, blank=True)
    openaiorg = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.username
