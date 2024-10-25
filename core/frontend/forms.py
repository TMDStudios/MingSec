from django import forms

class CamRequestForm(forms.Form):
    cam_type = forms.ChoiceField(choices=[('image', 'IMAGE'), ('video', 'VIDEO'), ('status', 'STATUS')])
    camera = forms.ChoiceField(choices=[('pc', 'MAIN'), ('external', 'EXTERNAL')])
    length = forms.IntegerField(required=False, min_value=1, max_value=60, widget=forms.TextInput(attrs={'placeholder': 'Optional (1-60 seconds)'}))

    def clean_length(self):
        length = self.cleaned_data.get('length')
        if length is None:
            return 10
        return length