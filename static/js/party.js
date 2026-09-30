// PocketSmart AI - Party Planner JavaScript

document.addEventListener('DOMContentLoaded', () => {
  const accommodationCheckbox = document.getElementById('need-accommodation');
  const roomCountContainer = document.getElementById('room-count-container');
  const form = document.getElementById('party-planner-form');

  // Toggle accommodation room count
  if (accommodationCheckbox && roomCountContainer) {
    accommodationCheckbox.addEventListener('change', () => {
      roomCountContainer.style.display = accommodationCheckbox.checked ? 'block' : 'none';
    });
  }

  // Check for reuse data
  const prefillRaw = localStorage.getItem('reuse_party_data');
  if (prefillRaw) {
    try {
      const data = JSON.parse(prefillRaw);
      localStorage.removeItem('reuse_party_data');
      prefillPartyForm(data);
    } catch (e) {
      console.warn('Could not parse party prefill data');
    }
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const budget = parseFloat(document.getElementById('budget').value);
      const eventType = document.getElementById('event-type').value;
      const guestCount = parseInt(document.getElementById('guest-count').value);
      const eventDate = document.getElementById('event-date').value;
      const venueType = document.getElementById('venue-type').value;
      const location = document.getElementById('location').value.trim();
      const cateringPref = document.getElementById('catering-pref').value;
      const decorationLevel = document.getElementById('decoration-level').value;
      const entertainment = document.getElementById('entertainment').value;
      const needAcc = document.getElementById('need-accommodation').checked;
      const roomCount = needAcc ? (parseInt(document.getElementById('room-count').value) || 1) : 0;
      const additionalNotes = document.getElementById('additional-notes').value;

      if (!budget || budget <= 0) {
        showToast('Please enter a valid budget greater than ₹0', 'error');
        return;
      }

      if (!guestCount || guestCount <= 0) {
        showToast('Guest count must be at least 1 person.', 'error');
        return;
      }

      const payload = {
        budget,
        currency: "INR",
        event_type: eventType,
        guest_count: guestCount,
        event_date: eventDate || null,
        venue_type: venueType,
        location: location || "City Center",
        catering_preference: cateringPref,
        decoration_level: decorationLevel,
        entertainment: entertainment,
        need_accommodation: needAcc,
        room_count: roomCount,
        additional_requirements: additionalNotes
      };

      startPartyLoading();

      try {
        const response = await fetch('/api/generate-party', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (response.ok && data.success && data.data && data.data.plan_id) {
          showToast('Party plan generated successfully!', 'success');
          window.location.href = `/party-recommendations/${data.data.plan_id}`;
        } else {
          stopPartyLoading();
          showToast(data.detail || data.message || 'Failed to generate party plan.', 'error');
        }
      } catch (err) {
        stopPartyLoading();
        showToast('Network error while planning party.', 'error');
      }
    });
  }

  function startPartyLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('active');

    const s1 = document.getElementById('party-step-1');
    const s2 = document.getElementById('party-step-2');
    const s3 = document.getElementById('party-step-3');

    if (s1) s1.className = 'step-item active';
    setTimeout(() => {
      if (s1) s1.className = 'step-item completed';
      if (s2) s2.className = 'step-item active';
    }, 1200);

    setTimeout(() => {
      if (s2) s2.className = 'step-item completed';
      if (s3) s3.className = 'step-item active';
    }, 2400);
  }

  function stopPartyLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
  }

  function prefillPartyForm(data) {
    if (data.budget) document.getElementById('budget').value = data.budget;
    if (data.event_type) document.getElementById('event-type').value = data.event_type;
    if (data.guest_count) document.getElementById('guest-count').value = data.guest_count;
    if (data.event_date) document.getElementById('event-date').value = data.event_date;
    if (data.venue_type) document.getElementById('venue-type').value = data.venue_type;
    if (data.location) document.getElementById('location').value = data.location;
    if (data.catering_preference) document.getElementById('catering-pref').value = data.catering_preference;
    if (data.decoration_level) document.getElementById('decoration-level').value = data.decoration_level;
    if (data.entertainment) document.getElementById('entertainment').value = data.entertainment;
    if (data.need_accommodation) {
      document.getElementById('need-accommodation').checked = true;
      roomCountContainer.style.display = 'block';
      if (data.room_count) document.getElementById('room-count').value = data.room_count;
    }
    if (data.additional_requirements) document.getElementById('additional-notes').value = data.additional_requirements;

    showToast('Loaded previously saved party details.', 'info');
  }
});
