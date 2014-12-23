from django import forms
from .models import Subtitle

class SubtitleForm(forms.ModelForm):
    class Meta:
        model = Subtitle
        fields = ['state', 'time_processed_transcribing', 'time_processed_syncing', 'time_quality_check_done', 'time_processed_translating']

    def clean(self):
        cleaned_data = super(SubtitleForm, self).clean()
        my_obj = self.instance

        for k,v in cleaned_data.items():
            if v is None:
                cleaned_data[k] = my_obj.__dict__[k]

        if cleaned_data['time_processed_transcribing'] > my_obj.talk.video_duration:
           self._errors['time_processed_transcribing'] = self.error_class(['Time longer than the talk.'])
        print(cleaned_data)
        if cleaned_data['time_processed_syncing'] > my_obj.talk.video_duration:
           self._errors['time_processed_syncing'] = self.error_class(['Time longer than the talk.'])
        if cleaned_data['time_quality_check_done'] > my_obj.talk.video_duration:
           self._errors['time_quality_check_done'] = self.error_class(['Time longer than the talk.'])
        if cleaned_data['time_processed_translating'] > my_obj.talk.video_duration:
           self._errors['time_processed_translating'] = self.error_class(['Time longer than the talk.'])
        return cleaned_data
