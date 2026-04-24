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
        moods_data = [
            'Rainy Evening Reads', 'For Dreamers', 'Odia Classics',
            'Spiritual Calm', 'Quick Weekend Read', 'UPSC Prep',
        ]
        moods = {}
        for mood_name in moods_data:
            mood, created = Mood.objects.get_or_create(name=mood_name)
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
            },
        ]

        for book_data in books_data:
            mood_names = book_data.pop('moods')
            cat_name = book_data.pop('category')
            book_data['category'] = categories[cat_name]

            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                defaults=book_data
            )

            if created:
                for mood_name in mood_names:
                    book.moods.add(moods[mood_name])
                self.stdout.write(f'  Book: {book.title} [Created]')
            else:
                self.stdout.write(f'  Book: {book.title} [Exists]')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {Book.objects.count()} books, {Category.objects.count()} categories, {Mood.objects.count()} moods in the store.'
        ))
