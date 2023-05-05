import PyPDF2
import requests
import logging
import uuid
from pathlib import Path

import openai
import random
import gtts
from playsound import playsound
import re

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import Template, RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from animals.forms import AllForm
from animals.models import Chat, Personality, Story, Completestory, Djangoaiuser

logger = logging.getLogger(__name__)
# model_coding = 'code-davinci-002'
model_coding = 'gpt-3.5-turbo'
# engine_completions = 'text-davinci-003'
model_completions = 'text-davinci-003'
# model_chat = 'gpt-3.5-turbo'
model_chat = 'gpt-4'
model_embedding = 'text-embedding-ada-002'
# size_parameter defines the chunk that is possible to send to chatGPT in one time
size_parameter = 18000
turbomode_messages = [{"role": "system", "content": ""}]


def logout(request):
    logout(request)


@login_required
def startindex(request):
    userin = request.user.username
    OPENAI_API_KEY = Djangoaiuser.objects.get(username__exact=userin).openaikey
    form = AllForm
    return render(request, "index.html", {'form': form})


@login_required
def indexexamples(request):
    return render(request, 'indexexamples.html')


def indexexampleopen(request, id):
    form = AllForm
    context = {
        'form': form
    }
    tool = 'index.html'
    start = f'<div id="{id}"'
    html = render_to_string(tool, context)
    start_index = html.find(start)
    end_index = html.find('<br>', start_index)
    extracted = html[start_index:end_index + + len('</div></div>')]
    extracted_html = f'{extracted}</div></div>'

    template_string = extracted_html
    template = Template(template_string)
    context = RequestContext(request)
    rendered_template = template.render(context)

    return render(request, 'partials/indexlanding.html', {'rendered_template': rendered_template})


def toemoji(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        movie = request.GET.get("toemoji_movie", '')
        logger.info(movie)
        prompt = f'Convert movie titles into emoji.\n\nBack to the Future: 👨👴🚗🕒 \nBatman: 🤵🦇 \nTransformers: 🚗🤖 ' \
                 f'\nLord of the Ring:Return of the King: 🧙💍:🤴🔙\n{movie}'
        response = openai.Completion.create(
            model=model_completions,
            prompt=prompt,
        )
        result = response.choices[0].text
        return HttpResponse(f'<h3>{movie}{result}</h3>')
    return render(request, "index.html")


def studypoints(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        studypoint = request.GET.get("studypoints", '')
        logger.info(studypoint)
        prompt = f'What are 5 key points I should know when studying {studypoint}? Answer with an html bulleted list'
        response = openai.Completion.create(
            model=model_completions,
            prompt=prompt,
            temperature=0.3,
            max_tokens=450,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        result = response.choices[0].text
        return HttpResponse(f'{result}')
    return render(request, "index.html")


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

    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == "GET":
        animal_to_pic = request.GET.get("animal", "")
        prompt = f'{animal_to_pic} fotorealistic cool cartoon style'
        r = openai.Image.create(
            prompt=f'{prompt}',
            n=1,
            size='512x512')
        image_url = r['data'][0]['url']

        return HttpResponse(f'<img src="{image_url}" style="width: 250px">')
    return render(request, "index.html")


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

    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == "GET":
        animal = request.GET.get('animal', '')
        # animal = request.POST["animal"]
        # logger.info(animal)
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


def kirjallisuus(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        author = request.GET.get('author', '')
        book = request.GET.get('book', '')

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": "You are a literature reviewer understanding especially well classical "
                                              "american literature."},
                {"role": "user", "content": f"Please write a short summary of book {book} by {author} using "
                                            f"his/her own writing style. Limit your answer to 100 words"},
            ]
        )

        reply = completion.choices[0].message['content']

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": "You are a writer with great sence of classical poetry"},
                {"role": "user", "content": f"Please write a representative poem about book {book} by {author}."
                                            f" Limit your answer to 50 words"},
            ]
        )

        poem = completion.choices[0].message['content']

        prompt = f'{reply[0:320]}'
        r = openai.Image.create(
            prompt=f'{prompt}',
            n=1,
            size='256x256')
        image_url = r['data'][0]['url']

        return HttpResponse(f'<p>{reply}</p><img src="{image_url}" style="width: 250px"><p class="w3-small"><pre>{poem}</pre></p>')

    return render(request, "index.html")


