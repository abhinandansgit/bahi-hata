from django.contrib import admin
from .models import Category, Mood, Book, BookReview

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price', 'stock', 'is_trending_in_odisha', 'is_odisha_heritage')
    list_filter = ('category', 'language', 'is_trending_in_odisha', 'is_odisha_heritage')
    search_fields = ('title', 'author')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('moods',)

@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
