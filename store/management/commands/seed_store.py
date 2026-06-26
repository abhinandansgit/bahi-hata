from django.core.management.base import BaseCommand
from store.models import Category, Mood, Book

class Command(BaseCommand):
    help = 'Seed the store with sample categories, moods, and books'

    def handle(self, *args, **options):
        self.stdout.write('Seeding store data...')

        # --- Categories ---
        categories_data = [
            {'name': 'Fiction', 'description': 'Novels, short stories, and imaginative tales.'},
            {'name': 'Non-Fiction', 'description': 'Biographies, essays, and real-world explorations.'},
            {'name': 'Odia Literature', 'description': 'Classic and modern Odia literary works.'},
            {'name': 'Children', 'description': 'Books for young readers and curious minds.'},
            {'name': 'Academic', 'description': 'Textbooks, guides, and competitive exam prep.'},
            {'name': 'Poetry', 'description': 'Verses, anthologies, and poetic collections.'},
            {'name': 'Spiritual', 'description': 'Philosophy, meditation, and inner peace.'},
        ]
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
            categories[cat.name] = cat
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  Category: {cat.name} [{status}]')

        # --- Moods ---
        moods_data = {
            'Rainy Evening Reads': 'https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&q=80&w=600',
            'For Dreamers': 'https://images.unsplash.com/photo-1490730141103-6cac27aaab94?auto=format&fit=crop&q=80&w=600',
            'Odia Classics': 'https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&q=80&w=600',
            'Spiritual Calm': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&q=80&w=600',
            'Quick Weekend Read': 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&q=80&w=600',
            'UPSC Prep': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&q=80&w=600',
        }
        moods = {}
        for mood_name, image_url in moods_data.items():
            mood, created = Mood.objects.get_or_create(name=mood_name)
            mood.image_url = image_url
            mood.save()
            moods[mood.name] = mood
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  Mood: {mood.name} [{status}]')

        # --- Books ---
        books_data = [
            {
                'title': 'Chha Mana Atha Guntha',
                'author': 'Fakir Mohan Senapati',
                'description': 'A pioneering Odia novel that explores the exploitation of peasants by landlords in colonial Odisha. Considered the first modern Indian novel dealing with the plight of the landless poor.',
                'price': 299,
                'discount_percentage': 15,
                'category': 'Odia Literature',
                'language': 'OD',
                'is_trending_in_odisha': True,
                'is_odisha_heritage': True,
                'stock': 45,
                'moods': ['Odia Classics', 'Rainy Evening Reads'],
                'cover_image_url': 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'Matira Manisha',
                'author': 'Kalindi Charan Panigrahi',
                'description': 'An epic Odia novel depicting the struggles of common people in rural Odisha. Winner of the Jnanpith Award.',
                'price': 350,
                'discount_percentage': 10,
                'category': 'Odia Literature',
                'language': 'OD',
                'is_trending_in_odisha': True,
                'is_odisha_heritage': True,
                'stock': 30,
                'moods': ['Odia Classics', 'Spiritual Calm'],
                'cover_image_url': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'Paraja',
                'author': 'Gopinath Mohanty',
                'description': 'A powerful novel about the lives of tribal people in the hills of Odisha. Translated into many languages and widely acclaimed.',
                'price': 425,
                'discount_percentage': 20,
                'category': 'Odia Literature',
                'language': 'OD',
                'is_trending_in_odisha': True,
                'is_odisha_heritage': True,
                'stock': 25,
                'moods': ['Odia Classics', 'Rainy Evening Reads'],
                'cover_image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'The Guide',
                'author': 'R.K. Narayan',
                'description': 'A humorous and insightful novel about Raju, a tour guide in the fictional town of Malgudi, who transforms into a spiritual guru.',
                'price': 199,
                'discount_percentage': 5,
                'category': 'Fiction',
                'language': 'EN',
                'is_trending_in_odisha': False,
                'is_odisha_heritage': False,
                'stock': 80,
                'moods': ['Quick Weekend Read', 'For Dreamers'],
                'cover_image_url': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'Wings of Fire',
                'author': 'A.P.J. Abdul Kalam',
                'description': 'The autobiography of India\'s beloved Missile Man and former President, tracing his journey from a small town in Tamil Nadu to the pinnacle of Indian science.',
                'price': 399,
                'discount_percentage': 25,
                'category': 'Non-Fiction',
                'language': 'EN',
                'is_trending_in_odisha': True,
                'is_odisha_heritage': False,
                'stock': 100,
                'moods': ['UPSC Prep', 'For Dreamers'],
                'cover_image_url': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'Gitanjali',
                'author': 'Rabindranath Tagore',
                'description': 'Nobel Prize-winning collection of poems, offering spiritual insight and lyrical beauty. A masterpiece of Indian literature.',
                'price': 250,
                'discount_percentage': 0,
                'category': 'Poetry',
                'language': 'EN',
                'is_trending_in_odisha': False,
                'is_odisha_heritage': False,
                'stock': 60,
                'moods': ['Spiritual Calm', 'Rainy Evening Reads'],
                'cover_image_url': 'https://images.unsplash.com/photo-1474932430478-367dbb6832c1?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'Indian Polity by Laxmikant',
                'author': 'M. Laxmikant',
                'description': 'The most comprehensive and authoritative book on Indian polity for UPSC and competitive exam preparation.',
                'price': 699,
                'discount_percentage': 10,
                'category': 'Academic',
                'language': 'EN',
                'is_trending_in_odisha': True,
                'is_odisha_heritage': False,
                'stock': 150,
                'moods': ['UPSC Prep'],
                'cover_image_url': 'https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'Panchatantra',
                'author': 'Vishnu Sharma',
                'description': 'Timeless collection of animal fables teaching wisdom, statecraft, and moral lessons. Loved by children and adults alike.',
                'price': 175,
                'discount_percentage': 0,
                'category': 'Children',
                'language': 'EN',
                'is_trending_in_odisha': False,
                'is_odisha_heritage': False,
                'stock': 90,
                'moods': ['Quick Weekend Read'],
                'cover_image_url': 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'Bhagavad Gita As It Is',
                'author': 'A.C. Bhaktivedanta Swami Prabhupada',
                'description': 'The most widely read edition of the Bhagavad Gita with original Sanskrit text, transliteration, word-for-word meanings, and elaborate purports.',
                'price': 550,
                'discount_percentage': 15,
                'category': 'Spiritual',
                'language': 'EN',
                'is_trending_in_odisha': False,
                'is_odisha_heritage': False,
                'stock': 70,
                'moods': ['Spiritual Calm'],
                'cover_image_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'Amrutara Santana',
                'author': 'Manoj Das',
                'description': 'A mesmerizing collection of short stories by the legendary Odia-English bilingual author Manoj Das, blending mysticism with realism.',
                'price': 320,
                'discount_percentage': 10,
                'category': 'Odia Literature',
                'language': 'OD',
                'is_trending_in_odisha': True,
                'is_odisha_heritage': True,
                'stock': 35,
                'moods': ['Odia Classics', 'For Dreamers'],
                'cover_image_url': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'description': 'A magical story about Santiago, an Andalusian shepherd boy who yearns to travel in search of a worldly treasure.',
                'price': 299,
                'discount_percentage': 20,
                'category': 'Fiction',
                'language': 'EN',
                'is_trending_in_odisha': True,
                'is_odisha_heritage': False,
                'stock': 120,
                'moods': ['For Dreamers', 'Quick Weekend Read'],
                'cover_image_url': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=400',
            },
            {
                'title': 'Yajnaseni',
                'author': 'Pratibha Ray',
                'description': 'A Jnanpith Award-winning Odia novel retelling the Mahabharata from Draupadi\'s perspective. A landmark in feminist Indian literature.',
                'price': 399,
                'discount_percentage': 10,
                'category': 'Odia Literature',
                'language': 'OD',
                'is_trending_in_odisha': True,
                'is_odisha_heritage': True,
                'stock': 40,
                'moods': ['Odia Classics', 'Spiritual Calm'],
                'cover_image_url': 'https://images.unsplash.com/photo-1463320359563-34ea9c6a7386?auto=format&fit=crop&q=80&w=400',
            },
        ]

        for book_data in books_data:
            mood_names = book_data.pop('moods')
            cat_name = book_data.pop('category')
            book_data['category'] = categories[cat_name]
            cover_image_url = book_data.pop('cover_image_url', '')

            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                defaults=book_data
            )
            book.cover_image_url = cover_image_url
            book.save()

            if created:
                for mood_name in mood_names:
                    book.moods.add(moods[mood_name])
                self.stdout.write(f'  Book: {book.title} [Created]')
            else:
                self.stdout.write(f'  Book: {book.title} [Exists]')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {Book.objects.count()} books, {Category.objects.count()} categories, {Mood.objects.count()} moods in the store.'
        ))
