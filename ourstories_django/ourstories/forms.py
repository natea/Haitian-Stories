from ourstories import models

from django import forms
from django.conf import settings

from hashlib import sha1 as hash_func
import time

SIGNATURE_EXPIRY_INTERVAL = 60*60 # one hour # (in seconds)

def sign_value(value, expiry_delay=SIGNATURE_EXPIRY_INTERVAL):
    expiry_time = int(time.time()) + expiry_delay

    plaintext = ':'.join([settings.SECRET_KEY,
                          str(expiry_time),
                          str(value)])
    return "%d,%s" % (expiry_time, hash_func(plaintext).hexdigest())

def check_signed_value(value, sig):
    parts = str(sig).split(",", 1) # split only once

    if len(parts) != 2:
        return False

    expiry_time = parts[0]
    sigdigest = parts[1]

    if int(expiry_time) < time.time():
        return False
        
    plaintext = ':'.join([settings.SECRET_KEY,
                          str(expiry_time),
                          str(value)])
        
    return hash_func(plaintext).hexdigest() == sigdigest



class CityChoiceField(forms.ChoiceField):
    def clean(self, value):
        if not value:
            return None
        try:
            value = int(value)
        except ValueError:
            raise forms.ValidationError("Please select a valid city.")

        try:
            ci = models.City.objects.get(pk=value)
            return ci.id
        except models.City.DoesNotExist:
            raise forms.ValidationError("Please select a valid city.")


class SearchForm(forms.Form):
    """ Form used for (advanced) search queries
    @todo: This can (obviously) still be expanded; really depends on what we need
    """
    q = forms.CharField(label='Containing text', required=False)
    storytype = forms.ChoiceField(label='Story Type', choices=[('','--all--')]+list(models.STORYTYPE_CHOICES), required=False)
    category = forms.ChoiceField(label='Category', choices=(), required=False)
    language = forms.ChoiceField(label='Language', choices=(), required=False)
    country = forms.ChoiceField(label='Country', choices=(), required=False)
    gender = forms.ChoiceField(label='Contributor gender', choices=(('','--all--'),('M', 'Male'), ('F', 'Female')), required=False)
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        # Set up these choices dynamically, so that any changes in the models are automatically picked up
        self.fields['category'].choices = [('', '--all--')] + [(category.name, category.name) for category in models.Category.objects.all()]
        self.fields['language'].choices = [('', '--all--')] + [(language.name, language.name) for language in models.Language.objects.all()]
        self.fields['country'].choices = [('', '--all--')] + [(country.name, country.name) for country in models.Country.objects.all()]




class StoryForm(forms.Form):

    name = forms.CharField(label="Your Name")
    email = forms.EmailField(required=False)
    age = forms.IntegerField(required=False)
    gender = forms.ChoiceField(widget=forms.RadioSelect,
                               choices=(('M', 'Male'), ('F', 'Female')),
                               required=False)

    title = forms.CharField(label="Story Title")
    summary = forms.CharField(label="Story Text",
                              widget=forms.Textarea)

    language = forms.ChoiceField(required=True,
                                 choices=[ (l.id, l.name) for l in models.Language.objects.all() ])

    country = forms.ChoiceField(required=True,
                                choices=[('','Please select:')]+[ (c.pk, c.name) for c in models.Country.objects.all() ])
    city = CityChoiceField(required=False,
                           choices=[('','')]) # +[ (c.id, c.name) for c in models.City.objects.all() ]

    _storytype = forms.CharField(widget=forms.HiddenInput(), required=True)
    _storytype_sig = forms.CharField(widget=forms.HiddenInput(), required=True)
    _link = forms.CharField(widget=forms.HiddenInput(), required=False)
    _link_sig = forms.CharField(widget=forms.HiddenInput(), required=False)



    def __init__(self, _link=None, _storytype=None, *args, **kwargs):
        super(StoryForm, self).__init__(*args, **kwargs)
        if _storytype:
            self.fields["_storytype"].initial = _storytype
            self.fields["_storytype_sig"].initial = sign_value(_storytype)
        if _link:
            self.fields["_link"].initial = _link
            self.fields["_link_sig"].initial = sign_value(_link)

    def clean(self):
        for fieldname in ('_storytype', '_link'):
            value = self.cleaned_data.get(fieldname)
            sig = self.cleaned_data.get(fieldname+"_sig")

            if value and sig and check_signed_value(value, sig):
                pass #OK
            else:
                self.cleaned_data[fieldname] = None

        storytype = self.cleaned_data.get("_storytype")
        link = self.cleaned_data.get("_link")

        if storytype == "text":
            self.cleaned_data["_link"] = None

        return self.cleaned_data



    def clean_country(self):
        """Country must be an integer ID; empty is not really allowed even
        thought it's supported in the choices."""
        try:
            data = self.cleaned_data['country']
        except ValueError:
            data = None

        if not(data):
            raise forms.ValidationError("Please select your country.")

        # Always return the cleaned data, whether you have changed it or
        # not.
        return data


    def save(self):
        assert self.is_valid()

        d = self.cleaned_data

        contrib = models.Contributor(name=d["name"],
                                     email=d["email"],
                                     age=d["age"],
                                     gender=d["gender"])
        contrib.save()

        try:
            country = models.Country.objects.get(pk=d["country"])
        except models.Country.DoesNotExist:
            country = None

        try:
            city_id = int(d["city"])
        except (ValueError, TypeError):
            city_id = None

        try:
            language_id = int(d["language"])
        except (ValueError, TypeError):
            language_id = None

        s = models.Story(title=d["title"],
                         summary=d["summary"],
                         language_id=language_id,
                         city_id=city_id,
                         country=country,
                         contributor=contrib,
                         link=d["_link"],
                         storytype=d["_storytype"],
                         is_published = True) # with this step coming AFTER recording, stories will always be published when created.
        s.save()

        return s
