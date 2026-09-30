// PocketSmart AI - History Page JavaScript

let currentFilter = 'all';
let currentSort = 'newest';

document.addEventListener('DOMContentLoaded', () => {
  loadHistory();

  // Filter buttons
  const filterBtns = document.querySelectorAll('.history-filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.getAttribute('data-filter');
      loadHistory();
    });
  });

  // Sort dropdown
  const sortSelect = document.getElementById('history-sort');
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      currentSort = sortSelect.value;
      loadHistory();
    });
  }
});

async function loadHistory() {
  const container = document.getElementById('history-list-container');
  if (!container) return;

  container.innerHTML = `
    <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
      <i class="fa-solid fa-spinner fa-spin" style="font-size: 1.5rem; margin-bottom: 0.5rem;"></i>
      <div>Loading your previous plans...</div>
    </div>
  `;

  try {
    let url = `/api/history?sort_by=${currentSort}`;
    if (currentFilter !== 'all') {
      url += `&planner_type=${currentFilter}`;
    }

    const res = await fetch(url);
    const data = await res.json();

    if (res.ok && data.success) {
      renderHistoryList(data.data.plans);
    } else {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 2.5rem;">
          <div style="color: var(--danger); font-size: 1.5rem; margin-bottom: 0.5rem;"><i class="fa-solid fa-triangle-exclamation"></i></div>
          <p>Failed to load history.</p>
        </div>
      `;
    }
  } catch (err) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 2.5rem;">
        <p style="color: var(--danger);">Network error while loading history.</p>
      </div>
    `;
  }
}

function renderHistoryList(plans) {
  const container = document.getElementById('history-list-container');
  if (!container) return;

  if (!plans || plans.length === 0) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 3.5rem 1.5rem;">
        <div style="width: 56px; height: 56px; border-radius: 50%; background: var(--bg-subtle); color: var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin: 0 auto 1rem;">
          <i class="fa-solid fa-folder-open"></i>
        </div>
        <h3 style="font-size: 1.25rem; margin-bottom: 0.5rem;">No Plans Found</h3>
        <p style="color: var(--text-muted); max-width: 440px; margin: 0 auto 1.5rem; font-size: 0.9rem;">
          No plans match the selected category filter. Start planning a new project now.
        </p>
        <div style="display: flex; gap: 0.75rem; justify-content: center;">
          <a href="/home-planner" class="btn btn-primary btn-sm"><i class="fa-solid fa-couch"></i> Home</a>
          <a href="/party-planner" class="btn btn-primary btn-sm" style="background:#be185d; border-color:#be185d;"><i class="fa-solid fa-champagne-glasses"></i> Party</a>
          <a href="/jewelry-planner" class="btn btn-primary btn-sm" style="background:#b45309; border-color:#b45309;"><i class="fa-solid fa-gem"></i> Jewelry</a>
        </div>
      </div>
    `;
    return;
  }

  let html = '<div style="display: flex; flex-direction: column; gap: 1rem;">';
  plans.forEach(p => {
    let icon = 'fa-couch';
    let iconBg = '#e0e7ff';
    let iconCol = '#4338ca';
    let viewUrl = `/home-recommendations/${p.id}`;

    if (p.planner_type === 'party') {
      icon = 'fa-champagne-glasses';
      iconBg = '#fce7f3';
      iconCol = '#be185d';
      viewUrl = `/party-recommendations/${p.id}`;
    } else if (p.planner_type === 'jewelry') {
      icon = 'fa-gem';
      iconBg = '#fef3c7';
      iconCol = '#b45309';
      viewUrl = `/jewelry-recommendations/${p.id}`;
    }

    const dateStr = new Date(p.created_at).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });

    html += `
      <div class="card" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding: 1.25rem 1.5rem;">
        <div style="display: flex; align-items: center; gap: 1rem; flex: 1; min-width: 280px;">
          <div style="width: 48px; height: 48px; border-radius: var(--radius-sm); background: ${iconBg}; color: ${iconCol}; display: flex; align-items: center; justify-content: center; font-size: 1.35rem; flex-shrink: 0;">
            <i class="fa-solid ${icon}"></i>
          </div>
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.2rem;">
              <span class="badge badge-${p.planner_type}">${p.planner_type}</span>
              <span style="font-size: 0.8rem; color: var(--text-muted);">${dateStr}</span>
              ${p.is_fallback ? '<span class="badge badge-fallback" title="Fallback data used">Fallback</span>' : ''}
            </div>
            <h3 style="font-size: 1.1rem; margin-bottom: 0.2rem;">${p.title}</h3>
            <p style="font-size: 0.85rem; color: var(--text-muted);">
              ${p.summary ? p.summary.slice(0, 110) + '...' : ''}
            </p>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;">
          <div style="text-align: right;">
            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Budget</div>
            <div style="font-size: 1.2rem; font-weight: 800; color: var(--text-main);">${formatINR(p.budget)}</div>
            <div style="font-size: 0.8rem; color: var(--accent); font-weight: 600;">${formatINR(p.remaining_budget)} remaining</div>
          </div>

          <div style="display: flex; gap: 0.5rem;">
            <a href="${viewUrl}" class="btn btn-sm btn-primary" title="View Recommendations">
              <i class="fa-solid fa-eye"></i> View
            </a>
            <a href="/recommendation/${p.id}" class="btn btn-sm btn-secondary" title="View Full Details">
              <i class="fa-solid fa-file-lines"></i> Details
            </a>
            <button class="btn btn-sm btn-secondary" onclick="reuseFromHistory(${p.id})" title="Reuse Parameters">
              <i class="fa-solid fa-rotate-right"></i>
            </button>
            <button class="btn btn-sm btn-danger-outline" onclick="confirmDeleteHistory(${p.id})" title="Delete Plan">
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    `;
  });
  html += '</div>';

  container.innerHTML = html;
}

async function reuseFromHistory(planId) {
  try {
    const res = await fetch(`/api/recommendations/${planId}/reuse`, { method: 'POST' });
    const data = await res.json();
    if (res.ok && data.success) {
      if (data.data.planner_type === 'home') {
        localStorage.setItem('reuse_home_data', JSON.stringify(data.data.input_data));
      } else if (data.data.planner_type === 'party') {
        localStorage.setItem('reuse_party_data', JSON.stringify(data.data.input_data));
      } else if (data.data.planner_type === 'jewelry') {
        localStorage.setItem('reuse_jewelry_data', JSON.stringify(data.data.input_data));
      }
      window.location.href = data.data.target_url;
    } else {
      showToast('Could not load plan parameters.', 'error');
    }
  } catch (err) {
    showToast('Network error while reusing plan.', 'error');
  }
}

let planIdToDelete = null;

function confirmDeleteHistory(planId) {
  planIdToDelete = planId;
  const modal = document.getElementById('delete-modal');
  if (modal) modal.style.display = 'flex';
}

function closeDeleteModal() {
  planIdToDelete = null;
  const modal = document.getElementById('delete-modal');
  if (modal) modal.style.display = 'none';
}

async function executeDeleteHistory() {
  if (!planIdToDelete) return;
  try {
    const res = await fetch(`/api/history/${planIdToDelete}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Plan deleted from history.', 'success');
      closeDeleteModal();
      loadHistory();
    } else {
      showToast('Could not delete plan.', 'error');
    }
  } catch (err) {
    showToast('Network error deleting plan.', 'error');
  }
}
