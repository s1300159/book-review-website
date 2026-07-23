from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.views.decorators.http import require_GET

from reviews.models import Book

RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY = "recently_viewed_book_ids"


def _page(title, body):
    document = format_html(
        "<!doctype html><html><head><title>{}</title></head><body>{}</body></html>",
        title,
        body,
    )
    return HttpResponse(document)


def _book_links(books):
    return format_html_join(
        "",
        '<li><a href="{}">{}</a></li>',
        (
            (reverse("reviews:book_detail", args=[book.pk]), book.title)
            for book in books
        ),
    )


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
    return render(
        request,
        "reviews/book_detail.html",
        {
            "book": book,
            "reviews": reviews,
            "average_rating": book.average_rating,
        },
    )


@require_GET
def book_search(request):
    query = request.GET.get("q", "").strip()
    form = format_html(
        '<form method="get" action="{}"><label for="q">{}</label> '
        '<input id="q" name="q" value="{}"><button type="submit">{}</button>'
        "</form>",
        reverse("reviews:book_search"),
        "Book title",
        query,
        "Search",
    )

    if not query:
        results = format_html("<p>{}</p>", "Enter a book title to search.")
    else:
        book_links = _book_links(Book.objects.filter(title__icontains=query))
        if book_links:
            results = format_html(
                "<p>Search query: {}</p><ul>{}</ul>", query, book_links
            )
        else:
            results = format_html(
                "<p>Search query: {}</p><p>{}</p>",
                query,
                "No books matched.",
            )

    body = format_html("<h1>{}</h1>{}{}", "Search books", form, results)
    return _page("Search books", body)


@require_GET
def review_create(request, book_id):
    del request
    book = get_object_or_404(Book, pk=book_id)
    body = format_html(
        "<h1>Review {}</h1><p>{}</p>",
        book.title,
        "Review submission is not available yet.",
    )
    return _page("Write a review", body)


@require_GET
def book_list_redirect(request):
    del request
    return redirect("reviews:book_list")