def stars(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        spacethought = request.GET.get('stars', '')

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": "use scientific terms on your answer"},
                {"role": "user", "content": f"{spacethought}"},
            ]
        )

        reply = completion.choices[0].message['content']

        return HttpResponse(f'<p>{reply}</p>')
    return render(request, "index.html")


def askanything(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        anyquestion = request.GET.get('askanything', '')
        turbomode_messages = [{"role": "system", "content": ""}]
        turbomode_messages[0] = {
            "role": "system",
            "content": "Answer always correctly"
        }
        turbomode_messages.append(
            {
                "role": "user",
                "content": f"{anyquestion} Use max 350 words"
            }
        )
        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=turbomode_messages,
        )
        reply = completion.choices[0].message['content']

        return HttpResponse(f'<p>{reply}</p>')
    return render(request, "index.html")


def artquestion(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == "GET":
        question = request.GET.get("artquestion", "")
        artstyle = request.GET.get("artstyle", "")
        artstyle_ext = 'Contemporary'

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": f"You are an arts expert who highly values {artstyle_ext} art"},
                {"role": "user", "content": f"{question}. Consider art style: {artstyle}"},
            ]
        )
        reply = completion.choices[0].message['content']

        return HttpResponse(f'<textarea name="artanswer" rows="7" cols="40" style="border: none">{reply}</textarea>')

    return render(request, "index.html")


def tyylitaulu(request):
    """ This function takes kysymys() result and uses it as a prompt to create DALLE2 image """
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    vastaus_kuvaksi_hx = request.GET.get('artanswer', '')
    prompt = f'{vastaus_kuvaksi_hx[0:320]}'
    r = openai.Image.create(
        prompt=f'{prompt}',
        n=1,
        size='256x256')
    image_url = r['data'][0]['url']

    return HttpResponse(f'<img src="{image_url}" style="width: 250px">')


def codepython(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        codethought = request.GET.get('codepython', '')

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": 'You are system that is always using standards'},
                {"role": "user", "content": f"{codethought}"},
            ]
        )

        reply = completion.choices[0].message['content']
        logger.info(reply)
        context = {
            'code_result': reply,
        }
        return render(request, 'partials/code_python.html', {'context': context})
    return render(request, "index.html")


def askbuffet(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        company = request.GET.get("askbuffet", '')
        turbomode_messages = [{"role": "system", "content": ""}]
        turbomode_messages[0] = {
            "role": "system",
            "content": "You are a talented and polite Financial Analyst knowing only the OMX Helsinki Stocks. You will"
                       "use book closing day data that you have access to, 2020 or 2021. You can perform at least the"
                       "following indicators: P/E, P/B, EV/EBIT and DIV/P, which you always"
                       "include in your answer (in html tagged table format) even if not asked for. First present the "
                       f"company {company} with few words. Then give short analysis on the latest indicators. In a "
                       f"separate html <p> paragraph at the end of your report write a short conclusion of book "
                       f"closing day financials over three earlier years. Name that paragraph 'Summary'."
        }
        turbomode_messages.append(
            {
                "role": "user",
                "content": f"analyse {company}"
            }
        )

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=turbomode_messages,
        )

        reply = completion.choices[0].message['content']

        return HttpResponse(f'<p>Warren thinks you are a smartass!</p>{reply}')
    return render(request, "index.html")


