// Slide management
let currentSlide = 1;
const totalSlides = 3;

function showSlide(slideNumber) {
    // Hide all slides
    for (let i = 1; i <= totalSlides; i++) {
        document.getElementById(`slide${i}`).classList.remove('active');
        document.querySelectorAll('.indicator')[i-1].classList.remove('active');
    }
    
    // Show selected slide
    document.getElementById(`slide${slideNumber}`).classList.add('active');
    document.querySelectorAll('.indicator')[slideNumber-1].classList.add('active');
    currentSlide = slideNumber;
}

// Auto-rotate slides
setInterval(() => {
    currentSlide = currentSlide >= totalSlides ? 1 : currentSlide + 1;
    showSlide(currentSlide);
}, 4000);

// Form switching
function switchToRegister() {
    document.getElementById('loginForm').classList.remove('active');
    document.getElementById('registerForm').classList.add('active');
}

function switchToLogin() {
    document.getElementById('registerForm').classList.remove('active');
    document.getElementById('loginForm').classList.add('active');
}

// Notification system
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Login form handler
document.getElementById('loginFormElement').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Login failed. Please try again.', 'error');
    }
});

// Register form handler
document.getElementById('registerFormElement').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const budget = document.getElementById('registerBudget').value;
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password, budget: parseInt(budget) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Registration successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Registration failed. Please try again.', 'error');
    }
});

// Set today's date as default
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('expenseDate');
    if (dateInput) {
        dateInput.value = today;
    }
});