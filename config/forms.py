from django import forms
from django.core.exceptions import ValidationError

from .models import Advert, Reviews



class AdvertForm(forms.ModelForm):
    description = forms.CharField(min_length=20)

    class Meta:
        model = Advert
        fields = ['user', 'category', 'filters', 'date', 'subject', 'description', 'images', 'file', 'price', 'slug',]

    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data.get("description")
        user = cleaned_data.get("user")

        if user == description:
            raise ValidationError(
                "Описание не должно быть идентично названию."
            )

        return cleaned_data


class ReviewForm(forms.ModelForm):
    """Форма отзыва"""
    class Meta:
        model = Reviews
        fields = ("user", "email", "text",)