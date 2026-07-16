from django.contrib import admin

from reviews.models import Book, Review


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "created_at")
