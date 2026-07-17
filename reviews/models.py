from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    cover_image = models.ImageField(upload_to="book_covers/", blank=True)
    description = models.TextField(blank=True)

    @property
    def average_rating(self):
        return self.reviews.aggregate(average=models.Avg("rating"))["average"]

    def __str__(self):
        return self.title


class Review(models.Model):
    text = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="unique_review_per_user_book",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="rating_between_1_and_5",
            ),
        ]

    def clean(self):
        super().clean()
        if not self.user_id or not self.book_id:
            return

        duplicate_reviews = Review.objects.filter(
            user_id=self.user_id,
            book_id=self.book_id,
        )
        if self.pk:
            duplicate_reviews = duplicate_reviews.exclude(pk=self.pk)
        if duplicate_reviews.exists():
            raise ValidationError(
                {"__all__": "This user has already reviewed this book."}
            )

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
