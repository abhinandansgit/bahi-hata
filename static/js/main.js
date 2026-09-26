// ===== CURSOR =====
const cursor = document.getElementById('cursor');
const follower = document.getElementById('cursorFollower');
let mx = 0, my = 0, fx = 0, fy = 0;

document.addEventListener('mousemove', e => {
  mx = e.clientX; my = e.clientY;
  if(cursor) {
    cursor.style.left = mx + 'px';
    cursor.style.top = my + 'px';
  }
});

function animateFollower() {
  fx += (mx - fx) * 0.12;
  fy += (my - fy) * 0.12;
  if(follower) {
    follower.style.left = fx + 'px';
    follower.style.top = fy + 'px';
  }
  requestAnimationFrame(animateFollower);
}
animateFollower();

document.querySelectorAll('a, button, .book-card, .mood-card, .plan-card, .faq-item, .search-tag, .nav-btn, .nav-cta, .quiz-option, .shelf-tab').forEach(el => {
  el.addEventListener('mouseenter', () => { 
    if(cursor) cursor.classList.add('hover'); 
    if(follower) follower.classList.add('hover'); 
  });
  el.addEventListener('mouseleave', () => { 
    if(cursor) cursor.classList.remove('hover'); 
    if(follower) follower.classList.remove('hover'); 
  });
});

// ===== READING PROGRESS =====
const progressBar = document.getElementById('readingProgress');
window.addEventListener('scroll', () => {
  const scrolled = window.scrollY;
  const total = document.documentElement.scrollHeight - window.innerHeight;
  if(progressBar) progressBar.style.width = (scrolled / total * 100) + '%';
  
  // Nav scroll style
  const nav = document.getElementById('mainNav');
  if(nav) nav.classList.toggle('scrolled', scrolled > 50);
});

// ===== SCROLL REVEAL =====
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.classList.add('visible');
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// Trigger hero reveals immediately
setTimeout(() => document.querySelectorAll('.hero .reveal').forEach(el => el.classList.add('visible')), 100);

// ===== READING SHELF (SIDE-OUT CART DRAWER) =====
function openCart() {
  const cart = document.getElementById('miniCart');
  const overlay = document.getElementById('cartOverlay');
  if (cart) cart.classList.add('open');
  if (overlay) overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeCart() {
  const cart = document.getElementById('miniCart');
  const overlay = document.getElementById('cartOverlay');
  if (cart) cart.classList.remove('open');
  if (overlay) overlay.classList.remove('open');
  document.body.style.overflow = '';
}

function toggleCart() {
  const cart = document.getElementById('miniCart');
  if (cart && cart.classList.contains('open')) {
    closeCart();
  } else {
    fetchCartData();
    openCart();
  }
}

// Close on Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeCart();
});

