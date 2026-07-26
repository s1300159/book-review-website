from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_http_methods

from reviews.forms import BookSearchForm, DUPLICATE_REVIEW_ERROR, ReviewForm
from reviews.models import Book, Review

RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY = "recently_viewed_book_ids"


def _page(title, body):
    document = format_html(
        "<!doctype html><html><head><title>{}</title></head><body>{}</body></html>",
        title,
        body,
    )
    return HttpResponse(document)


def _record_recently_viewed_book(request, book_id):
    stored_ids = request.session.get(RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY, [])
    if not isinstance(stored_ids, list):
        stored_ids = []

    normalized_ids = []
    for stored_id in stored_ids:
        if (
            isinstance(stored_id, int)
            and not isinstance(stored_id, bool)
            and stored_id != book_id
            and stored_id not in normalized_ids
        ):
            normalized_ids.append(stored_id)

    request.session[RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] = [
        book_id,
        *normalized_ids,
    ][:5]


def _save_review_form(form):
    try:
        with transaction.atomic():
            return form.save()
    except IntegrityError:
        form.add_error(None, DUPLICATE_REVIEW_ERROR)
        return None


@require_GET
def home(request):
    del request
    body = format_html(
        '<h1>{}</h1><nav><a href="{}">{}</a> <a href="{}">{}</a></nav>',
        "Book Review Website",
        reverse("reviews:book_list"),
        "Books",
        reverse("reviews:book_search"),
        "Search",
    )
    return _page("Book Review Website", body)


@require_GET
def book_list(request):
    return render(
        request,
        "reviews/book_list.html",
        {"books": Book.objects.all()},
    )


@require_GET
def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    _record_recently_viewed_book(request, book.pk)
    reviews = book.reviews.select_related("user").order_by("-created_at", "-pk")
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    if user_review is None:
        review_action_url = reverse(
            "reviews:review_create",
            args=[book.pk],
        )
        if request.user.is_authenticated:
            review_action_label = "Write a review"
        else:
            review_action_label = "Log in to write a review"
    else:
        review_action_url = reverse(
            "reviews:review_edit",
            args=[user_review.pk],
        )
        review_action_label = "Edit your review"

    return render(
        request,
        "reviews/book_detail.html",
        {
            "book": book,
            "reviews": reviews,
            "average_rating": book.average_rating,
            "review_action_url": review_action_url,
            "review_action_label": review_action_label,
        },
    )


@require_GET
def book_search(request):
    form = BookSearchForm(request.GET)
    books = Book.objects.all()
    query = ""
    min_rating = None
    filters_applied = False

    if form.is_valid():
        query = form.cleaned_data["q"]
        min_rating = form.cleaned_data["min_rating"]
        if query:
            books = books.filter(title__icontains=query)
            filters_applied = True
        if min_rating is not None:
            books = books.annotate(search_average_rating=Avg("reviews__rating")).filter(
                search_average_rating__gte=min_rating
            )
            filters_applied = True
    else:
        books = Book.objects.none()

    show_no_results = filters_applied and not books.exists()
    return render(
        request,
        "reviews/book_search.html",
        {
            "form": form,
            "books": books,
            "query": query,
            "min_rating": min_rating,
            "show_no_results": show_no_results,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def review_create(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    form = ReviewForm(
        request.POST if request.method == "POST" else None,
        user=request.user,
        book=book,
    )
    if request.method == "POST" and form.is_valid():
        review = _save_review_form(form)
        if review is not None:
            messages.success(request, "Your review was created successfully.")
            return redirect("reviews:book_detail", book_id=book.pk)

    return render(
        request,
        "reviews/review_form.html",
        {
            "book": book,
            "form": form,
            "heading": "Write a review",
            "submit_label": "Post review",
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def review_edit(request, review_id):
    review = get_object_or_404(
        Review.objects.select_related("book", "user"),
        pk=review_id,
    )
    if review.user_id != request.user.pk:
        raise PermissionDenied

    form = ReviewForm(
        request.POST if request.method == "POST" else None,
        instance=review,
        user=request.user,
        book=review.book,
    )
    if request.method == "POST" and form.is_valid():
        saved_review = _save_review_form(form)
        if saved_review is not None:
            messages.success(request, "Your review was updated successfully.")
            return redirect(
                "reviews:book_detail",
                book_id=review.book_id,
            )

    return render(
        request,
        "reviews/review_form.html",
        {
            "book": review.book,
            "form": form,
            "heading": "Edit your review",
            "submit_label": "Save changes",
        },
    )


@require_GET
def book_list_redirect(request):
    del request
    return redirect("reviews:book_list")
