from django import forms


class AllForm(forms.Form):
    toemoji_movie = forms.CharField(
        label='Movie name',
        max_length=32,
        widget=forms.TextInput(
            attrs={
                'onfocus': "this.value=''",
                "class": "form-control",
                "placeholder": "What's Your favourite movie?"
            })
    )

    studypoints = forms.CharField(
        max_length=64,
        widget=forms.TextInput(
            attrs={
                'onfocus': "this.value=''",
                "class": "form-control",
                "placeholder": "5 key points to know about.."
            })
    )

    author = forms.CharField(
        max_length=32,
        widget=forms.TextInput(
            attrs={
                'onfocus': "this.value=''",
                "class": "form-control",
                "placeholder": "American writer.."
            })
    )

    book = forms.CharField(
        max_length=64,
        widget=forms.TextInput(
            attrs={
                'onfocus': "this.value=''",
                "class": "form-control",
                "placeholder": "Book.."
            })
    )

    stars = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'cols': 36,
                'placeholder': "Astronomy.."
            })
    )

    askanything = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'cols': 36,
                'placeholder': "Answer limited to 350 words.."
            })
    )

    artquestion = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'cols': 36,
                'placeholder': "Art question..",
                'class': 'w3-margin-bottom'
            })
    )

    ART_STYLE_CHOICES = (
        ('Impressionism', 'Impressionism'),
        ('Abstract Expressionism', 'Abstract Expressionism'),
        ('Fauvism', 'Fauvism'),
        ('Cubism', 'Cubism'),
        ('Surrealism', 'Surrealism'),
    )

    artstyle = forms.ChoiceField(
        choices=ART_STYLE_CHOICES,
        widget=forms.RadioSelect(
            attrs={
                'class': 'w3-row'
            })
    )

    codepython = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'cols': 36,
                'onfocus': "this.value=''",
                'placeholder': "Ask for some neat code.."
            })
    )

    askbuffet = forms.CharField(
        max_length=32,
        widget=forms.TextInput(
            attrs={
                'onfocus': "this.value=''",
                "class": "form-control",
                "placeholder": "Give HEX 25 Company.."
            })
    )

    turbomode = forms.CharField(
        max_length=64,
        widget=forms.TextInput(
            attrs={
                'onfocus': "this.value=''",
                "class": "form-control",
                "placeholder": "Chat with GPT-4.."
            })
    )

    getscience = forms.CharField(
        max_length=64,
        widget=forms.TextInput(
            attrs={
                'onfocus': "this.value=''",
                "class": "form-control",
                "placeholder": "give field of science"
            })
    )

    justdraw = forms.CharField(
        max_length=32,
        widget=forms.TextInput(
            attrs={
                'onfocus': "this.value=''",
                "class": "form-control",
                "placeholder": "what you want me to draw"
            })
    )

    comparedocsone = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 8,
                'cols': 36,
                'placeholder': "Drop document 1 here"
            })
    )

    comparedocstwo = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 8,
                'cols': 36,
                'placeholder': "Drop document 2 here"
            })
    )

    whatsup = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 8,
                'cols': 36,
                'placeholder': "Ask for Joe Biden latest remarks on climate and ask for comparison to earlier "
                               "presidents remarks"
            })
    )

    analysedoc = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 8,
                'cols': 36,
                'placeholder': "Drop link to pdf here.."
            })
    )