async function fetchCartData() {
  try {
    const response = await fetch('/orders/api/cart-data/', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const data = await response.json();
    if (data.authenticated && data.cart) {
      renderShelfDrawer(data.cart);
    }
  } catch (err) {
    console.warn('Could not fetch shelf data:', err);
  }
}

function updateCartBadges(count) {
  document.querySelectorAll('.cart-count, #cartCount, .mob-cart-badge, #shelfCountBadge').forEach(el => {
    el.textContent = count;
  });
}

function renderShelfDrawer(cart) {
  const container = document.getElementById('shelfItemsContainer');
  const footer = document.getElementById('shelfFooter');
  const subtotalEl = document.getElementById('shelfSubtotal');
  const countBadge = document.getElementById('shelfCountBadge');

  if (!container) return;

  const totalCount = cart.total_items_count || 0;
  if (countBadge) countBadge.textContent = totalCount;
  updateCartBadges(totalCount);

  if (totalCount === 0) {
    container.innerHTML = `
      <div class="mini-cart-empty">
          <div class="mini-cart-empty-icon">📖</div>
          <h4 class="mini-cart-empty-title">Your shelf is empty</h4>
          <p class="mini-cart-empty-desc">Explore hand-picked Odia classics, book combos, and Abhilasha magazine editions.</p>
          <a href="/store/books/" class="btn-sm btn-gold" onclick="closeCart()">Explore Books →</a>
      </div>
    `;
    if (footer) footer.style.display = 'none';
    return;
  }

  if (footer) {
    footer.style.display = 'block';
    if (subtotalEl) subtotalEl.textContent = `₹${(cart.subtotal || 0).toFixed(2)}`;
  }

  let html = '';

  // 1. Regular Books
  if (cart.items && cart.items.length > 0) {
    cart.items.forEach(item => {
      html += `
        <div class="shelf-item-card" data-item-id="${item.id}" data-item-type="book">
          ${item.cover_image_url ? 
            `<img src="${item.cover_image_url}" alt="${item.title}" class="shelf-item-img">` : 
            `<div class="shelf-item-img-placeholder">📖</div>`
          }
          <div class="shelf-item-info">
            <div>
              <div class="shelf-item-tag">${item.category || 'Odia Literature'}</div>
              <h4 class="shelf-item-title" title="${item.title}">${item.title}</h4>
              <div class="shelf-item-meta">by ${item.author || 'Author'}</div>
            </div>
            <div class="shelf-item-bottom">
              <div class="shelf-item-price">₹${item.price}</div>
              <div class="shelf-qty-stepper">
                <button type="button" class="shelf-qty-btn" onclick="updateShelfItem('${item.update_url}?action=decrease')">−</button>
                <span class="shelf-qty-val">${item.quantity}</span>
                <button type="button" class="shelf-qty-btn" onclick="updateShelfItem('${item.update_url}?action=increase')">+</button>
              </div>
              <button type="button" class="shelf-item-remove" title="Remove" onclick="updateShelfItem('${item.remove_url}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"></path></svg>
              </button>
            </div>
          </div>
        </div>
      `;
    });
  }

  // 2. Magazine Editions
  if (cart.magazine_items && cart.magazine_items.length > 0) {
    cart.magazine_items.forEach(mi => {
      html += `
        <div class="shelf-item-card mag-item" data-item-id="${mi.id}" data-item-type="magazine">
          ${mi.cover_image_url ? 
            `<img src="${mi.cover_image_url}" alt="${mi.title}" class="shelf-item-img">` : 
            `<div class="shelf-item-img-placeholder">📰</div>`
          }
          <div class="shelf-item-info">
            <div>
              <div class="shelf-item-tag" style="color: var(--forest);">📖 Magazine · ${mi.year}</div>
              <h4 class="shelf-item-title" title="${mi.title}">${mi.title}</h4>
              <div class="shelf-item-meta">${mi.issue} · ${mi.language}</div>
            </div>
            <div class="shelf-item-bottom">
              <div class="shelf-item-price">₹${mi.price}</div>
              <div class="shelf-qty-stepper">
                <button type="button" class="shelf-qty-btn" onclick="updateShelfItem('${mi.update_url}?action=decrease')">−</button>
                <span class="shelf-qty-val">${mi.quantity}</span>
                <button type="button" class="shelf-qty-btn" onclick="updateShelfItem('${mi.update_url}?action=increase')">+</button>
              </div>
              <button type="button" class="shelf-item-remove" title="Remove" onclick="updateShelfItem('${mi.remove_url}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"></path></svg>
              </button>
            </div>
          </div>
        </div>
      `;
    });
  }

  // 3. Combo Bundles
  if (cart.combo_items && cart.combo_items.length > 0) {
    cart.combo_items.forEach(ci => {
      html += `
        <div class="shelf-item-card combo-item" data-item-id="${ci.id}" data-item-type="combo">
          <div class="shelf-item-img-placeholder" style="background: linear-gradient(135deg, var(--gold-pale), var(--beige-warm)); font-size: 32px;">🎁</div>
          <div class="shelf-item-info">
            <div>
              <div class="shelf-item-tag" style="color: var(--gold);">🎁 Combo Bundle</div>
              <h4 class="shelf-item-title" title="${ci.name}">${ci.name}</h4>
              <div class="shelf-item-meta">${ci.books_included.join(' + ')}</div>
            </div>
            <div class="shelf-item-bottom">
              <div class="shelf-item-price">₹${ci.price}</div>
              <span style="font-size: 12px; color: var(--ink-softer); font-weight: 700;">Qty: 1</span>
              <button type="button" class="shelf-item-remove" title="Remove" onclick="updateShelfItem('${ci.remove_url}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"></path></svg>
              </button>
            </div>
          </div>
        </div>
      `;
    });
  }

  container.innerHTML = html;
}

async function updateShelfItem(url) {
  try {
    const res = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const data = await res.json();
    if (data.cart) {
      renderShelfDrawer(data.cart);
    }
    if (data.message) {
      showToast(data.message);
    }
  } catch (err) {
    console.error('Shelf update failed:', err);
  }
}

// Global AJAX interceptor for Add to Cart buttons
async function handleAddToCartClick(e, btn) {
  e.preventDefault();
  const href = btn.getAttribute('href');
  if (!href) return;

  const originalContent = btn.innerHTML;
  btn.style.pointerEvents = 'none';
  btn.style.opacity = '0.8';
  btn.innerHTML = `<span style="display:inline-block; width:12px; height:12px; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:spin 0.6s linear infinite; vertical-align:middle; margin-right:6px;"></span> Adding…`;

  try {
    const res = await fetch(href, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });

    if (res.status === 401) {
      const data = await res.json();
      if (data.login_url) {
        window.location.href = data.login_url;
        return;
      }
    }

    const data = await res.json();
    if (data.success && data.cart) {
      renderShelfDrawer(data.cart);
      showToast(data.message || 'Added to your reading shelf!');
      openCart();
    } else if (data.message) {
      showToast(data.message);
    }
  } catch (err) {
    // Fallback normal navigation if AJAX fails
    window.location.href = href;
  } finally {
    btn.style.pointerEvents = '';
    btn.style.opacity = '';
    btn.innerHTML = originalContent;
  }
}


