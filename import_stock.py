import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bahihata.settings')
django.setup()

from store.models import Category, Book
from django.utils.text import slugify

stock_data = [
    # Page 1
    {"title": "Badhu Nirupama", "author": "Bibhuti Pattnaik", "mrp": 150.00, "stock": 6, "category": "Odia Literature"},
    {"title": "Jagyaseni", "author": "Pratibha Ray", "mrp": 550.00, "stock": 1, "category": "Fiction"},
    {"title": "Silapadma", "author": "Pratibha Ray", "mrp": 350.00, "stock": 3, "category": "Fiction"},
    {"title": "Coffee Bagicha Re Rati", "author": "Bibhuti Pattnaik", "mrp": 250.00, "stock": 2, "category": "Fiction"},
    {"title": "Dhuli Mati Ra Santha", "author": "Gopinath Mohanty", "mrp": 420.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Mati Matala", "author": "Gopinath Mohanty", "mrp": 800.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Bullet Lover", "author": "Varnalipi", "mrp": 249.00, "stock": 2, "category": "Fiction"},
    {"title": "Nayika Ra Nama Srabani", "author": "Bibhuti Pattnaik", "mrp": 450.00, "stock": 1, "category": "Fiction"},
    {"title": "Bou Mo Apadha Bahi", "author": "Pratibha Ray", "mrp": 500.00, "stock": 2, "category": "Odia Literature"},
    {"title": "Bundae Pani", "author": "Gopinath Mohanty", "mrp": 180.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Dana Pani", "author": "Gopinath Mohanty", "mrp": 270.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Paraja", "author": "Gopinath Mohanty", "mrp": 350.00, "stock": 4, "category": "Odia Literature"},
    {"title": "Dhuli", "author": "Binapani Pradhan", "mrp": 300.00, "stock": 2, "category": "Fiction"},
    {"title": "Purna Cheda", "author": "Kalki Krushna", "mrp": 199.00, "stock": 1, "category": "Fiction"},
    {"title": "Amabasya Ra Chandra", "author": "Gobinda Das", "mrp": 90.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Mala Janha", "author": "Upendra Kishor Das", "mrp": 120.00, "stock": 6, "category": "Odia Literature"},
    {"title": "Marala Ra Mrutyu", "author": "Surendra Mohanty", "mrp": 120.00, "stock": 5, "category": "Odia Literature"},
    {"title": "Para Purusa", "author": "Binapani Pradhan", "mrp": 180.00, "stock": 2, "category": "Fiction"},
    {"title": "Abhilasha", "author": "Snigdha Tripathy", "mrp": 299.00, "stock": 2, "category": "Fiction"},
    {"title": "Maya Mrugaya", "author": "Bibhuti Pattnaik", "mrp": 250.00, "stock": 2, "category": "Fiction"},
    {"title": "Baidehi Bidroha", "author": "Bibhuti Pattnaik", "mrp": 170.00, "stock": 2, "category": "Historical Fiction"},
    {"title": "Premika", "author": "Bibhuti Pattnaik", "mrp": 175.00, "stock": 1, "category": "Fiction"},
    {"title": "Barsha Basanta Baisakha", "author": "Pratibha Ray", "mrp": 350.00, "stock": 3, "category": "Fiction"},
    {"title": "Sati Asati", "author": "Bibhuti Pattnaik", "mrp": 230.00, "stock": 2, "category": "Fiction"},
    {"title": "Prathama Prema", "author": "Bibhuti Pattnaik", "mrp": 250.00, "stock": 1, "category": "Fiction"},
    {"title": "Bhala Jhia Mane Bhulanti Nahi", "author": "Bibhuti Pattnaik", "mrp": 110.00, "stock": 1, "category": "Fiction"},
    {"title": "Andhari Gada Ra Iti Katha (Chapala Chhanda)", "author": "Bibhuti Pattnaik", "mrp": 350.00, "stock": 1, "category": "Historical Fiction"},
    {"title": "Rani Mahumachhi", "author": "Bibhuti Pattnaik", "mrp": 155.00, "stock": 1, "category": "Fiction"},
    {"title": "Trutiya Purusha", "author": "Bibhuti Pattnaik", "mrp": 240.00, "stock": 1, "category": "Fiction"},
    {"title": "Samaya Asamaya", "author": "Bibhuti Pattnaik", "mrp": 300.00, "stock": 1, "category": "Fiction"},
    {"title": "Mahisasura Raa Muhan", "author": "Bibhuti Pattnaik", "mrp": 200.00, "stock": 1, "category": "Fiction"},
    {"title": "Patni Parameswari", "author": "Bibhuti Pattnaik", "mrp": 175.00, "stock": 1, "category": "Fiction"},
    {"title": "Bapa", "author": "Ajay Mohapatra", "mrp": 249.00, "stock": 1, "category": "Fiction"},
    {"title": "Nirbachana Upakhyana", "author": "Ajay Mohapatra", "mrp": 129.00, "stock": 2, "category": "Fiction"},
    {"title": "Bhabantara", "author": "Ajay Mohapatra", "mrp": 149.00, "stock": 1, "category": "Fiction"},
    {"title": "Aranya", "author": "Pratibha Ray", "mrp": 300.00, "stock": 4, "category": "Fiction"},
    {"title": "Megha Meduraa", "author": "Pratibha Ray", "mrp": 250.00, "stock": 1, "category": "Fiction"},
    {"title": "Aparichita", "author": "Pratibha Ray", "mrp": 250.00, "stock": 1, "category": "Fiction"},
    {"title": "Upanayika", "author": "Pratibha Ray", "mrp": 250.00, "stock": 3, "category": "Fiction"},
    {"title": "Nilatrushna", "author": "Pratibha Ray", "mrp": 450.00, "stock": 1, "category": "Fiction"},
    {"title": "Asabari", "author": "Pratibha Ray", "mrp": 450.00, "stock": 1, "category": "Fiction"},
    {"title": "Parichaya", "author": "Pratibha Ray", "mrp": 350.00, "stock": 3, "category": "Fiction"},
    {"title": "Gangasiuli", "author": "Pratibha Ray", "mrp": 225.00, "stock": 2, "category": "Fiction"},
    {"title": "Baya Chadedhei Ra Basa", "author": "Binapani Pradhan", "mrp": 200.00, "stock": 1, "category": "Fiction"},
    {"title": "Dhumrabha Diganta", "author": "Manoj Das", "mrp": 90.00, "stock": 1, "category": "Odia Literature"},

    # Page 2
    {"title": "Krushna", "author": "Surendra Nath Satpathy", "mrp": 360.00, "stock": 2, "category": "Spiritual"},
    {"title": "Jajati", "author": "Pandita Nilamani Mishra", "mrp": 400.00, "stock": 1, "category": "Historical Fiction"},
    {"title": "Dadi Budha", "author": "Gopinath Mohanty", "mrp": 104.00, "stock": 2, "category": "Odia Literature"},
    {"title": "Nila Padma", "author": "Ajay Mohapatra", "mrp": 249.00, "stock": 2, "category": "Fiction"},
    {"title": "Sesha Basanta Ra Chithi (Ajay Mohapatra)", "author": "Ajay Mohapatra", "mrp": 149.00, "stock": 1, "category": "Fiction"},
    {"title": "Matira Manisha", "author": "Kalandi Charan Panigrahi", "mrp": 100.00, "stock": 5, "category": "Odia Literature"},
    {"title": "Nilasaila", "author": "Surendra Mohanty", "mrp": 280.00, "stock": 1, "category": "Historical Fiction"},
    {"title": "Niladri Bijaya", "author": "Surendra Mohanty", "mrp": 250.00, "stock": 1, "category": "Historical Fiction"},
    {"title": "Chitralekha", "author": "Upendra Bhanja", "mrp": 220.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Harinahin Karubaki", "author": "Lakhmidhar Sahu", "mrp": 350.00, "stock": 1, "category": "Historical Fiction"},
    {"title": "Kala Pahada", "author": "Dr. Bhagabata Behera", "mrp": 400.00, "stock": 1, "category": "Historical Fiction"},
    {"title": "Pruthibi Bahare Manisha", "author": "Prof. Gokulananda Mahapatra", "mrp": 200.00, "stock": 1, "category": "Academic"},
    {"title": "Chandra Ra Mrutyu", "author": "Prof. Gokulananda Mahapatra", "mrp": 250.00, "stock": 3, "category": "Academic"},
    {"title": "Sesha Basanta Ra Chithi", "author": "Manoj Das", "mrp": 75.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Sati Saraswati", "author": "Akhaya Mohanty", "mrp": 220.00, "stock": 1, "category": "Fiction"},
    {"title": "Chhelichareibara Dina", "author": "Gourahari Das", "mrp": 250.00, "stock": 1, "category": "Fiction"},
    {"title": "Tusha", "author": "Debabrata Das", "mrp": 349.00, "stock": 1, "category": "Fiction"},
    {"title": "Padma Mali", "author": "Umesh Ch Sarkar", "mrp": 130.00, "stock": 2, "category": "Odia Literature"},
    {"title": "Shree Radha", "author": "Ramakanta Ratha", "mrp": 200.00, "stock": 1, "category": "Poetry"},
    {"title": "Prayaschita", "author": "Fakirmohan Senapati", "mrp": 150.00, "stock": 2, "category": "Odia Literature"},
    {"title": "Mamu", "author": "Fakirmohan Senapati", "mrp": 200.00, "stock": 2, "category": "Odia Literature"},
    {"title": "Chha Mana Aatha Ghunta", "author": "Fakirmohan Senapati", "mrp": 150.00, "stock": 2, "category": "Odia Literature"},
    {"title": "Lachham", "author": "Fakirmohan Senapati", "mrp": 125.00, "stock": 2, "category": "Odia Literature"},
    {"title": "Chilika", "author": "Radhanath Ray", "mrp": 100.00, "stock": 3, "category": "Poetry"},
    {"title": "Bali Raja", "author": "Kanhu Charan", "mrp": 299.00, "stock": 2, "category": "Odia Literature"},
    {"title": "Paree", "author": "Kanhu Charan", "mrp": 199.00, "stock": 2, "category": "Odia Literature"},
    {"title": "Tapasi", "author": "Kanhu Charan", "mrp": 299.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Mayabarta", "author": "Kanhu Charan", "mrp": 299.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Bajra Bahu", "author": "Kanhu Charan", "mrp": 399.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Kaa", "author": "Kanhu Charan", "mrp": 299.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Sasti", "author": "Kanhu Charan", "mrp": 299.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Tathastu", "author": "Kanhu Charan", "mrp": 299.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Pratikhya", "author": "Kanhu Charan", "mrp": 149.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Chhutile Ghata", "author": "Kanhu Charan", "mrp": 299.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Parakiya", "author": "Kanhu Charan", "mrp": 199.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Abhinetri", "author": "Kanhu Charan", "mrp": 149.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Bhuli Huena", "author": "Kanhu Charan", "mrp": 149.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Olata Palata", "author": "Kanhu Charan", "mrp": 199.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Epari Separi", "author": "Kanhu Charan", "mrp": 149.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Angana", "author": "Kanhu Charan", "mrp": 149.00, "stock": 1, "category": "Odia Literature"},
    {"title": "Tandraloka Ra Prahari", "author": "Manoj Das", "mrp": 200.00, "stock": 3, "category": "Odia Literature"},
    {"title": "Kichhi Kahibara Thila", "author": "Ramakrushna Dakua", "mrp": 249.00, "stock": 13, "category": "Fiction"},
    {"title": "Kape Prema", "author": "Dr. Sumanta Kumar Sahu", "mrp": 149.00, "stock": 3, "category": "Fiction"},
    {"title": "Jui Ra Sakala", "author": "Dr. Sumanta Kumar Sahu", "mrp": 149.00, "stock": 3, "category": "Fiction"},
    {"title": "Puspagiri Ra Sesha Pandulipi", "author": "AP Subhakanta Samal", "mrp": 249.00, "stock": 8, "category": "Historical Fiction"},

    # Page 3
    {"title": "Kling", "author": "Sivsundar", "mrp": 299.00, "stock": 10, "category": "Fiction"},
    {"title": "Kuhudi Kanya", "author": "Sivsundar", "mrp": 299.00, "stock": 9, "category": "Fiction"},
    {"title": "Sei Oldtown Jhia", "author": "Dr. Abhisek Tripathy", "mrp": 249.00, "stock": 7, "category": "Fiction"},
    {"title": "Hadabai (Kali)", "author": "Dr. Abhisek Tripathy", "mrp": 299.00, "stock": 6, "category": "Fiction"},
    {"title": "Orange Icecream", "author": "Alok Kumar Nayak", "mrp": 229.00, "stock": 8, "category": "Fiction"},
    {"title": "Tala Gada Ra Rani Maa Hingula", "author": "Sonali Gadanayak", "mrp": 125.00, "stock": 5, "category": "Fiction"},
    {"title": "Pabitra Bandhana", "author": "Sonali Gadanayak", "mrp": 149.00, "stock": 4, "category": "Fiction"},
    {"title": "Upasana", "author": "Sonali Gadanayak", "mrp": 120.00, "stock": 4, "category": "Fiction"},
    {"title": "Nirabata", "author": "Sonali Gadanayak", "mrp": 149.00, "stock": 4, "category": "Fiction"}
]

def run_import():
    print(f"[*] Processing {len(stock_data)} book inventory items...")
    created_count = 0
    updated_count = 0

    for item in stock_data:
        cat, _ = Category.objects.get_or_create(name=item["category"])
        
        # Look up by title (case insensitive)
        book = Book.objects.filter(title__iexact=item["title"]).first()
        if not book:
            # Create new book entry
            book = Book.objects.create(
                title=item["title"],
                author=item["author"],
                category=cat,
                price=item["mrp"],
                stock=item["stock"],
                language="OD",
                description=f"Authentic Odia book '{item['title']}' by {item['author']}."
            )
            created_count += 1
        else:
            # Update existing book entry with sheet data
            book.price = item["mrp"]
            book.stock = item["stock"]
            book.author = item["author"]
            book.category = cat
            book.language = "OD"
            book.save()
            updated_count += 1

    print(f"[OK] Inventory import complete: {created_count} books created, {updated_count} books updated.")
    print(f"[OK] Total Books in Store Database: {Book.objects.count()}")

if __name__ == '__main__':
    run_import()
