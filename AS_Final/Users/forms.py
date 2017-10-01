from django import forms

from .models import Blog_Post

class BlogPostForm(forms.ModelForm):

    class Meta:
        model = Blog_Post
        fields = ('Title', 'Content')