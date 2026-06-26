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

// ===== MINI CART =====
function toggleCart() {
  const cart = document.getElementById('miniCart');
  const overlay = document.getElementById('cartOverlay');
  if(cart) cart.classList.toggle('open');
  if(overlay) overlay.classList.toggle('open');
}

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
    
    if (data.added) {
      showToast(`🔖 Saved "${data.book_title}" to your shelf!`);
      btn.innerHTML = '❤️';
    } else {
      showToast(`🗑️ Removed from your shelf.`);
      btn.innerHTML = '🔖';
    }
  } catch (err) {
    window.location.href = btn.href; // Fallback to normal link if AJAX fails
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