def schufflecards(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
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
        i = i + 1

    prompt = f'image of a card dealer in leather tie holding cards {pick}. Detailed, photorealistic, 4k'
    r = openai.Image.create(
        prompt=f'{prompt}',
        n=1,
        size='256x256')
    image = r['data'][0]['url']
    return HttpResponse(f'<img src="{image}" style="width: 200px"><p><small>AI is still evolving. Request was for '
                        f'"image of a card dealer in leather tie holding cards {pick}. Detailed, '
                        f'photorealistic"</small></p><p><small>Cards were picked randomly</small></p>')


def turbomode(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == "GET":
        stylemode = request.GET.get("stylemode", '')
        chatquery = request.GET.get("turbomode", '')
        systemcontent = Personality.objects.get(name='ai').character
        request.session['personality'] = stylemode
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
        elif stylemode == 'zlatan':
            systemcontent = Personality.objects.get(name='zlatan').character

        if 'this_chat' in request.session:
            request.session['this_chat'] += f'/n{user}: {chatquery}'
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
        request.session['this_chat'] += f'/n{assistant}: {reply}'
        turbomode_messages.append(
            {
                "role": "assistant",
                "content": f"{reply}"
            }
        )

        chat_reply = request.session['this_chat']
        chat_rows = re.split("/n", chat_reply)
        context = {
            'chat_rows': chat_rows,
        }
        return render(request, 'partials/chat_dialogue.html', {'context': context})
    return render(request, "index.html")


def flushchat(request):
    """ Tyhjennetään (alustetaan) luettujen lista"""
    if 'this_chat' in request.session:
        chats_dialoque = request.session['this_chat']
        chats_name = chats_dialoque[:23]
        chat = Chat.talteen(chats_name, chats_dialoque, request.session['personality'])
        chat.save()
        del request.session['this_chat']
        del request.session['personality']
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
    chat_rows = re.split("/n", chat_info)

    context = {
        'chat_id': id,
        'chat_name': chat_name,
        'chat_time': chat_time,
        'chat_rows': chat_rows,
    }
    return render(request, 'partials/chat_modal.html', {'context': context})


def chatimage(request, chat_id):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        modal = Chat.objects.get(id=chat_id).personality.character
        prompt = f'Generate a creative and engaging Dall-E prompt for an image using "{modal}" as your inspiration. ' \
                 f'Photorealistic. Canon EOS. Bokeh. Drone photography.'
        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": 'You are system that knows about photography and is always creative'},
                {"role": "user", "content": f"{prompt}"},
            ]
        )

        prompt = completion.choices[0].message['content']
        openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
        r = openai.Image.create(
            prompt=f'{prompt}',
            n=1,
            size='512x512')
        image_url = r['data'][0]['url']

        return HttpResponse(f'<img src="{image_url}" style="width: 250px">')
    return render(request, "index.html")


