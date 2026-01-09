// Global variables
let analyticsData = {};
let pastMonthData = [];
let dailyTrendChart = null;
let categoryChart = null;
let comparisonChart = null;

// Initialize analytics dashboard
document.addEventListener('DOMContentLoaded', async () => {
    await loadAnalyticsData();
    await loadPastMonthData();
    updateSummaryCards();
    createCharts();
    renderRecommendations();
    renderUnnecessaryExpenses();
});

// Load analytics summary data
async function loadAnalyticsData() {
    try {
        const response = await fetch('/api/analytics-summary');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        analyticsData = data;
    } catch (error) {
        console.error('Error loading analytics data:', error);
        showNotification('Failed to load analytics data: ' + error.message, 'error');
        
        // Set default analytics data to prevent UI errors
        analyticsData = {
            total_spent: 0,
            category_totals: {},
            daily_spending: {},
            unnecessary_expenses: [],
            savings_potential: 0,
            recommendations: [],
            expense_count: 0
        };
    }
}

// Load past month detailed data
async function loadPastMonthData() {
    try {
        const response = await fetch('/api/past-month-data');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        pastMonthData = data;
    } catch (error) {
        console.error('Error loading past month data:', error);
        showNotification('Failed to load past month data: ' + error.message, 'error');
        
        // Set default past month data
        pastMonthData = [];
    }
}

// Update summary cards
function updateSummaryCards() {
    document.getElementById('pastMonthTotal').textContent = `₹${analyticsData.total_spent?.toLocaleString('en-IN') || 0}`;
    document.getElementById('savingsPotential').textContent = `₹${Math.round(analyticsData.savings_potential || 0).toLocaleString('en-IN')}`;
    document.getElementById('dailyAverage').textContent = `₹${Math.round((analyticsData.total_spent || 0) / 30).toLocaleString('en-IN')}`;
    document.getElementById('transactionCount').textContent = analyticsData.expense_count || 0;
}

// Create all charts
function createCharts() {
    createDailyTrendChart();
    createCategoryChart();
    createComparisonChart();
}

// Create daily spending trend chart
function createDailyTrendChart() {
    const ctx = document.getElementById('dailyTrendChart').getContext('2d');
    
    if (dailyTrendChart) {
        dailyTrendChart.destroy();
    }
    
    // Prepare daily data
    const dailyData = analyticsData.daily_spending || {};
    const dates = Object.keys(dailyData).sort();
    const amounts = dates.map(date => dailyData[date]);
    
    // Format dates for display
    const labels = dates.map(date => {
        const d = new Date(date);
        return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    });
    
    dailyTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Spending',
                data: amounts,
                borderColor: '#1E3A8A',
                backgroundColor: 'rgba(30, 58, 138, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#FB923C',
                pointBorderColor: '#1E3A8A',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `₹${context.parsed.y.toLocaleString('en-IN')}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString('en-IN');
                        }
                    },
                    grid: {
                        color: 'rgba(30, 58, 138, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(30, 58, 138, 0.1)'
                    }
                }
            }
        }
    });
}

// Create category breakdown chart
function createCategoryChart() {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    const categoryTotals = analyticsData.category_totals || {};
    const labels = Object.keys(categoryTotals);
    const data = Object.values(categoryTotals);
    
    if (labels.length === 0) {
        ctx.font = '16px Arial';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
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
                hoverOffset: 8
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

// Create category comparison chart
function createComparisonChart() {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    if (comparisonChart) {
        comparisonChart.destroy();
    }
    
    const categoryTotals = analyticsData.category_totals || {};
    const labels = Object.keys(categoryTotals);
    const data = Object.values(categoryTotals);
    
    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Amount Spent',
                data: data,
                backgroundColor: [
                    '#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE',
                    '#FB923C', '#FDBA74', '#FED7AA', '#FEF3E2'
                ],
                borderColor: '#1E3A8A',
                borderWidth: 1,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `₹${context.parsed.y.toLocaleString('en-IN')}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString('en-IN');
                        }
                    },
                    grid: {
                        color: 'rgba(30, 58, 138, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45
                    }
                }
            }
        }
    });
}

// Render savings recommendations
function renderRecommendations() {
    const recommendationsGrid = document.getElementById('recommendationsGrid');
    const recommendations = analyticsData.recommendations || [];
    
    if (recommendations.length === 0) {
        recommendationsGrid.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666; grid-column: 1 / -1;">
                <i class="fas fa-check-circle" style="font-size: 3rem; margin-bottom: 15px; color: #FB923C;"></i>
                <p style="font-size: 1.2rem;">Great job! Your spending looks optimized.</p>
                <p style="margin-top: 10px;">Keep up the good financial habits!</p>
            </div>
        `;
        return;
    }
    
    recommendationsGrid.innerHTML = recommendations.map(rec => `
        <div class="recommendation-card">
            <div class="recommendation-header">
                <div class="recommendation-category">${rec.category}</div>
                <div class="savings-badge">Save ₹${rec.savings.toLocaleString('en-IN')}</div>
            </div>
            
            <div class="recommendation-details">
                <div class="amount-comparison">
                    <span class="current-amount">Current: ₹${rec.current.toLocaleString('en-IN')}</span>
                    <span class="suggested-amount">Suggested: ₹${rec.suggested.toLocaleString('en-IN')}</span>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${(rec.suggested / rec.current * 100)}%"></div>
                </div>
            </div>
            
            <div class="recommendation-tip">
                <i class="fas fa-lightbulb" style="margin-right: 8px; color: #FB923C;"></i>
                ${rec.tip}
            </div>
        </div>
    `).join('');
}

// Render unnecessary expenses
function renderUnnecessaryExpenses() {
    const expensesList = document.getElementById('unnecessaryExpensesList');
    const unnecessaryExpenses = analyticsData.unnecessary_expenses || [];
    
    if (unnecessaryExpenses.length === 0) {
        expensesList.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <i class="fas fa-thumbs-up" style="font-size: 3rem; margin-bottom: 15px; color: #FB923C;"></i>
                <p style="font-size: 1.2rem;">No unnecessary expenses found!</p>
                <p style="margin-top: 10px;">Your spending habits are on track.</p>
            </div>
        `;
        return;
    }
    
    expensesList.innerHTML = unnecessaryExpenses.map(expense => {
        const potentialSaving = Math.round(expense.amount * 0.3);
        return `
            <div class="expense-item">
                <div class="expense-info">
                    <div class="expense-title">${expense.title}</div>
                    <div class="expense-details">
                        <span class="expense-category">${expense.category}</span>
                        <span><i class="fas fa-calendar"></i> ${formatDate(expense.date)}</span>
                        <span><i class="fas fa-comment"></i> ${expense.description}</span>
                    </div>
                </div>
                <div class="expense-amount">₹${expense.amount.toLocaleString('en-IN')}</div>
                <div class="potential-savings">
                    <i class="fas fa-piggy-bank"></i> Save ₹${potentialSaving.toLocaleString('en-IN')}
                </div>
            </div>
        `;
    }).join('');
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