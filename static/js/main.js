// PocketSmart AI - Global Utility JavaScript

function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'fa-circle-info';
  if (type === 'success') icon = 'fa-circle-check';
  if (type === 'error') icon = 'fa-triangle-exclamation';
  if (type === 'warning') icon = 'fa-circle-exclamation';

  toast.innerHTML = `
    <i class="fa-solid ${icon}"></i>
    <div style="flex:1;">${message}</div>
    <button style="background:none;border:none;color:#94a3b8;cursor:pointer;padding:2px 6px;" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

function formatINR(amount) {
  if (amount == null) return '₹0';
  return '₹' + Number(amount).toLocaleString('en-IN');
}

// Toggle mobile navigation
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.querySelector('.nav-mobile-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', () => {
      navLinks.classList.toggle('show');
    });
  }

  // Parse URL query params for flash messages
  const urlParams = new URLSearchParams(window.location.search);
  const msg = urlParams.get('msg');
  const error = urlParams.get('error');

  if (msg) {
    showToast(msg, 'success');
  }
  if (error) {
    showToast(error, 'error');
  }
});

// Asynchronously save a recommendation item
async function saveRecommendationItem(button, planId, itemName, category, platform, price, itemDataJson) {
  try {
    let itemData = {};
    if (typeof itemDataJson === 'string') {
      try { itemData = JSON.parse(itemDataJson); } catch (e) { itemData = { name: itemName }; }
    } else {
      itemData = itemDataJson || {};
    }

    button.disabled = true;
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

    const response = await fetch(`/api/recommendations/${planId}/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        item_name: itemName,
        item_category: category,
        platform: platform,
        estimated_price: Number(price),
        recommendation_data: itemData
      })
    });

    const res = await response.json();
    if (response.ok && res.success) {
      button.className = 'btn btn-sm btn-accent';
      button.innerHTML = '<i class="fa-solid fa-bookmark"></i> Saved';
      button.disabled = true;
      showToast(res.message || 'Item saved to your collection!', 'success');
    } else {
      button.disabled = false;
      button.innerHTML = '<i class="fa-regular fa-bookmark"></i> Save';
      showToast(res.detail || res.message || 'Failed to save item', 'error');
    }
  } catch (err) {
    button.disabled = false;
    button.innerHTML = '<i class="fa-regular fa-bookmark"></i> Save';
    showToast('Network error while saving item.', 'error');
  }
}
