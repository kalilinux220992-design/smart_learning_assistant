from django import forms


class YouTubePDFForm(forms.Form):
    video_url = forms.URLField(
        label='YouTube video URL',
        max_length=400,
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
    )
    local_video_path = forms.CharField(
        label='Or local video path',
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/home/user/videos/example.mp4'}),
    )
    interval = forms.CharField(
        label='Screenshot interval',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1 or 00:00:01'}),
    )
    min_uniqueness = forms.IntegerField(
        label='Minimum uniqueness (%)',
        min_value=0,
        max_value=100,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 70'}),
    )
