// PocketSmart AI - Jewelry Planner JavaScript

document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('outfit-image-input');
  const dropZone = document.getElementById('image-drop-zone');
  const previewContainer = document.getElementById('image-preview-container');
  const previewImg = document.getElementById('preview-image');
  const removeBtn = document.getElementById('remove-image-btn');
  const form = document.getElementById('jewelry-planner-form');

  let uploadedImageUrl = null;

  // Check for prefill / reuse data
  const prefillRaw = localStorage.getItem('reuse_jewelry_data');
  if (prefillRaw) {
    try {
      const data = JSON.parse(prefillRaw);
      localStorage.removeItem('reuse_jewelry_data');
      prefillJewelryForm(data);
    } catch (e) {
      console.warn('Could not parse jewelry prefill data');
    }
  }

  // Drag and drop events
  if (dropZone && fileInput) {
    ['dragenter', 'dragover'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary)';
        dropZone.style.background = 'var(--primary-light)';
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border)';
        dropZone.style.background = '#fff';
      });
    });

    dropZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files.length > 0) {
        handleImageFile(files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (fileInput.files && fileInput.files.length > 0) {
        handleImageFile(fileInput.files[0]);
      }
    });
  }

  if (removeBtn) {
    removeBtn.addEventListener('click', () => {
      uploadedImageUrl = null;
      fileInput.value = '';
      previewContainer.style.display = 'none';
      dropZone.style.display = 'block';
    });
  }

  async function handleImageFile(file) {
    // Validate client-side
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      showToast('Invalid file format. Please upload JPG, PNG, or WEBP.', 'error');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      showToast('File exceeds 5MB size limit.', 'error');
      return;
    }

    // Show instant local preview
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      dropZone.style.display = 'none';
      previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);

    // Upload to server
    const formData = new FormData();
    formData.append('file', file);

    showToast('Uploading image for visual AI analysis...', 'info');

    try {
      const response = await fetch('/api/upload-image', {
        method: 'POST',
        body: formData
      });

      const res = await response.json();
      if (response.ok && res.success && res.data && res.data.image_url) {
        uploadedImageUrl = res.data.image_url;
        showToast('Outfit image uploaded & ready for AI analysis!', 'success');
      } else {
        showToast(res.detail || 'Image upload failed.', 'error');
      }
    } catch (err) {
      showToast('Network error uploading image.', 'error');
    }
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const budget = parseFloat(document.getElementById('budget').value);
      const occasion = document.getElementById('occasion').value;
      const jewelryType = document.getElementById('jewelry-type').value;
      const preferredStyle = document.getElementById('preferred-style').value;
      const preferredMaterial = document.getElementById('preferred-material').value;
      const preferredColor = document.getElementById('preferred-color').value;
      const outfitDescription = document.getElementById('outfit-description').value.trim();

      if (!budget || budget <= 0) {
        showToast('Please enter a valid budget greater than ₹0', 'error');
        return;
      }

      const payload = {
        budget,
        currency: "INR",
        occasion,
        jewelry_type: jewelryType,
        preferred_style: preferredStyle,
        preferred_material: preferredMaterial,
        preferred_color: preferredColor,
        outfit_description: outfitDescription,
        image_url: uploadedImageUrl
      };

      startJewelryLoading();

      try {
        const response = await fetch('/api/generate-jewelry', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (response.ok && data.success && data.data && data.data.plan_id) {
          showToast('Jewelry recommendations generated successfully!', 'success');
          window.location.href = `/jewelry-recommendations/${data.data.plan_id}`;
        } else {
          stopJewelryLoading();
          showToast(data.detail || data.message || 'Failed to generate jewelry styling.', 'error');
        }
      } catch (err) {
        stopJewelryLoading();
        showToast('Network error during jewelry styling.', 'error');
      }
    });
  }

  function startJewelryLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('active');

    const s1 = document.getElementById('j-step-1');
    const s2 = document.getElementById('j-step-2');
    const s3 = document.getElementById('j-step-3');

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

  function stopJewelryLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
  }

  function prefillJewelryForm(data) {
    if (data.budget) document.getElementById('budget').value = data.budget;
    if (data.occasion) document.getElementById('occasion').value = data.occasion;
    if (data.jewelry_type) document.getElementById('jewelry-type').value = data.jewelry_type;
    if (data.preferred_style) document.getElementById('preferred-style').value = data.preferred_style;
    if (data.preferred_material) document.getElementById('preferred-material').value = data.preferred_material;
    if (data.preferred_color) document.getElementById('preferred-color').value = data.preferred_color;
    if (data.outfit_description) document.getElementById('outfit-description').value = data.outfit_description;

    showToast('Loaded previously saved jewelry preferences.', 'info');
  }
});