// Bind click event listener on document
document.addEventListener('click', (e) => {
  const addBtn = e.target.closest('a[href*="/orders/cart/add/"], a[href*="/orders/cart/add-combo/"], a[href*="/orders/cart/add-magazine/"], .btn-cart, .btn-add-shelf, .btn-combo-add, .btn-mag-cart');
  if (addBtn && !addBtn.getAttribute('href')?.includes('checkout=1')) {
    handleAddToCartClick(e, addBtn);
  }
});

// ===== TOAST =====
let toastTimer;
function showToast(msg) {
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toastMsg');
  if(toastMsg) toastMsg.textContent = msg;
  if(toast) {
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
  }
}

// ===== SHELF SCROLL =====
function scrollShelf(dir) {
  const shelf = document.getElementById('mainShelf');
  if(shelf) shelf.scrollBy({ left: dir * 500, behavior: 'smooth' });
}

function scrollShelfAlt(shelfId, dir) {
  const shelf = document.getElementById(shelfId);
  if(shelf) shelf.scrollBy({ left: dir * 500, behavior: 'smooth' });
}

// ===== PARALLAX HERO =====
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  const scene = document.querySelector('.hero-scene');
  if (scene) scene.style.transform = `translateY(${scrollY * 0.3}px)`;
  const particles = document.getElementById('heroParticles');
  if (particles) particles.style.transform = `translateY(${scrollY * 0.15}px)`;
});

