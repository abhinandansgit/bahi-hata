from django.contrib import admin
from .models import Category, Mood, Book, BookReview, BookCombo, Offer


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
    list_display = ('title', 'author', 'category', 'price', 'discount_percentage', 'stock',
                    'is_trending_in_odisha', 'is_odisha_heritage', 'is_bestseller')
    list_filter = ('category', 'language', 'is_trending_in_odisha', 'is_odisha_heritage',
                   'is_bestseller', 'is_popular')
    search_fields = ('title', 'author')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('moods',)
    list_editable = ('stock', 'price', 'discount_percentage')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BookCombo)
class BookComboAdmin(admin.ModelAdmin):
    list_display = ('name', 'combo_price', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    filter_horizontal = ('books',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'offer_type', 'discount_value', 'is_active',
                    'valid_from', 'valid_until', 'times_used')
    list_filter = ('is_active', 'offer_type', 'applies_to_combos_only')
    search_fields = ('name', 'code')
    readonly_fields = ('times_used', 'created_at')
    list_editable = ('is_active',)


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
