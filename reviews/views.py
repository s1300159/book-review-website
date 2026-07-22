from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.views.decorators.http import require_GET

from reviews.models import Book


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
    del request
    book_links = _book_links(Book.objects.all())
    if book_links:
        content = format_html("<ul>{}</ul>", book_links)
    else:
        content = format_html("<p>{}</p>", "No books are available.")

    body = format_html("<h1>{}</h1>{}", "Books", content)
    return _page("Books", body)


@require_GET
def book_detail(request, book_id):
    del request
    book = get_object_or_404(Book, pk=book_id)
    reviews = book.reviews.select_related("user").order_by("-created_at", "-pk")
    review_items = format_html_join(
        "",
        "<li><strong>{}</strong>: {} / 5 &mdash; {}</li>",
        ((review.user.username, review.rating, review.text) for review in reviews),
    )
    if review_items:
        review_content = format_html("<ul>{}</ul>", review_items)
    else:
        review_content = format_html("<p>{}</p>", "No reviews yet.")

    description = book.description or "No description available."
    average_rating = book.average_rating
    average_display = (
        "No ratings yet." if average_rating is None else str(average_rating)
    )
    body = format_html(
        "<h1>{}</h1><p>{}</p><p>Average rating: {}</p>"
        '<h2>{}</h2>{}<p><a href="{}">{}</a></p>',
        book.title,
        description,
        average_display,
        "Reviews",
        review_content,
        reverse("reviews:review_create", args=[book.pk]),
        "Write a review",
    )
    return _page(book.title, body)


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
