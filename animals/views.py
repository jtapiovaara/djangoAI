import os.path
import urllib
import requests
import uuid
from pathlib import Path

import openai
import random
import gtts
from playsound import playsound
import pprint
import re
import json

from django.http import HttpResponse
from django.shortcuts import render

from animals.models import Chat, Personality, Story, Completestory
from djangoAI.settings import MEDIA_ROOT, OPENAI_ORG, OPENAI_API_KEY

# model_coding = 'code-davinci-002'
model_coding = 'gpt-3.5-turbo'
# engine_completions = 'text-davinci-003'
model_completions = 'text-davinci-003'
# model_chat = 'gpt-3.5-turbo'
model_chat = 'gpt-4'

# user_talks = []
# ai_talks = []
turbomode_messages = [{"role": "system", "content": ""}]


def getimage(request):
    """ The function first sets the openai.org and openai.api_key variables to some predefined constants
    OPENAI_ORG and OPENAI_API_KEY. It then retrieves a value from the GET data of the request object by looking up
    the key "animal" in the GET dictionary. If the "animal" key is not found, the default value "" (empty string) is
    used. Next, the code constructs a prompt for the image generation by concatenating the animal_kuvaksi value with
    the string "naivistic art". The code then calls the openai.Image.create method, passing in the prompt and several
    other arguments to specify the number of images to generate and the size of the images. The method returns a
    dictionary containing data about the generated images. Finally, the function returns an HTTP response using the
    HttpResponse function, which is a class in the Django web framework for returning HTTP responses. The response
    text is an HTML img tag that displays the image at the URL stored in the image_url variable, which is set to the
    URL of the first image in the data attribute of the dictionary returned by the openai.Image.create method. This
    content was created by chatGPT."""

    openai.organization = OPENAI_ORG
    openai.api_key = OPENAI_API_KEY
    animal_kuvaksi = request.GET.get("animal", "")
    prompt = f'{animal_kuvaksi} cartoon style naivistic art'
    r = openai.Image.create(
        prompt=f'{prompt}',
        n=1,
        size='256x256')
    image_url = r['data'][0]['url']

    return HttpResponse(f'<img src="{image_url}" style="width: 250px">')


def animals(request):
    """ The function first checks to see if the request method is POST by checking the method attribute of the
    request object. If the request method is POST, the code retrieves a value from the POST data by looking up the
    key "animal" in the POST dictionary.
    The code then creates a new OpenAI Completion object using the
    openai.Completion.create method, passing in several arguments to specify the model to use and the prompt for the
    completion.
    The generate_prompt function is called with the animal value to generate the prompt.
    Finally, the function returns an HTTP response using the HttpResponse function, which is a class in the Django web
    framework for returning HTTP responses. The response text is constructed using string formatting to include the
    result variable, which is set to the text of the first choice in the choices attribute of the response object.
    If the request method is not POST, the function simply returns the result of calling the render function, which is a
    function in the Django web framework for rendering an HTML template. The render function takes in the request object
    and the name of the template file as arguments. This content was created by chatGPT."""

    openai.api_key = OPENAI_API_KEY
    if request.method == "POST":
        animal = request.POST["animal"]
        response = openai.Completion.create(
            model=model_completions,
            prompt=generate_prompt(animal),
            temperature=0.4,
        )
        result = response.choices[0].text
        return HttpResponse(f'{result}')

    context = {
        'model_coding': model_coding,
        'model_completions': model_completions,
        'model_chat': model_chat,
    }

    return render(request, "index.html", {'context': context})


