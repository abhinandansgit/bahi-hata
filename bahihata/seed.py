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
    mood2, _ = Mood.objects.get_or_create(name="For Dreamers")
    
    book1, _ = Book.objects.get_or_create(
        title="Paraja",
        author="Gopinath Mohanty",
        description="A classic of Odia literature.",
        price=350.00,
        discount_percentage=10.0,
        category=cat2,
        is_trending_in_odisha=True,
        is_odisha_heritage=True,
        stock=50
    )
    book1.moods.add(mood1, mood2)
    
    book2, _ = Book.objects.get_or_create(
        title="Six Acres and a Third",
        author="Fakir Mohan Senapati",
        description="A foundational work of modern Odia literature.",
        price=299.00,
        category=cat2,
        is_trending_in_odisha=True,
        stock=30
    )
    book2.moods.add(mood1)

    print("Data seeded successfully!")

if __name__ == '__main__':
    run()
