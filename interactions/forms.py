from django import forms

from .models import Comment, Rating, Report


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share your thoughts...',
                'class': 'comment-input',
            }),
        }


class RatingForm(forms.Form):
    score = forms.IntegerField(min_value=1, max_value=5)


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('reason', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