// ===== SCROLL TO SECTION =====
function scrollTo(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ===== HERO SEARCH TAGS =====
function setSearch(el) {
  const input = document.getElementById('heroSearch');
  if (input) {
    input.value = el.textContent.replace(/^[^\s]+\s/, ''); // strip emoji
    input.closest('form').submit();
  }
}

// ===== SHELF TABS =====
function setTab(btn) {
  document.querySelectorAll('.shelf-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');

  const filter = btn.textContent.trim().toLowerCase();
  const shelf = document.getElementById('mainShelf');
  if (!shelf) return;

  const cards = shelf.querySelectorAll('.book-card');
  cards.forEach(card => {
    let show = false;
    if (filter === 'all') {
      show = true;
    } else if (filter === 'odia') {
      show = (card.getAttribute('data-language') === 'odia');
    } else {
      const cat = card.getAttribute('data-category') || '';
      show = cat.includes(filter);
    }
    card.style.display = show ? '' : 'none';
  });
}

// ===== QUIZ OPTIONS =====
function selectOption(el) {
  document.querySelectorAll('.quiz-option').forEach(o => o.classList.remove('selected'));
  el.classList.add('selected');
}

// ===== WISHLIST =====
// ===== WISHLIST AJAX =====
async function toggleWishlist(e, bookId) {
  e.preventDefault();
  const btn = e.currentTarget;
  
  try {
    const response = await fetch(`/accounts/wishlist/toggle/${bookId}/`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const data = await response.json();
    
    const svg = btn.querySelector('svg');
    if (data.added) {
      showToast(`🔖 Saved "${data.book_title || 'Book'}" to your wishlist!`);
      btn.classList.add('active');
      if (svg) svg.setAttribute('fill', 'currentColor');
    } else {
      showToast(`🗑️ Removed from your wishlist.`);
      btn.classList.remove('active');
      if (svg) svg.setAttribute('fill', 'none');
    }
  } catch (err) {
    if (btn.href) window.location.href = btn.href;
  }
}

// ===== FAQ TOGGLE =====
function toggleFaq(item) {
  item.classList.toggle('open');
}

// ===== NEWSLETTER =====
function handleNewsletter(e) {
  e.preventDefault();
  showToast('📬 Welcome to the Bahi Patrika! Check your inbox.');
  e.target.reset();
}

// ===================================================
// BOOK CARDS AUTO-SWIPING & MULTI-IMAGE CAROUSEL
// ===================================================
const cardSliderTimers = new Map();

function updateCardSlide(sliderEl, targetIndex) {
  const slides = sliderEl.querySelectorAll('.book-slide');
  const dots = sliderEl.parentElement.querySelectorAll('.slider-dot');
  const total = slides.length;
  if (total <= 1) return;

  const validIndex = ((targetIndex % total) + total) % total;
  sliderEl.setAttribute('data-current-slide', validIndex);

  slides.forEach((slide, idx) => {
    slide.classList.toggle('active', idx === validIndex);
  });

  dots.forEach((dot, idx) => {
    dot.classList.toggle('active', idx === validIndex);
  });
}

function nextCardSlide(sliderEl) {
  const curr = parseInt(sliderEl.getAttribute('data-current-slide') || '0', 10);
  updateCardSlide(sliderEl, curr + 1);
}

function prevCardSlide(sliderEl) {
  const curr = parseInt(sliderEl.getAttribute('data-current-slide') || '0', 10);
  updateCardSlide(sliderEl, curr - 1);
}

function goToSlide(e, dotEl, targetIndex) {
  if (e) { e.preventDefault(); e.stopPropagation(); }
  const wrap = dotEl.closest('.book-img-wrap');
  if (!wrap) return;
  const slider = wrap.querySelector('.book-card-slider');
  if (slider) updateCardSlide(slider, targetIndex);
}

function manualSlide(e, btnEl, delta) {
  if (e) { e.preventDefault(); e.stopPropagation(); }
  const wrap = btnEl.closest('.book-img-wrap');
  if (!wrap) return;
  const slider = wrap.querySelector('.book-card-slider');
  if (slider) {
    if (delta > 0) nextCardSlide(slider);
    else prevCardSlide(slider);
  }
}

function pauseCardSlider(wrapEl) {
  const slider = wrapEl.querySelector('.book-card-slider');
  if (slider && cardSliderTimers.has(slider)) {
    clearInterval(cardSliderTimers.get(slider));
    cardSliderTimers.delete(slider);
  }
}

function resumeCardSlider(wrapEl) {
  const slider = wrapEl.querySelector('.book-card-slider');
  if (!slider) return;
  const total = parseInt(slider.getAttribute('data-total-slides') || '0', 10);
  if (total > 1 && !cardSliderTimers.has(slider)) {
    const timer = setInterval(() => nextCardSlide(slider), 3500);
    cardSliderTimers.set(slider, timer);
  }
}

function initBookCardSliders() {
  document.querySelectorAll('.book-card-slider').forEach((slider, idx) => {
    const total = parseInt(slider.getAttribute('data-total-slides') || '0', 10);
    if (total > 1) {
      // Stagger auto-play start so not all cards swipe in unison
      const staggerDelay = (idx % 4) * 800 + 2000;
      setTimeout(() => {
        if (!cardSliderTimers.has(slider)) {
          const timer = setInterval(() => nextCardSlide(slider), 3600);
          cardSliderTimers.set(slider, timer);
        }
      }, staggerDelay);

      // Add touch swipe detection
      let touchStartX = 0;
      let touchEndX = 0;
      slider.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });

      slider.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        if (touchStartX - touchEndX > 40) {
          nextCardSlide(slider);
        } else if (touchEndX - touchStartX > 40) {
          prevCardSlide(slider);
        }
      }, { passive: true });
    }
  });
}

// Initialize on DOMContentLoaded and dynamic loads
function initPage() {
  initBookCardSliders();
  fetchCartData();
}

document.addEventListener('DOMContentLoaded', initPage);
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  initPage();
}

