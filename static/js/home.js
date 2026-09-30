// PocketSmart AI - Home Planner JavaScript

const ROOM_CATALOG = {
  "Living Room": [
    { name: "Sofa", defaultQty: 1, styles: ["Modern", "Minimalist", "Scandinavian", "Traditional"], materials: ["Fabric", "Leatherette", "Solid Wood"], colors: ["Grey", "Beige", "Navy", "Teal"], priority: "High" },
    { name: "Coffee Table", defaultQty: 1, styles: ["Modern", "Minimalist", "Industrial"], materials: ["Engineered Wood", "Glass", "Metal"], colors: ["Brown", "White", "Black"], priority: "Medium" },
    { name: "TV Unit", defaultQty: 1, styles: ["Modern", "Minimalist"], materials: ["Engineered Wood", "Sheesham"], colors: ["Walnut", "Oak", "White"], priority: "High" },
    { name: "Floor/Ceiling Lighting", defaultQty: 1, styles: ["Modern", "Warm"], materials: ["Metal", "Fabric"], colors: ["Warm White", "Brass", "Black"], priority: "Medium" },
    { name: "Living Room Rug", defaultQty: 1, styles: ["Geometric", "Boho", "Solid"], materials: ["Jute", "Cotton", "Wool"], colors: ["Neutral", "Grey", "Multi"], priority: "Low" },
    { name: "Curtains (Pair)", defaultQty: 2, styles: ["Blackout", "Sheer"], materials: ["Polyester", "Cotton"], colors: ["Grey", "Cream", "Teal"], priority: "Medium" },
    { name: "Wall Decor / Art", defaultQty: 1, styles: ["Minimalist", "Canvas"], materials: ["Framed Canvas", "Wood"], colors: ["Abstract", "Nature"], priority: "Low" }
  ],
  "Bedroom": [
    { name: "Bed Frame with Storage", defaultQty: 1, styles: ["Modern", "Minimalist", "Platform"], materials: ["Engineered Wood", "Solid Sheesham"], colors: ["Walnut", "Teak", "Grey"], priority: "High" },
    { name: "Orthopedic Mattress", defaultQty: 1, styles: ["Medium Firm", "Memory Foam"], materials: ["High Density Foam", "Coir"], colors: ["White", "Grey"], priority: "High" },
    { name: "Wardrobe", defaultQty: 1, styles: ["2-Door", "3-Door", "Sliding"], materials: ["Engineered Wood", "MDF"], colors: ["Walnut", "White", "Wenge"], priority: "High" },
    { name: "Bedside Lamp", defaultQty: 2, styles: ["Warm Ambient", "Focus"], materials: ["Ceramic", "Metal"], colors: ["Warm Glow", "White"], priority: "Medium" },
    { name: "Blackout Curtains", defaultQty: 2, styles: ["100% Blackout", "Thermal"], materials: ["Polyester", "Jacquard"], colors: ["Dark Blue", "Charcoal", "Beige"], priority: "Medium" },
    { name: "Bedside Tables", defaultQty: 2, styles: ["Minimalist", "Drawer"], materials: ["Wood", "Engineered Wood"], colors: ["Matching Bed", "White"], priority: "Low" }
  ],
  "Kitchen": [
    { name: "Storage Racks & Organizers", defaultQty: 2, styles: ["Tiered", "Under-Cabinet"], materials: ["Stainless Steel", "BPA-Free Plastic"], colors: ["Silver", "Black", "Clear"], priority: "High" },
    { name: "Under-Cabinet LED Batten", defaultQty: 1, styles: ["Daylight White", "Smart"], materials: ["Aluminum", "Polycarbonate"], colors: ["Cool White"], priority: "Medium" },
    { name: "Cooking Hob / Gas Stove", defaultQty: 1, styles: ["3-Burner", "Toughened Glass"], materials: ["Glass", "Cast Iron"], colors: ["Black"], priority: "High" },
    { name: "Spice & Dish Drainer Rack", defaultQty: 1, styles: ["Wall Mount", "Countertop"], materials: ["Stainless Steel"], colors: ["Metallic"], priority: "Medium" }
  ],
  "Dining Room": [
    { name: "Dining Table & 4 Chairs", defaultQty: 1, styles: ["Scandinavian", "Modern", "Traditional"], materials: ["Solid Pine", "Sheesham"], colors: ["Antique Wood", "Natural"], priority: "High" },
    { name: "Pendant Ceiling Light", defaultQty: 1, styles: ["Industrial", "Nordic"], materials: ["Metal Mesh", "Glass"], colors: ["Matte Black", "Brass"], priority: "Medium" }
  ],
  "Study Room": [
    { name: "Ergonomic Mesh Chair", defaultQty: 1, styles: ["High-Back", "Lumbar Support"], materials: ["Breathable Mesh", "Nylon"], colors: ["Black", "Grey"], priority: "High" },
    { name: "Study Desk with Drawer", defaultQty: 1, styles: ["Minimalist", "Cable Port"], materials: ["Engineered Wood"], colors: ["Oak", "White"], priority: "High" },
    { name: "Adjustable Task Lamp", defaultQty: 1, styles: ["Flexible Arm", "LED"], materials: ["Metal"], colors: ["Dark Grey", "Black"], priority: "Medium" }
  ],
  "Balcony": [
    { name: "Weather-Resistant Coffee Table Set", defaultQty: 1, styles: ["Bistro", "Folding"], materials: ["Cast Iron", "Rattan"], colors: ["Black", "Teak"], priority: "Medium" },
    { name: "Planter Stands & String Lights", defaultQty: 1, styles: ["Warm Fairy", "Vertical"], materials: ["Metal", "Coir"], colors: ["Warm White"], priority: "Low" }
  ],
  "Bathroom": [
    { name: "Mirror Cabinet & Vanity Storage", defaultQty: 1, styles: ["Modern Box", "LED"], materials: ["Waterproof PVC", "Mirror"], colors: ["White", "Silver"], priority: "High" },
    { name: "Non-Slip Quick Dry Floor Mats", defaultQty: 2, styles: ["Absorbent"], materials: ["Microfiber", "Diatomite"], colors: ["Grey", "Blue"], priority: "Medium" }
  ],
  "Other": [
    { name: "Multi-purpose Storage Unit", defaultQty: 1, styles: ["Modular"], materials: ["Engineered Wood"], colors: ["Neutral"], priority: "Medium" }
  ]
};

