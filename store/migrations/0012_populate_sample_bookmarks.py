from django.db import migrations


def create_initial_bookmarks(apps, schema_editor):
    Bookmark = apps.get_model('store', 'Bookmark')
    items = [
        {
            'title': 'Classic Odia Palm Leaf Calligraphy Bookmark',
            'description': 'Handcrafted palm-leaf inspired bookmark with Odia literary quotes & gold tassel.',
            'price': 35.00,
            'stock': 10,
            'is_featured': True,
            'is_active': True,
        },
        {
            'title': 'Handmade Tassel Brass Bookmark',
            'description': 'Premium metallic bookmark featuring intricate Odisha temple heritage motifs.',
            'price': 49.00,
            'stock': 8,
            'is_featured': True,
            'is_active': True,
        },
        {
            'title': 'Jagannath Culture Wooden Bookmark',
            'description': 'Laser-engraved polished wooden bookmark celebrating Odia heritage.',
            'price': 79.00,
            'stock': 5,
            'is_featured': True,
            'is_active': True,
        },
        {
            'title': 'Abhilasha Vintage Leatherette Bookmark',
            'description': 'Collector edition leatherette bookmark with embossed Odia script.',
            'price': 99.00,
            'stock': 1,
            'is_featured': True,
            'is_active': True,
        },
    ]
    for item in items:
        Bookmark.objects.get_or_create(title=item['title'], defaults=item)


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_bookmark_alter_magazinesubmission_options'),
    ]

    operations = [
        migrations.RunPython(create_initial_bookmarks, reverse_code=reverse_func),
    ]