def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.
Animal: Cat
Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
Animal: Dog
Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
Animal: Horse
Names: White Fury, Black Beauty, The Queen Charme Asserdal
Animal: {}
Names:""".format(
        animal.capitalize()
    )


def kysymys(request):
    """ Tässä koitetaan ennakoida ja vaikuttaa vastaukseen muutenkin kuin vain kirjoitetulla kysymyksellä. Voidaan
    antaa käyttäjän valita kysymyksen aihe (esim. arkkitehtuuri: Alvar Aalto, Cubism, etc.) ja välittää se mukaan.
    Voidaan myös vaikuttaa/manipuloida kysymystä palvelinpäässä tässä funktiossa. Vaikuttaminen voi olla tietysti myös
    vaikka ohjattua muualta käsin (tässä muuttujalla 'tyyli_ext)' tai tietokannasta tms. Kiehtovaa."""

    openai.api_key = OPENAI_API_KEY
    if request.method == "GET":
        kysymyksesi = request.GET.get("kysymys", "")
        tyyli = request.GET.get("tyyli", "")
        tyyli_ext = 'Contemporary'
        # response = openai.Completion.create(
        #     engine=engine_completions,
        #     prompt=f'{kysymyksesi} {tyyli} {tyyli_ext}',
        #     temperature=0.6,
        #     max_tokens=150,
        # )
        # result = response.choices[0].text[:800]

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": f"You are an arts expert who highly values {tyyli_ext} art"},
                {"role": "user", "content": f"{kysymyksesi}. Consider art style: {tyyli}"},
                # {"role": "assistant", "content": f"{ai_talks}"},
                # {"role": "user", "content": f"{chatquery}"},
                # {"role": "user", "content": f"{content_query}"},
            ]
        )

        reply = completion.choices[0].message['content']
        # print(completion)

        return HttpResponse(f'<textarea name="artanswer" rows="7"cols="40" style="border: none">{reply}</textarea>')

    return render(request, "index.html")


def tyylitaulu(request):
    """ This function takes kysymys() result and uses it as a prompt to create DALLE2 image """
    openai.organization = OPENAI_ORG
    openai.api_key = OPENAI_API_KEY
    vastaus_kuvaksi_hx = request.GET.get('artanswer', '')
    prompt = f'{vastaus_kuvaksi_hx[0:320]}'
    r = openai.Image.create(
        prompt=f'{prompt}',
        n=1,
        size='256x256')
    image_url = r['data'][0]['url']

    return HttpResponse(f'<img src="{image_url}" style="width: 250px">')


def kirjallisuus(request):
    """ Here we send two separate requests (one for a story and one for a poem) to AI and get the results back in one
    HttpResponse. Also comparing result using different OpenAI Models
    """
    openai.api_key = OPENAI_API_KEY
    if request.method == 'GET':
        kirjailija = request.GET.get('kirjailija', '')
        kirja = request.GET.get('kirja', '')
        # response = openai.Completion.create(
        #     engine=model_completions,
        #     prompt=f'Assistant, please write a summary of book {kirja} by {kirjailija}',
        #     temperature=0.2,
        #     max_tokens=150,
        # )
        # tarina = response.choices[0].text

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": "You are a literature reviewer understanding especially well classical "
                                              "american literature. You also have a great sense of classical poetry"},
                {"role": "user", "content": f"Please write a short summary of book {kirja} by {kirjailija}. At the "
                                            f"end add representative poem about book {kirja}"},
                # {"role": "assistant", "content": f"{ai_talks}"},
                # {"role": "user", "content": f"{chatquery}"},
                # {"role": "user", "content": f"{content_query}"},
            ]
        )

        reply = completion.choices[0].message['content']
        # print(completion)

        return HttpResponse(f'About {kirja}:<p>{reply}</p>')

    return render(request, "index.html")


def stars(request):
    openai.api_key = OPENAI_API_KEY
    if request.method == 'GET':
        spacethought = request.GET.get('stars', '')
        # response = openai.Completion.create(
        #     engine=model_completions,
        #     prompt=f"{spacethought}, use scientific terms on your answer",
        #     temperature=0.2,
        #     max_tokens=250,
        # )
        # result = response.choices[0].text[:1600]

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": "use scientific terms on your answer"},
                {"role": "user", "content": f"{spacethought}"},
                # {"role": "assistant", "content": f"{ai_talks}"},
                # {"role": "user", "content": f"{chatquery}"},
                # {"role": "user", "content": f"{content_query}"},
            ]
        )

        reply = completion.choices[0].message['content']
        # print(completion)

        return HttpResponse(f'<p>{reply}</p>')
        # return HttpResponse(f'<p>GPT-3.5:&nbsp;{result}</p><p>GPT-4:&nbsp;{reply}</p>')
    return render(request, "index.html")


def turbomode(request):
    openai.api_key = OPENAI_API_KEY
    if request.method == "POST":
        systemcontent = Personality.objects.get(name='ai').character
        stylemode = request.POST["stylemode"]
        user = 'User'
        assistant = stylemode.capitalize()

        if stylemode == 'emilia':
            systemcontent = Personality.objects.get(name='emilia').character
        elif stylemode == 'jack':
            systemcontent = Personality.objects.get(name='jack').character
        elif stylemode == 'albert':
            systemcontent = Personality.objects.get(name='albert').character
        elif stylemode == 'marv':
            systemcontent = Personality.objects.get(name='marv').character
        elif stylemode == 'socrates':
            systemcontent = Personality.objects.get(name='socrates').character
        elif stylemode == 'drunken':
            systemcontent = Personality.objects.get(name='drunken').character

        chatquery = request.POST["fast"]
        if 'this_chat' in request.session:
            request.session['this_chat'] += f'{user}: {chatquery}'
        else:
            request.session['this_chat'] = f'{user}: {chatquery}'

        turbomode_messages[0]['content'] = f"{systemcontent}"
        turbomode_messages.append(
            {
                "role": "user",
                "content": f"{chatquery}"
            }
        )

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=turbomode_messages,
        )

        reply = completion.choices[0].message['content']
        request.session['this_chat'] += f'{assistant}: {reply}'
        turbomode_messages.append(
            {
                "role": "assistant",
                "content": f"{reply}"
            }
        )

        chat_reply = request.session['this_chat']
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(turbomode_messages)
        # print(completion)
        # print(chat_reply)
        context = {
            'chat_reply': chat_reply,
        }
        return render(request, 'partials/chat_dialogue.html', {'context': context})
    return render(request, "index.html")


def flushchat(request):
    """ Tyhjennetään (alustetaan) luettujen lista"""
    if 'this_chat' in request.session:
        # chats_dialoque = str(request.session['this_chat'])
        chats_dialoque = request.session['this_chat']
        chats_name = chats_dialoque[:23]
        chat = Chat.talteen(chats_name, chats_dialoque)
        chat.save()
        del request.session['this_chat']
        turbomode_messages = [{"role": "system", "content": ""}]

        return HttpResponse('&nbsp;Saved&nbsp;&&nbsp;flushed&nbsp;☑&nbsp;')
    return render(request, "index.html")


def chatstories(request):
    stories = Chat.objects.all().order_by('-timestamp')
    context = {
        'stories': stories,
    }
    return render(request, 'partials/chat_stories.html', {'context': context})


def chatmodal(request, id):
    """ Chatin sisältö"""
    chat = Chat.objects.get(id=id)
    chat_name = chat.name
    chat_info = chat.dialoque
    chat_time = chat.timestamp
    osissa = chat_info.split("', '")
    print(osissa[0][2:])
    print(osissa[1:-2])
    print(osissa[-1][:-2])

    context = {
        'chat_name': chat_name,
        'chat_info': chat_info,
        'chat_time': chat_time,
        'osissa_first': osissa[0][2:],
        'osissa': osissa[1:-2],
        'osissa_last': osissa[-1][:-2],
    }
    return render(request, 'partials/chat_modal.html', {'context': context})


def codepython(request):
    openai.api_key = OPENAI_API_KEY
    if request.method == 'GET':
        codethought = request.GET.get('codepython', '')
        # response = openai.Completion.create(
        #     model=model_coding,
        #     prompt=f'\"\"\"\n{codethought}\n\"\"\"',
        #     temperature=0,
        #     max_tokens=450,
        #     top_p=1,
        #     frequency_penalty=0,
        #     presence_penalty=0
        # )
        # code_result = response.choices[0].text

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": 'You are system that is always using standards'},
                {"role": "user", "content": f"{codethought}"},
                # {"role": "user", "content": f"{chatquery}"},
                # {"role": "user", "content": f"{content_query}"},
            ]
        )

        reply = completion.choices[0].message['content']
        # print(reply)
        context = {
            'code_result': reply,
        }
        return render(request, 'partials/code_python.html', {'context': context})
    return render(request, "index.html")


def rolldicies(request):
    playsound("animals/static/dice.mp3")
    cubes = [
        [
            'pyramid',
            'credit card',
            'rainbow',
            'tower',
            'tree',
            'eye'
        ],
        [
            'unhappy',
            'question',
            'fountain',
            'old key',
            'tiipii',
            'shooting star'
        ],
        [
            'cube',
            'magnifyer glass',
            'beetle',
            'hand',
            'turtle',
            'nightmare'
        ],
        [
            'keyhole',
            'masks',
            'parachute',
            'fish',
            'sunflower',
            'directions'
        ],
        [
            'moon',
            'bee',
            'magic wand',
            'bead board',
            'book',
            'bridge'
        ],
        [
            'phrase',
            'sleeping',
            'lamp',
            'house',
            'time',
            'arrow up'
        ],
        [
            'magnet',
            'footstep',
            'lock',
            'dragon',
            'lamb',
            'learning'
        ],
        [
            'mobile phone',
            'scale',
            'ufo',
            'walking stick',
            'flash',
            'arrow down'
        ],
        [
            'flashlight',
            'skyscraper',
            'happy',
            'airplane',
            'apple',
            'earth'
        ]
    ]
    random.shuffle(cubes[0])
    random.shuffle(cubes[1])
    random.shuffle(cubes[2])
    random.shuffle(cubes[3])
    random.shuffle(cubes[4])
    random.shuffle(cubes[5])
    random.shuffle(cubes[6])
    random.shuffle(cubes[7])
    random.shuffle(cubes[8])

    roll = [
        cubes[0][0],
        cubes[1][0],
        cubes[2][0],
        cubes[3][0],
        cubes[4][0],
        cubes[5][0],
        cubes[6][0],
        cubes[7][0],
        cubes[8][0],
    ]
    random.shuffle(roll)
    return HttpResponse(f'{roll}')


def storycubesstory(request):
    """ Muutettu käyttämään GPT-4 mallia.  Esimerkki vastausten tasossa on dokumentissa 'Diff_btw_gpt35_gpt4_Story' """
    openai.api_key = OPENAI_API_KEY

    if request.method == 'GET':
        roll = request.GET.get('roll', '')
        storystyle = request.GET.get('storystyle', '')
        story = Story.objects.get(name=f'{storystyle}')
        name = story.name
        style = story.styles
        # temp = float(story.temp)
        # response = openai.Completion.create(
        #     engine=model_completions,
        #     prompt=f'Use {name}, {style} as a theme. Write a short story containing the following words: {roll}.',
        #     temperature=0.8,
        #     # temperature=temp,
        #     max_tokens=650,
        # )
        # tarina = response.choices[0].text

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": f"Use {name}, {style} as a theme"},
                {"role": "user", "content": f"Write a short story containing the following words: {roll}."},
                # {"role": "user", "content": f"{chatquery}"},
                # {"role": "user", "content": f"{content_query}"},
            ]
        )

        reply = completion.choices[0].message['content']
        # print(reply)

        # print(f'Query Tokens: {response.usage.prompt_tokens}\nResponse Tokens: {response.usage.completion_tokens}')
        context = {
            'result': reply
        }
        return render(request, 'partials/readoutloud.html', {'context': context})
    return render(request, "index.html")


def readoutloud(request):
    """ Luetaan esimerkiksi AIn tuottama tarina ääneen. Hyvä. Tarvitaan vain pari kirjastoa. Check msu/tts_lang.py for
    supported languages """
    if request.method == "GET":
        readthis = request.GET.get("readme", "")
        # tts_2 = gtts.gTTS(f'{readthis}', lang="de")
        # tts_3 = gtts.gTTS(f'{readthis}', lang="fi")
        tts = gtts.gTTS(f'{readthis}')
        tts.save("answ.mp3")
        playsound("answ.mp3")
        return HttpResponse('Read it out')
    return render(request,  "index.html")


def storycubesimage(request):
    """ The function first sets the openai.org and openai.api_key variables to some predefined constants
    OPENAI_ORG and OPENAI_API_KEY. It then retrieves a value from the GET data of the request object by looking up
    the key "animal" in the GET dictionary. If the "animal" key is not found, the default value "" (empty string) is
    used. Next, the code constructs a prompt for the image generation by concatenating the animal_kuvaksi value with
    the string "naivistic art". The code then calls the openai.Image.create method, passing in the prompt and several
    other arguments to specify the number of images to generate and the size of the images. The method returns a
    dictionary containing data about the generated images. Finally, the function returns an HTTP response using the
    HttpResponse function, which is a class in the Django web framework for returning HTTP responses. The response
    text is an HTML img tag that displays the image at the URL stored in the image_url variable, which is set to the
    URL of the first image in the data attribute of the dictionary returned by the openai.Image.create method. This
    content was created by chatGPT."""

    openai.organization = OPENAI_ORG
    openai.api_key = OPENAI_API_KEY
    if request.method == 'GET':
        to_img = request.GET.get("readme", "")
        style = request.GET.get('storystyle', '')
        styles = Story.objects.get(name=f'{style}')
        prompt = f'create detailed representative fotorealistic cartoon image following story "{to_img[0:240]}". Use ' \
                 f'styles ({styles}) for theme'
        r = openai.Image.create(
            prompt=f'{prompt}',
            n=1,
            size='512x512')
        storycube_url = r['data'][0]['url']
        context = {
            'storycube_url': storycube_url
        }
        return render(request, 'partials/storycubesimage.html', {'context': context})

    return render(request, "index.html")


def savestory(request):
    if request.method == "POST":
        name = request.POST["readme"][0:50]
        content = request.POST["readme"]
        rolls = request.POST["roll"]
        image_url = request.POST['storycube_url']
        response = requests.get(image_url)

        path = Path('media/images/image.jpg')
        image = '{}{}'.format(uuid.uuid4(), path.suffix)
        with open(f'media/images/{image}', 'wb') as f:
            f.write(response.content)

        completestory = Completestory.completestorytalteen(name, content, rolls, image)
        completestory.save()
        return HttpResponse('Saved!')
    return HttpResponse('hmm, not correct yet')


def schufflecards(request):
    openai.organization = OPENAI_ORG
    openai.api_key = OPENAI_API_KEY
    cards = [
        'Diamonds',
        'Spades',
        'Hearts',
        'Clubs',
    ]
    ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King', 'Ace']
    pick = []
    i = 0

    while i < 3:
        card = random.choices(cards)
        rank = random.choices(ranks)
        pick.append('{} of {}'.format(rank[0], card[0]))
        i = i+1

    # print(pick)

    prompt = f'image of a card dealer in leather tie holding cards {pick}. Detailed, photorealistic, 4k'
    r = openai.Image.create(
        prompt=f'{prompt}',
        n=1,
        size='256x256')
    image = r['data'][0]['url']
    return HttpResponse(f'<img src="{image}" style="width: 200px"><p><small>AI is still evolving. Request was for '
                        f'"image of a card dealer in leather tie holding cards {pick}. Detailed, '
                        f'photorealistic"</small></p><p><small>Cards were picked randomly by my code</small></p>')


