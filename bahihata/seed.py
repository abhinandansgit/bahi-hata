import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bahihata.settings')
django.setup()

from store.models import Category, Mood, Book
from accounts.models import User

def run():
    print("Seeding data...")
    cat1, _ = Category.objects.get_or_create(name="Historical Fiction")
    cat2, _ = Category.objects.get_or_create(name="Odia Literature")
    
    mood1, _ = Mood.objects.get_or_create(name="For Rainy Evenings")
    mood1.image_url = 'https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&q=80&w=600'
    mood1.save()
    
    mood2, _ = Mood.objects.get_or_create(name="For Dreamers")
    mood2.image_url = 'https://images.unsplash.com/photo-1490730141103-6cac27aaab94?auto=format&fit=crop&q=80&w=600'
    mood2.save()
    
    book1, created = Book.objects.get_or_create(
        title="Paraja",
        defaults={
            'author': "Gopinath Mohanty",
            'description': "A classic of Odia literature.",
            'price': 350.00,
            'discount_percentage': 10.0,
            'category': cat2,
            'is_trending_in_odisha': True,
            'is_odisha_heritage': True,
            'stock': 50
        }
    )
    book1.cover_image_url = 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=400'
    book1.save()
    book1.moods.add(mood1, mood2)
    
    book2, created = Book.objects.get_or_create(
        title="Six Acres and a Third",
        defaults={
            'author': "Fakir Mohan Senapati",
            'description': "A foundational work of modern Odia literature.",
            'price': 299.00,
            'category': cat2,
            'is_trending_in_odisha': True,
            'stock': 30
        }
    )
    book2.cover_image_url = 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=400'
    book2.save()
    book2.moods.add(mood1)

    print("Data seeded successfully!")

if __name__ == '__main__':
    run()
