import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bahihata.settings')
django.setup()

from store.models import Category, Mood, Book, BookCombo, Offer, MagazineEdition, MagazineSubmission
from core.models import ReaderStory
from accounts.models import User

def run():
    print("[*] Starting Bahi Hata Full Platform Seeding...")

    # 1. Superuser
    if not User.objects.filter(username="abhiadmin").exists():
        admin_user = User.objects.create_superuser(
            username="abhiadmin",
            email="theabhilasha14@gmail.com",
            password="admin@123",
            first_name="Abhinandan",
            last_name="Mishra"
        )
        print("[+] Created Superuser: abhiadmin / admin@123")

    # 2. Categories
    categories_data = [
        "Odia Literature", "Fiction", "Non-Fiction", "Children", 
        "Academic", "Poetry", "Spiritual", "Historical Fiction"
    ]
    cats = {}
    for cname in categories_data:
        cat, _ = Category.objects.get_or_create(name=cname)
        cats[cname] = cat
    print(f"[+] Seeded {len(cats)} Categories.")

    # 3. Moods
    moods_data = [
        ("Rainy Evening Reads", "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&q=80&w=600"),
        ("UPSC Prep", "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&q=80&w=600"),
        ("For Dreamers", "https://images.unsplash.com/photo-1490730141103-6cac27aaab94?auto=format&fit=crop&q=80&w=600"),
        ("Odia Classics", "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=600"),
        ("Spiritual Calm", "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&q=80&w=600"),
        ("Quick Weekend Read", "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=600"),
    ]
    mood_objs = {}
    for mname, murl in moods_data:
        m, _ = Mood.objects.get_or_create(name=mname)
        m.image_url = murl
        m.save()
        mood_objs[mname] = m
    print(f"[+] Seeded {len(mood_objs)} Moods.")

    # 4. Books with 3 images each (500x500 high-res)
    books_data = [
        {
            "title": "Paraja (ପରଜା)",
            "author": "Gopinath Mohanty",
            "category": cats["Odia Literature"],
            "price": 380.00,
            "discount_percentage": 15.0,
            "description": "The magnum opus of modern Odia literature, chronicling the tribal soul and resilience of Koraput.",
            "cover_image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=500",
            "image_2_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=500",
            "image_3_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&q=80&w=500",
            "is_trending_in_odisha": True,
            "is_odisha_heritage": True,
            "is_bestseller": True,
            "stock": 45,
            "moods": ["Odia Classics", "Rainy Evening Reads"]
        },
        {
            "title": "Chha Mana Atha Guntha (ଛ' ମାଣ ଆଠଗୁଣ୍ଠ)",
            "author": "Fakir Mohan Senapati",
            "category": cats["Odia Literature"],
            "price": 299.00,
            "discount_percentage": 10.0,
            "description": "Fakir Mohan Senapati's iconic satire on feudal exploitation and moral justice in rural Odisha.",
            "cover_image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=500",
            "image_2_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=500",
            "image_3_url": "https://images.unsplash.com/photo-1495640388908-05fa85288e61?auto=format&fit=crop&q=80&w=500",
            "is_trending_in_odisha": True,
            "is_odisha_heritage": True,
            "is_bestseller": True,
            "stock": 35,
            "moods": ["Odia Classics"]
        },
        {
            "title": "Yajnaseni: The Story of Draupadi",
            "author": "Pratibha Ray",
            "category": cats["Fiction"],
            "price": 420.00,
            "discount_percentage": 12.0,
            "description": "The Jnanpith-winning lyrical narrative reimagining the Mahabharata through the consciousness of Draupadi.",
            "cover_image_url": "https://images.unsplash.com/photo-1495640388908-05fa85288e61?auto=format&fit=crop&q=80&w=500",
            "image_2_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=500",
            "image_3_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=500",
            "is_trending_in_odisha": True,
            "is_bestseller": True,
            "stock": 50,
            "moods": ["For Dreamers", "Rainy Evening Reads"]
        },
        {
            "title": "Odisha History & Civil Services Guide",
            "author": "Bahi Hata Editorial Board",
            "category": cats["Academic"],
            "price": 550.00,
            "discount_percentage": 20.0,
            "description": "Comprehensive guide covering Odisha culture, geography, and modern history for OPSC/UPSC aspirants.",
            "cover_image_url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&q=80&w=500",
            "image_2_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&q=80&w=500",
            "image_3_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=500",
            "is_trending_in_odisha": False,
            "is_bestseller": True,
            "stock": 60,
            "moods": ["UPSC Prep"]
        },
        {
            "title": "Bhagabata Gita (Odia Anubada)",
            "author": "Jagannatha Dasa",
            "category": cats["Spiritual"],
            "price": 250.00,
            "discount_percentage": 10.0,
            "description": "Timeless Odia Nabakshari verse translation of the holy Bhagavad Gita for daily spiritual contemplation.",
            "cover_image_url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&q=80&w=500",
            "image_2_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=500",
            "image_3_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=500",
            "is_trending_in_odisha": True,
            "is_odisha_heritage": True,
            "stock": 40,
            "moods": ["Spiritual Calm"]
        }
    ]

    created_books = []
    for bdata in books_data:
        m_list = bdata.pop("moods", [])
        book, _ = Book.objects.get_or_create(title=bdata["title"], defaults=bdata)
        for k, v in bdata.items():
            setattr(book, k, v)
        book.save()
        for mn in m_list:
            if mn in mood_objs:
                book.moods.add(mood_objs[mn])
        created_books.append(book)
    print(f"[+] Seeded {len(created_books)} Books with 3 high-res images each.")

    # 5. Book Combo
    combo, _ = BookCombo.objects.get_or_create(
        name="Odia Literary Heritage Pack",
        defaults={
            "description": "Curated twin bundle featuring Fakir Mohan Senapati's Chha Mana Atha Guntha and Gopinath Mohanty's Paraja.",
            "combo_price": 549.00,
            "cover_image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=600",
            "is_active": True
        }
    )
    if len(created_books) >= 2:
        combo.books.set([created_books[0], created_books[1]])
    print("[+] Seeded Book Combo.")

    # 6. Abhilasha Magazine Editions
    mag_ed, _ = MagazineEdition.objects.get_or_create(
        title="Abhilasha Annual Literary Edition 2026",
        defaults={
            "edition_year": "2026",
            "issue_number": "Annual Edition",
            "language": "BI",
            "description": "Bahi Hata's annual print magazine uniting premier poets, essayists, and emerging writers across Odisha and India.",
            "price": 249.00,
            "discount_percentage": 15.0,
            "stock": 100,
            "is_current_edition": True,
            "is_active": True,
            "total_pages": 140,
            "chief_editor": "Abhilasha Editorial Board",
            "cover_image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&q=80&w=800"
        }
    )
    print("[+] Seeded Abhilasha Magazine Edition.")

    # 7. Reader Stories
    stories_seed = [
        {
            "name": "Abhinandan Mishra",
            "location": "Bhubaneswar, Odisha",
            "rating": 5,
            "review_text": "Bahi Hata has made accessing Odia literature effortless! The page-curl reading feel and fast delivery across Odisha is unmatched.",
            "is_approved": True
        },
        {
            "name": "Priyabrata Mohapatra",
            "location": "Cuttack, Odisha",
            "rating": 5,
            "review_text": "Finding original Odia books like Paraja delivered right to my doorstep with authentic bookmarks was a joy.",
            "is_approved": True
        },
        {
            "name": "Subhashree Dash",
            "location": "Puri, Odisha",
            "rating": 5,
            "review_text": "The mood-based discovery and Abhilasha magazine section reflect genuine passion for Odia culture.",
            "is_approved": True
        },
        {
            "name": "Alok Kumar Sahoo",
            "location": "Rourkela, Odisha",
            "rating": 5,
            "review_text": "Superb packing and fast dispatch. The book combos provide incredible value for students and literature enthusiasts.",
            "is_approved": True
        }
    ]
    for sdata in stories_seed:
        ReaderStory.objects.get_or_create(
            name=sdata["name"],
            location=sdata["location"],
            defaults=sdata
        )
    print("[+] Seeded Approved Reader Stories.")

    print("[*] All Bahi Hata platform features seeded successfully!")

if __name__ == '__main__':
    run()

