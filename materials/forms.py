from django import forms
from taggit.forms import TagWidget

from .models import StudyMaterial, Category, Subject
from .utils import validate_upload_file


class StudyMaterialForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        help_text='Comma-separated tags',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. notes, exam, chapter-3'}),
    )

    class Meta:
        model = StudyMaterial
        fields = [
            'title', 'description', 'subject', 'category',
            'semester', 'file', 'thumbnail',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-input'}),
            'semester': forms.NumberInput(attrs={'min': 1, 'max': 12, 'class': 'form-input'}),
            'subject': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'file': forms.FileInput(attrs={'class': 'form-input'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['subject'].required = False
        self.fields['category'].required = False
        self.fields['file'].required = True
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = ', '.join(
                self.instance.tags.names()
            )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            validate_upload_file(file)
        elif not self.instance.pk:
            raise forms.ValidationError('Please upload a file.')
        return file

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.uploaded_by = self.user
        if instance.file and not instance.file_size:
            instance.file_size = instance.file.size
            instance.file_type = instance.detect_file_type()
        if commit:
            instance.save()
            tags = self.cleaned_data.get('tags_input', '')
            if tags:
                instance.tags.set([t.strip() for t in tags.split(',') if t.strip()])
            else:
                instance.tags.clear()
        return instance


class MaterialFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search materials...',
        'class': 'search-input',
    }))
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=False, empty_label='All Subjects')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label='All Categories')
    file_type = forms.ChoiceField(
        choices=[('', 'All Types')] + StudyMaterial.FILE_TYPES,
        required=False,
    )
    semester = forms.IntegerField(required=False, min_value=1, max_value=12)
    uploader = forms.CharField(required=False)
    sort = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest'),
            ('created_at', 'Oldest'),
            ('-download_count', 'Most Downloaded'),
            ('-view_count', 'Most Viewed'),
            ('title', 'Title A-Z'),
        ],
        required=False,
        initial='-created_at',
    )