document.addEventListener('DOMContentLoaded', () => {
  const roomCheckboxes = document.querySelectorAll('input[name="rooms"]');
  const roomsContainer = document.getElementById('selected-rooms-items-container');

  // Check if we have prefill data from "Reuse Plan"
  const prefillRaw = localStorage.getItem('reuse_home_data');
  let prefillData = null;
  if (prefillRaw) {
    try {
      prefillData = JSON.parse(prefillRaw);
      localStorage.removeItem('reuse_home_data');
      prefillHomeForm(prefillData);
    } catch (e) {
      console.warn('Could not parse prefill data');
    }
  }

  function renderRoomSections() {
    if (!roomsContainer) return;
    roomsContainer.innerHTML = '';

    const selectedRooms = Array.from(document.querySelectorAll('input[name="rooms"]:checked')).map(cb => cb.value);

    if (selectedRooms.length === 0) {
      roomsContainer.innerHTML = `
        <div style="text-align: center; padding: 2rem; background: var(--bg-subtle); border-radius: var(--radius-sm); color: var(--text-muted);">
          <i class="fa-solid fa-arrow-up" style="margin-right: 6px;"></i> Please select at least one room above to customize items and preferences.
        </div>
      `;
      return;
    }

    selectedRooms.forEach(room => {
      const catalogItems = ROOM_CATALOG[room] || ROOM_CATALOG["Other"];
      const roomCard = document.createElement('div');
      roomCard.className = 'card';
      roomCard.style.marginBottom = '1.25rem';
      roomCard.style.borderLeft = '4px solid var(--primary)';

      let itemsHtml = catalogItems.map((item, idx) => `
        <div style="display: grid; grid-template-columns: 2fr 1fr 1.5fr 1fr; gap: 0.75rem; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid var(--border);" class="room-item-row" data-room="${room}" data-name="${item.name}">
          <div>
            <label style="font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; gap: 0.4rem;">
              <input type="checkbox" checked class="item-enable-check"> ${item.name}
            </label>
          </div>
          <div>
            <input type="number" min="1" max="10" value="${item.defaultQty}" class="form-control item-qty" style="padding: 0.35rem 0.5rem; font-size: 0.85rem;" title="Quantity">
          </div>
          <div>
            <select class="form-select item-style" style="padding: 0.35rem 0.5rem; font-size: 0.85rem;">
              ${item.styles.map(s => `<option value="${s}">${s}</option>`).join('')}
            </select>
          </div>
          <div>
            <select class="form-select item-priority" style="padding: 0.35rem 0.5rem; font-size: 0.85rem;">
              <option value="High" ${item.priority === 'High' ? 'selected' : ''}>High</option>
              <option value="Medium" ${item.priority === 'Medium' ? 'selected' : ''}>Medium</option>
              <option value="Low" ${item.priority === 'Low' ? 'selected' : ''}>Low</option>
            </select>
          </div>
        </div>
      `).join('');

      roomCard.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <h4 style="font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
            <i class="fa-solid fa-door-open" style="color: var(--primary);"></i> ${room} Requirements
          </h4>
          <span class="badge badge-home">${catalogItems.length} candidate items</span>
        </div>
        <div style="display: grid; grid-template-columns: 2fr 1fr 1.5fr 1fr; gap: 0.75rem; font-size: 0.75rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase; padding-bottom: 0.4rem; border-bottom: 2px solid var(--border);">
          <div>Item Name</div>
          <div>Qty</div>
          <div>Preferred Style</div>
          <div>Priority</div>
        </div>
        ${itemsHtml}
      `;

      roomsContainer.appendChild(roomCard);
    });
  }

  roomCheckboxes.forEach(cb => {
    cb.addEventListener('change', renderRoomSections);
  });

  // Initial render
  renderRoomSections();

  // Form Submission
  const form = document.getElementById('home-planner-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const budget = parseFloat(document.getElementById('budget').value);
      const homeType = document.getElementById('home-type').value;
      const overallStyle = document.getElementById('overall-style').value;
      const allocationPref = document.getElementById('allocation-pref').value;
      const additionalNotes = document.getElementById('additional-notes').value;

      const selectedRooms = Array.from(document.querySelectorAll('input[name="rooms"]:checked')).map(cb => cb.value);

      if (!budget || budget <= 0) {
        showToast('Please enter a valid budget greater than ₹0', 'error');
        return;
      }

      if (selectedRooms.length === 0) {
        showToast('Please select at least one room to furnish.', 'error');
        return;
      }

      // Collect room items
      const roomItems = {};
      selectedRooms.forEach(room => {
        roomItems[room] = [];
        const rows = document.querySelectorAll(`.room-item-row[data-room="${room}"]`);
        rows.forEach(row => {
          const isEnabled = row.querySelector('.item-enable-check').checked;
          if (isEnabled) {
            const name = row.getAttribute('data-name');
            const qty = parseInt(row.querySelector('.item-qty').value) || 1;
            const style = row.querySelector('.item-style').value;
            const priority = row.querySelector('.item-priority').value;
            roomItems[room].push({
              name,
              quantity: qty,
              preferred_style: style,
              priority
            });
          }
        });
      });

      const payload = {
        budget,
        currency: "INR",
        home_type: homeType,
        rooms: selectedRooms,
        room_items: roomItems,
        overall_style: overallStyle,
        budget_allocation_preference: allocationPref,
        additional_requirements: additionalNotes
      };

      // Show animated loading overlay
      startHomeLoading();

      try {
        const response = await fetch('/api/generate-home', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (response.ok && data.success && data.data && data.data.plan_id) {
          showToast('Home interior plan generated successfully!', 'success');
          window.location.href = `/home-recommendations/${data.data.plan_id}`;
        } else {
          stopHomeLoading();
          showToast(data.detail || data.message || 'Failed to generate recommendations.', 'error');
        }
      } catch (err) {
        stopHomeLoading();
        showToast('Network error while contacting AI engine.', 'error');
      }
    });
  }

  function startHomeLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('active');

    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');

    if (step1) step1.className = 'step-item active';
    setTimeout(() => {
      if (step1) step1.className = 'step-item completed';
      if (step2) step2.className = 'step-item active';
    }, 1200);

    setTimeout(() => {
      if (step2) step2.className = 'step-item completed';
      if (step3) step3.className = 'step-item active';
    }, 2400);
  }

  function stopHomeLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
  }

  function prefillHomeForm(data) {
    if (data.budget) document.getElementById('budget').value = data.budget;
    if (data.home_type) document.getElementById('home-type').value = data.home_type;
    if (data.overall_style) document.getElementById('overall-style').value = data.overall_style;
    if (data.budget_allocation_preference) document.getElementById('allocation-pref').value = data.budget_allocation_preference;
    if (data.additional_requirements) document.getElementById('additional-notes').value = data.additional_requirements;

    if (data.rooms && Array.isArray(data.rooms)) {
      document.querySelectorAll('input[name="rooms"]').forEach(cb => {
        cb.checked = data.rooms.includes(cb.value);
      });
      renderRoomSections();
    }
    showToast('Loaded previously saved plan parameters.', 'info');
  }
});
