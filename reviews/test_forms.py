import pytest
from django.contrib.auth import get_user_model

from reviews.forms import BookSearchForm, ReviewForm
from reviews.models import Book, Review


def test_book_search_form_fields_are_optional():
    form = BookSearchForm({})

    assert form.is_valid()
    assert form.cleaned_data == {"q": "", "min_rating": None}


def test_book_search_form_trims_query():
    form = BookSearchForm({"q": "  dUnE  "})

    assert form.is_valid()
    assert form.cleaned_data["q"] == "dUnE"


@pytest.mark.parametrize("rating", ["1", "5"])
def test_book_search_form_accepts_and_coerces_rating_boundaries(rating):
    form = BookSearchForm({"min_rating": rating})

    assert form.is_valid()
    assert form.cleaned_data["min_rating"] == int(rating)


@pytest.mark.parametrize("rating", ["0", "6", "invalid"])
def test_book_search_form_rejects_invalid_minimum_rating(rating):
    form = BookSearchForm({"min_rating": rating})

    assert not form.is_valid()
    assert "min_rating" in form.errors


@pytest.mark.django_db
class TestReviewForm:
    user = None
    book = None

    def setup_method(self):
        self.user = get_user_model().objects.create_user(username="alice")
        self.book = Book.objects.create(title="Dune")

    def make_form(self, data, **kwargs):
        return ReviewForm(
            data=data,
            user=self.user,
            book=self.book,
            **kwargs,
        )

    def test_public_fields_are_limited_to_text_and_rating(self):
        form = self.make_form({})

        assert list(form.fields) == ["text", "rating"]
        assert [choice[0] for choice in form.fields["rating"].choices] == [
            1,
            2,
            3,
            4,
            5,
        ]

    @pytest.mark.parametrize("text", ["", "   "])
    def test_empty_or_whitespace_only_text_is_invalid(self, text):
        form = self.make_form({"text": text, "rating": "4"})

        assert not form.is_valid()
        assert "text" in form.errors

    def test_text_is_trimmed(self):
        form = self.make_form({"text": "  Thoughtful review.  ", "rating": "4"})

        assert form.is_valid()
        assert form.cleaned_data["text"] == "Thoughtful review."

    @pytest.mark.parametrize("rating", ["", "0", "6", "invalid"])
    def test_missing_or_invalid_rating_is_rejected(self, rating):
        form = self.make_form({"text": "Thoughtful review.", "rating": rating})

        assert not form.is_valid()
        assert "rating" in form.errors

    def test_duplicate_review_is_a_non_field_error(self):
        Review.objects.create(
            text="Existing review.",
            rating=4,
            user=self.user,
            book=self.book,
        )
        form = self.make_form({"text": "Another review.", "rating": "5"})

        assert not form.is_valid()
        assert "already reviewed" in form.non_field_errors()[0]

    def test_current_instance_is_excluded_from_duplicate_check(self):
        review = Review.objects.create(
            text="Existing review.",
            rating=4,
            user=self.user,
            book=self.book,
        )
        form = self.make_form(
            {"text": "Updated review.", "rating": "5"},
            instance=review,
        )

        assert form.is_valid()

    def test_save_uses_trusted_user_and_book_context(self):
        other_user = get_user_model().objects.create_user(username="mallory")
        other_book = Book.objects.create(title="Foundation")
        form = self.make_form(
            {
                "text": "Trusted relationships.",
                "rating": "5",
                "user": other_user.pk,
                "book": other_book.pk,
            }
        )

        assert form.is_valid()
        review = form.save()
        assert review.user == self.user
        assert review.book == self.book
