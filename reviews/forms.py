from django import forms
from django.core.exceptions import ValidationError

from reviews.models import Review

DUPLICATE_REVIEW_ERROR = "You have already reviewed this book."
RATING_CHOICES = [(rating, str(rating)) for rating in range(1, 6)]


class BookSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Book title",
    )
    min_rating = forms.TypedChoiceField(
        required=False,
        choices=[("", "Any rating"), *RATING_CHOICES],
        coerce=int,
        empty_value=None,
        label="Minimum rating",
    )


class ReviewForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea,
        error_messages={"required": "Review text cannot be empty."},
    )
    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
    )

    class Meta:
        model = Review
        fields = ("text", "rating")

    def __init__(self, *args, user, book, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.book = book

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if not text:
            raise ValidationError("Review text cannot be empty.")
        return text

    def clean(self):
        cleaned_data = super().clean()
        duplicate_reviews = Review.objects.filter(
            user=self.user,
            book=self.book,
        )
        if self.instance.pk:
            duplicate_reviews = duplicate_reviews.exclude(pk=self.instance.pk)
        if duplicate_reviews.exists():
            raise ValidationError(DUPLICATE_REVIEW_ERROR)
        return cleaned_data

    def save(self, commit=True):
        review = super().save(commit=False)
        review.user = self.user
        review.book = self.book
        if commit:
            review.save()
        return review
