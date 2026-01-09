// Global variables
let expenses = [];
let categories = [];
let stats = {};
let categoryChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async () => {
    await loadCategories();
    await loadExpenses();
    await loadStats();
    setupEventListeners();
    setTodayDate();
});

// Load categories
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        categories = await response.json();
        
        const categorySelect = document.getElementById('expenseCategory');
        categorySelect.innerHTML = '<option value="">Select Category</option>';
        
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categorySelect.appendChild(option);
        });
    } catch (error) {
        showNotification('Failed to load categories', 'error');
    }
}

// Load expenses
async function loadExpenses() {
    try {
        const response = await fetch('/api/expenses');
        expenses = await response.json();
        renderExpenses();
    } catch (error) {
        showNotification('Failed to load expenses', 'error');
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        stats = await response.json();
        updateStatsDisplay();
        updateCategoryChart();
    } catch (error) {
        showNotification('Failed to load statistics', 'error');
    }
}

// Update stats display
function updateStatsDisplay() {
    document.getElementById('totalSpent').textContent = `₹${stats.total_spent?.toLocaleString('en-IN') || 0}`;
    document.getElementById('budgetRemaining').textContent = `₹${stats.remaining?.toLocaleString('en-IN') || 0}`;
    document.getElementById('expenseCount').textContent = stats.expense_count || 0;
    
    // Update budget progress
    const percentage = Math.min(stats.budget_used_percentage || 0, 100);
    document.getElementById('budgetProgress').style.width = `${percentage}%`;
    document.getElementById('budgetPercentage').textContent = `${percentage.toFixed(1)}%`;
    
    // Change progress color based on usage
    const progressFill = document.getElementById('budgetProgress');
    if (percentage > 90) {
        progressFill.style.background = 'linear-gradient(90deg, #EF4444, #DC2626)';
    } else if (percentage > 70) {
        progressFill.style.background = 'linear-gradient(90deg, #FB923C, #F97316)';
    } else {
        progressFill.style.background = 'linear-gradient(90deg, #3B82F6, #1E3A8A)';
    }
}

// Update category chart
function updateCategoryChart() {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    const categoryTotals = stats.category_totals || {};
    const labels = Object.keys(categoryTotals);
    const data = Object.values(categoryTotals);
    
    if (labels.length === 0) {
        // Show empty state
        ctx.font = '16px Arial';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('No expenses yet', ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }
    
    const colors = [
        '#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE',
        '#FB923C', '#FDBA74', '#FED7AA', '#FEF3E2', '#FFFBEB'
    ];
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ₹${value.toLocaleString('en-IN')} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Render expenses list
function renderExpenses() {
    const expensesList = document.getElementById('expensesList');
    const expensesTotal = document.getElementById('expensesTotal');
    
    if (expenses.length === 0) {
        expensesList.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <i class="fas fa-receipt" style="font-size: 3rem; margin-bottom: 15px; opacity: 0.3;"></i>
                <p>No expenses recorded yet</p>
                <p style="font-size: 0.9rem; margin-top: 5px;">Add your first expense using the form above</p>
            </div>
        `;
        expensesTotal.textContent = 'Total: ₹0';
        return;
    }
    
    // Sort expenses by date (newest first)
    const sortedExpenses = [...expenses].sort((a, b) => new Date(b.date) - new Date(a.date));
    
    expensesList.innerHTML = sortedExpenses.map(expense => `
        <div class="expense-item">
            <div class="expense-info">
                <div class="expense-title">${expense.title}</div>
                <div class="expense-details">
                    <span class="expense-category">${expense.category}</span>
                    <span><i class="fas fa-calendar"></i> ${formatDate(expense.date)}</span>
                    ${expense.description ? `<span><i class="fas fa-comment"></i> ${expense.description}</span>` : ''}
                </div>
            </div>
            <div class="expense-amount">₹${expense.amount.toLocaleString('en-IN')}</div>
            <div class="expense-actions">
                <button class="btn-delete" onclick="deleteExpense('${expense.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
    
    const total = expenses.reduce((sum, expense) => sum + expense.amount, 0);
    expensesTotal.textContent = `Total: ₹${total.toLocaleString('en-IN')}`;
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('expenseForm').addEventListener('submit', addExpense);
}

// Set today's date as default
function setTodayDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('expenseDate').value = today;
}

// Add expense
async function addExpense(e) {
    e.preventDefault();
    
    const formData = {
        title: document.getElementById('expenseTitle').value,
        amount: parseFloat(document.getElementById('expenseAmount').value),
        category: document.getElementById('expenseCategory').value,
        date: document.getElementById('expenseDate').value,
        description: document.getElementById('expenseDescription').value
    };
    
    try {
        const response = await fetch('/api/expenses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const newExpense = await response.json();
            expenses.push(newExpense);
            
            // Reset form
            document.getElementById('expenseForm').reset();
            setTodayDate();
            
            // Refresh data
            await loadStats();
            renderExpenses();
            
            showNotification('Expense added successfully!', 'success');
        } else {
            showNotification('Failed to add expense', 'error');
        }
    } catch (error) {
        showNotification('Failed to add expense', 'error');
    }
}

// Delete expense
async function deleteExpense(expenseId) {
    if (!confirm('Are you sure you want to delete this expense?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/expenses/${expenseId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            expenses = expenses.filter(expense => expense.id !== expenseId);
            
            // Refresh data
            await loadStats();
            renderExpenses();
            
            showNotification('Expense deleted successfully!', 'success');
        } else {
            showNotification('Failed to delete expense', 'error');
        }
    } catch (error) {
        showNotification('Failed to delete expense', 'error');
    }
}

// Logout function
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST'
        });
        
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        showNotification('Logout failed', 'error');
    }
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