import re
import os

log_path = r'C:\Users\hp\.gemini\antigravity\brain\93322571-6d11-46e3-8ac4-95618fa707be\.system_generated\logs\overview.txt'
with open(log_path, 'r', encoding='utf-8') as f:
    text = f.read()

# find body
html_match = re.search(r'<!-- ===== HERO ===== -->(.*?)<!-- ===== FOOTER ===== -->', text, re.DOTALL)
if html_match:
    html_content = html_match.group(1)
    
    # Wrap in base extension
    final_html = "{% extends 'base.html' %}\n{% load static %}\n{% block content %}\n" + html_content + "\n{% endblock %}\n"
    
    # Replace the shelf books with a loop.
    shelf_pattern = re.compile(r'<div class="shelf-scroll" id="mainShelf">(.*?)</div>\s*<button class="shelf-nav shelf-nav-next"', re.DOTALL)
    
    django_loop = """
        {% for book in trending_books|slice:":6" %}
        <div class="book-card">
          <div class="book-img-wrap" style="height:280px;background:linear-gradient(135deg,#9B3A1A,#C4531E);">
            <div class="book-ribbon">{{ book.category.name }}</div>
            {% if book.is_trending_in_odisha %}
            <div class="book-trending">🔥 Trending</div>
            {% endif %}
            <div class="book-wishlist" onclick="addWishlist(event)">🔖</div>
            <div class="book-quote-preview">
              <div class="book-quote-text">"{{ book.description|truncatechars:60 }}"</div>
            </div>
            <div style="display:flex;align-items:center;justify-content:center;height:100%;font-size:60px;opacity:0.8;">
              {% if book.cover_image %}
                <img src="{{ book.cover_image.url }}" style="width:100%; height:100%; object-fit:cover;" />
              {% else %}
                📕
              {% endif %}
            </div>
          </div>
          <div class="book-info">
            <div class="book-genre">{{ book.category.name }}</div>
            <div class="book-title">{{ book.title }}</div>
            <div class="book-author">{{ book.author }}</div>
            <div class="book-price-row">
              <div class="price-wrap">
                <span class="price-now">₹{{ book.price }}</span>
              </div>
              <a href="{% url 'orders:add_to_cart' book.id %}" class="btn-cart">Add +</a>
            </div>
          </div>
        </div>
        {% empty %}
        <div style="padding:40px;">No trending books available right now.</div>
        {% endfor %}
    """
    
    final_html = shelf_pattern.sub(f'<div class="shelf-scroll" id="mainShelf">{django_loop}</div>\n      <button class="shelf-nav shelf-nav-next"', final_html)
    
    with open(r'c:\Users\hp\.gemini\antigravity\scratch\core\templates\core\home.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
