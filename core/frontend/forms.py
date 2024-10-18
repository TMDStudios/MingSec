from django import forms

class CamRequestForm(forms.Form):
    cam_type = forms.ChoiceField(choices=[('image', 'Image'), ('video', 'Video'), ('status', 'Status')])
    camera = forms.ChoiceField(choices=[('pc', 'Main'), ('external', 'External')])
    length = forms.IntegerField(required=False, min_value=1, max_value=60, help_text="Length in seconds (1-60)")