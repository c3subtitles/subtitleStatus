from django import forms
from .models import Subtitle, Event, Event_Days, Talk_Persons, Language
#import django_filters
import datetime

class SubtitleForm(forms.ModelForm):
    class Meta:
        model = Subtitle
        fields = ['time_processed_transcribing', 'time_processed_syncing', 'time_quality_check_done', 'time_processed_translating']

    def clean(self):
        cleaned_data = super(SubtitleForm, self).clean()
        my_obj = self.instance

        for k,v in cleaned_data.items():
            if v is None:
                cleaned_data[k] = my_obj.__dict__[k]

        if cleaned_data['time_processed_transcribing'] > my_obj.talk.video_duration:
           self._errors['time_processed_transcribing'] = self.error_class(['Time longer than the talk.'])
        if cleaned_data['time_processed_syncing'] > my_obj.talk.video_duration:
           self._errors['time_processed_syncing'] = self.error_class(['Time longer than the talk.'])
        if cleaned_data['time_quality_check_done'] > my_obj.talk.video_duration:
           self._errors['time_quality_check_done'] = self.error_class(['Time longer than the talk.'])
        if cleaned_data['time_processed_translating'] > my_obj.talk.video_duration:
           self._errors['time_processed_translating'] = self.error_class(['Time longer than the talk.'])
        # Trigger a complete amara update
        my_obj.talk.next_amara_activity_check = datetime.datetime.now()
        my_obj.talk.needs_complete_amara_update = True
        my_obj.talk.save()
        return cleaned_data

class TestForm(forms.Form):
    event_30c3 = forms.BooleanField(label = "30c3", required = False, initial = True)
    event_31c3 = forms.BooleanField(label = "31c3", required = False, initial = True)
    event_32c3 = forms.BooleanField(label = "32c3", required = False, initial = True)
    #event_33c3 = forms.BooleanField(label = "33c3", required = False, initial = True)

    lang_none = forms.BooleanField(label = "None", required = False, initial = True)
    lang_en = forms.BooleanField(label = "En", required = False, initial = True)
    lang_de = forms.BooleanField(label = "De", required = False, initial = True)

    day_1 = forms.BooleanField(label = "1", required = False, initial = True)
    day_2 = forms.BooleanField(label = "2", required = False, initial = True)
    day_3 = forms.BooleanField(label = "3", required = False, initial = True)
    day_4 = forms.BooleanField(label = "4", required = False, initial = True)

    sort_spm = forms.BooleanField(label = "sort by spm", required = False, initial = True)
    sort_asc = forms.BooleanField(label = "sort asc", required = False, initial = True)


class BForm(forms.Form):
    my_text = forms.CharField(label="Zu konvertierender Text:", widget=forms.Textarea(attrs={'rows':30, 'cols':100}))

    def clean_my_text(self):
        data = self.cleaned_data["my_text"]
        #data = data + "Ätsch"
        return data


class SimplePasteForm(forms.Form):
    text = forms.CharField(label='pad text',
                           min_length=1,
                           widget=forms.Textarea(attrs={'rows': 30,
                                                        'cols': 100}))