def rolldicies(request):
    playsound("animals/static/dice.mp3")
    cubes = [
        [
            'pyramid',
            'credit card',
            'sustainability',
            'tower',
            'tree',
            'eye'
        ],
        [
            'unhappy but ready',
            'question',
            'fountain',
            'rusty key',
            'teepee',
            'shooting star'
        ],
        [
            'cube',
            'magnifier glass',
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
            'insect',
            'magical',
            'counter',
            'book',
            'bridge'
        ],
        [
            'phrase',
            'sleepy',
            'lamp',
            'house',
            'time',
            'arrow up'
        ],
        [
            'magnetic',
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
            'happy and ready',
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
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey

    if request.method == "GET":
        roll = request.GET.get('roll', '')
        storystyle = request.GET.get('storystyle', '')
        story = Story.objects.get(name=f'{storystyle}')
        name = story.name
        style = story.styles

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=[
                {"role": "system", "content": f"Use {name}, {style} as a theme"},
                {"role": "user", "content": f"Write a short story containing the following words: {roll}."},
            ]
        )

        reply = completion.choices[0].message['content']
        context = {
            'result': reply
        }
        return render(request, 'partials/readoutloud.html', {'context': context})
    return render(request, "index.html")


def readoutloud(request):
    """ Luetaan esimerkiksi AIn tuottama tarina ääneen. Hyvä. Tarvitaan vain pari kirjastoa. Check msu/tts_lang.py for
    supported languages. Suomeksi tts_fi = gtts.gTTS(f'{readthis}', lang="fi")"""
    if request.method == "GET":
        readthis = request.GET.get("readme", "")
        tts = gtts.gTTS(f'{readthis}')
        tts.save("answ.mp3")
        playsound("answ.mp3")
        return HttpResponse('Read it out')
    return render(request, "index.html")


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

    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey

    if request.method == "GET":
        to_img = request.GET.get('readme', '')
        style = request.GET.get('storystyle', '')
        styles = Story.objects.get(name=f'{style}')
        prompt = f'detailed representative photorealistic illustration by Moebius following story "{to_img[0:240]}". ' \
                 f'Use styles ({styles}) for theme.'
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
    if request.method == "GET":
        name = request.GET.get("readme", '')[0:50]
        content = request.GET.get("readme", '')
        rolls = request.GET.get("roll", '')
        image_url = request.GET.get('storycube_url', '')
        response = requests.get(image_url)

        path = Path('media/images/image.jpg')
        image = '{}{}'.format(uuid.uuid4(), path.suffix)
        with open(f'media/images/{image}', 'wb') as f:
            f.write(response.content)

        completestory = Completestory.completestorytalteen(name, content, rolls, image)
        completestory.save()
        return HttpResponse('Saved!')
    return HttpResponse('hmm, not correct yet')


def getscience(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        scienceq = request.GET.get("getscience", '')
        prompt = f'provide me with max 8 references and links on {scienceq} field'
        turbomode_messages = [{"role": "system", "content": ""}]
        turbomode_messages[0] = {
            "role": "system",
            "content": "Answer always correctly"
        }
        turbomode_messages.append(
            {
                "role": "user",
                "content": f"{prompt}. Reply in html table format."
            }
        )

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=turbomode_messages,
        )
        reply = completion.choices[0].message['content']

        return HttpResponse(f'{reply}')
    return render(request, "index.html")


def justdraw(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        drawrequest = request.GET.get("justdraw", '')
        logger.info(drawrequest)
        turbomode_messages = [{"role": "system", "content": ""}]
        turbomode_messages[0] = {
            "role": "system",
            "content": "You are able to draw some ASCII art"
        }
        turbomode_messages.append(
            {
                "role": "user",
                "content": f"use {drawrequest} as your ispiration"
            }
        )

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=turbomode_messages,
        )
        reply = completion.choices[0].message['content']

        return HttpResponse(f'<pre>{reply}</pre>')
    return render(request, "index.html")


def comparedocs(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        doc_one = request.GET.get("comparedocsone", '')
        doc_two = request.GET.get("comparedocstwo", '')
        turbomode_messages = [{"role": "system", "content": ""}]
        turbomode_messages[0] = {
            "role": "system",
            "content": "You can compare two documents scientifically"
        }
        turbomode_messages.append(
            {
                "role": "user",
                "content": f"read document {doc_one[:8000]} and document {doc_two[:8000]}. Reply with an idea of a "
                           f"prompt to compare them with some scientific approach."
            }
        )

        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=turbomode_messages,
        )
        reply = completion.choices[0].message['content']

        turbomode_messages.append(
            {
                "role": "assistant",
                "content": f'{reply}'
            }
        )
        prompt = reply
        turbomode_messages.append(
            {
                "role": "user",
                "content": f'{prompt} Reply with max 450 words.'
            }
        )
        completion = openai.ChatCompletion.create(
            model=model_chat,
            messages=turbomode_messages,
        )
        reply = completion.choices[0].message['content']

        return HttpResponse(f'<p><b>Comparison:</b>&nbsp;{reply}</p>')
    return render(request, "index.html")


def whatsup(request):
    """ fiscalnote.get_calendar_for_date_white_house_calendar__date__get: This endpoint retrieves information from
    the White House official calendar for a specified date.
    fiscalnote.list_biden_remarks_remarks_biden__get: This endpoint retrieves a list of remarks (spoken or written) made
    by President Joe Biden. You can optionally provide a query parameter to search for specific remarks.
    fiscalnote.search_articles_roll_call_articles__get: This endpoint allows you to search for news articles related to
    Congressional people and proceedings. You can provide a query parameter to specify the search criteria."""
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        newsquest = request.GET.get("whatsup", '')
        source_1 = 'fiscalnote.list_biden_remarks_remarks_biden__get latest five remarks'
        source_2 = 'fiscalnote.get_calendar_for_date_white_house_calendar__date__get date=February 10, 2023'
        source_3 = 'fiscalnote.search_articles_roll_call_articles__get'
        prompt = f"{newsquest} Consider utilizing {source_1}. please reply in html " \
                 "format and add tables when applicable. Add links to documents if they are available."
        response = openai.Completion.create(
            engine=model_completions,
            prompt=prompt,
            n=1,
            max_tokens=1024
        )
        result = response.choices[0].text
        return HttpResponse(f'{result}')
    return render(request, "index.html")


def analysedoc(request):
    """ e_u = 'https://julkaisut.valtioneuvosto.fi/bitstream/handle/10024/163864/VM_2022_12.pdf?sequence=1&isAllowed=y'
        e_lunes = 'https://www.lunes.fi/static/nados/docs/Lappi/rovaniemi_eelinm%C3%A4nty_p%C3%A4%C3%A4t%C3%B6s.pdf'"""
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    if request.method == 'GET':
        url = request.GET.get("analysedoc", '')
        r = requests.get(url, stream=True)

        if r.status_code != 200:
            return HttpResponse(f'Please give a valid url')
        else:
            with open('media/raw_example.pdf', 'wb') as f:
                f.write(r.content)

            EOF_MARKER = b'%%EOF'
            file_name = 'media/raw_example.pdf'

            with open(file_name, 'rb') as f:
                contents = f.read()

            if EOF_MARKER in contents:
                contents = contents.replace(EOF_MARKER, b'')
                contents = contents + EOF_MARKER
            else:
                contents = contents[:-6] + EOF_MARKER

            with open(file_name.replace('.pdf', '') + '_ready.pdf', 'wb') as f:
                f.write(contents)

            doc = 'media/raw_example_ready.pdf'
            pdf_file = open(doc, 'rb')
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            text_string = str(text)
            request.session['text_string'] = text_string
            doc_size = len(text_string)
            if doc_size < size_parameter:
                return makeanalysis(request)
            else:
                doc_share = int(round(size_parameter/doc_size, 2)*100)
                return render(request, 'partials/make_analysis.html', {'doc_share': doc_share})

    return render(request, "index.html")


def makeanalysis(request):
    turbomode_messages = [{"role": "system", "content": ""}]
    turbomode_messages[0] = {
        "role": "system",
        "content": "You are a University level Scientist who knows well how to analyse and review scientific "
                   "docs."
    }
    turbomode_messages.append(
        {
            "role": "user",
            "content": f"Identify the key findings and implications of this research paper: {request.session['text_string'][:size_parameter]}."
                       f"Summarize the main arguments at end."
        }
    )
    completion = openai.ChatCompletion.create(
        model=model_chat,
        messages=turbomode_messages,
    )
    reply = completion.choices[0].message['content']

    return HttpResponse(f'<p>{reply}</p>')


def doembedding(request):
    openai.api_key = Djangoaiuser.objects.get(username__exact=request.user.username).openaikey
    response = openai.Embedding.create(
        input="Your text string goes here",
        model="text-embedding-ada-002"
    )
    embeddings = response['data'][0]['embedding']

