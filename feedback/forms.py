
from django import forms

class FeedbackForm(forms.Form):
    # 你的欄位定義
    content = forms.CharField(widget=forms.Textarea)
