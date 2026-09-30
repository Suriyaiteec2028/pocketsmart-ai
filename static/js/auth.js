// PocketSmart AI - Authentication JavaScript

document.addEventListener('DOMContentLoaded', () => {
  // Login Form Handler
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const rememberMe = document.getElementById('remember-me')?.checked || false;
      const errorDiv = document.getElementById('auth-error');
      const submitBtn = document.getElementById('submit-btn');

      if (!email || !password) {
        showError(errorDiv, 'Please enter both email and password.');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Signing in...';
      hideError(errorDiv);

      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, remember_me: rememberMe })
        });

        const data = await response.json();
        if (response.ok && data.success) {
          showToast(data.message || 'Login successful!', 'success');
          // Store token in localStorage as backup for client-side API calls
          if (data.data && data.data.access_token) {
            localStorage.setItem('ps_token', data.data.access_token);
          }
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 600);
        } else {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fa-solid fa-arrow-right-to-bracket"></i> Sign In';
          showError(errorDiv, data.detail || data.message || 'Invalid email or password.');
        }
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-arrow-right-to-bracket"></i> Sign In';
        showError(errorDiv, 'Network error. Please try again.');
      }
    });
  }

  // Registration Form Handler
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirm_password').value;
      const errorDiv = document.getElementById('auth-error');
      const submitBtn = document.getElementById('submit-btn');

      if (!name || !email || !password || !confirmPassword) {
        showError(errorDiv, 'All fields are required.');
        return;
      }

      if (password.length < 6) {
        showError(errorDiv, 'Password must be at least 6 characters long.');
        return;
      }

      if (password !== confirmPassword) {
        showError(errorDiv, 'Passwords do not match.');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating Account...';
      hideError(errorDiv);

      try {
        const response = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name,
            email,
            password,
            confirm_password: confirmPassword
          })
        });

        const data = await response.json();
        if (response.ok && data.success) {
          showToast('Account created successfully! Welcome to PocketSmart AI.', 'success');
          if (data.data && data.data.access_token) {
            localStorage.setItem('ps_token', data.data.access_token);
          }
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 600);
        } else {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fa-solid fa-user-plus"></i> Create Account';
          showError(errorDiv, data.detail || data.message || 'Registration failed.');
        }
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-user-plus"></i> Create Account';
        showError(errorDiv, 'Network error. Please check your connection.');
      }
    });
  }

  function showError(div, message) {
    if (!div) return;
    div.style.display = 'block';
    div.innerText = message;
  }

  function hideError(div) {
    if (!div) return;
    div.style.display = 'none';
    div.innerText = '';
  }
});
