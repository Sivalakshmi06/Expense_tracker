from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import uuid
import random

app = Flask(__name__)
app.secret_key = 'expense_tracker_secret_key_change_in_production'

# Configure for deployment
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Add error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Unhandled exception: {str(e)}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

# In-memory storage
users = {}
expenses = {}
past_month_data = {}
categories = [
    'Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 
    'Bills & Utilities', 'Healthcare', 'Education', 'Travel', 'Other'
]

# Initialize sample past month data for all users
def init_sample_data():
    """Initialize sample past month data for demonstration"""
    # Sample user for demo purposes
    users['demo@example.com'] = {
        'id': 'demo_user',
        'email': 'demo@example.com',
        'password': 'demo123',
        'name': 'Demo User',
        'monthly_budget': 60000
    }
    
    # Initialize expenses for demo user
    expenses['demo_user'] = [
        {
            'id': str(uuid.uuid4()),
            'title': 'Grocery Shopping',
            'amount': 2500,
            'category': 'Food & Dining',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': 'Weekly groceries from supermarket'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Metro Card Recharge',
            'amount': 500,
            'category': 'Transportation',
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'description': 'Monthly metro pass'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Movie Tickets',
            'amount': 800,
            'category': 'Entertainment',
            'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'description': 'Weekend movie with friends'
        }
    ]
    
    # Generate past month data for demo user
    past_month_data['demo_user'] = generate_past_month_data('demo_user')

def generate_past_month_data(user_id):
    """Generate realistic past month expense data totaling ₹50,000"""
    try:
        past_expenses = []
        base_date = datetime.now() - timedelta(days=30)
        
        # Define expense patterns for realistic data
        expense_patterns = [
            # Daily essentials
            {'category': 'Food & Dining', 'items': ['Breakfast', 'Lunch', 'Dinner', 'Snacks', 'Coffee'], 'range': (50, 500)},
            {'category': 'Transportation', 'items': ['Metro', 'Auto', 'Uber', 'Petrol', 'Bus'], 'range': (20, 300)},
            
            # Weekly expenses
            {'category': 'Shopping', 'items': ['Groceries', 'Clothes', 'Electronics', 'Books', 'Household'], 'range': (200, 2000)},
            {'category': 'Entertainment', 'items': ['Movies', 'Games', 'Streaming', 'Events', 'Sports'], 'range': (100, 1000)},
            
            # Monthly bills
            {'category': 'Bills & Utilities', 'items': ['Electricity', 'Internet', 'Phone', 'Water', 'Gas'], 'range': (500, 3000)},
            {'category': 'Healthcare', 'items': ['Medicine', 'Doctor Visit', 'Gym', 'Supplements'], 'range': (200, 2000)},
            {'category': 'Education', 'items': ['Course Fee', 'Books', 'Online Learning', 'Certification'], 'range': (500, 5000)},
            {'category': 'Travel', 'items': ['Weekend Trip', 'Vacation', 'Flight', 'Hotel'], 'range': (1000, 8000)},
            {'category': 'Other', 'items': ['Gifts', 'Charity', 'Miscellaneous', 'Emergency'], 'range': (100, 2000)}
        ]
        
        total_spent = 0
        target_total = 50000
        
        # Generate 60-80 transactions over 30 days
        num_transactions = random.randint(60, 80)
        
        for i in range(num_transactions):
            try:
                # Random date in past 30 days
                days_ago = random.randint(0, 29)
                expense_date = base_date + timedelta(days=days_ago)
                
                # Choose category based on realistic distribution
                category_weights = [0.25, 0.15, 0.15, 0.10, 0.10, 0.08, 0.07, 0.05, 0.05]
                category = random.choices(categories, weights=category_weights)[0]
                
                # Find pattern for category
                pattern = next((p for p in expense_patterns if p['category'] == category), expense_patterns[0])
                
                # Calculate amount (adjust to reach target total)
                remaining_transactions = num_transactions - i
                remaining_amount = target_total - total_spent
                
                if remaining_transactions > 0:
                    avg_remaining = remaining_amount / remaining_transactions
                    min_amt, max_amt = pattern['range']
                    
                    # Adjust range based on remaining budget
                    if avg_remaining > max_amt:
                        amount = random.randint(max_amt, min(int(avg_remaining * 1.5), max_amt * 2))
                    elif avg_remaining < min_amt:
                        amount = random.randint(min(min_amt, max(1, remaining_amount)), max(1, remaining_amount))
                    else:
                        amount = random.randint(min_amt, max_amt)
                else:
                    amount = remaining_amount
                
                # Ensure we don't exceed target and amount is positive
                if total_spent + amount > target_total:
                    amount = target_total - total_spent
                
                if amount <= 0:
                    continue
                    
                expense = {
                    'id': str(uuid.uuid4()),
                    'title': random.choice(pattern['items']),
                    'amount': amount,
                    'category': category,
                    'date': expense_date.strftime('%Y-%m-%d'),
                    'description': f'Past month expense - {category.lower()}'
                }
                
                past_expenses.append(expense)
                total_spent += amount
                
                if total_spent >= target_total:
                    break
                    
            except Exception as e:
                print(f"Error generating expense {i}: {str(e)}")
                continue
        
        # Sort by date
        past_expenses.sort(key=lambda x: x['date'])
        
        return past_expenses
        
    except Exception as e:
        print(f"Error generating past month data for user {user_id}: {str(e)}")
        return []  # Return empty lis

# Initialize sample data
init_sample_data()

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'ExpenseFlow is running'}), 200

@app.route('/')
def index():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('auth.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if email in users and users[email]['password'] == password:
            user_id = users[email]['id']
            session['user_id'] = user_id
            session['user_name'] = users[email]['name']
            
            # Ensure past month data exists for this user
            if user_id not in past_month_data:
                print(f"Generating past month data for existing user: {user_id}")
                past_month_data[user_id] = generate_past_month_data(user_id)
            
            return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    budget = data.get('budget', 30000)
    
    if email in users:
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    user_id = str(uuid.uuid4())
    users[email] = {
        'id': user_id,
        'email': email,
        'password': password,
        'name': name,
        'monthly_budget': budget
    }
    
    # Add some sample expenses for new users to demonstrate the app
    expenses[user_id] = [
        {
            'id': str(uuid.uuid4()),
            'title': 'Grocery Shopping',
            'amount': 2500,
            'category': 'Food & Dining',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': 'Weekly groceries from supermarket'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Metro Card Recharge',
            'amount': 500,
            'category': 'Transportation',
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'description': 'Monthly metro pass'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Movie Tickets',
            'amount': 800,
            'category': 'Entertainment',
            'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'description': 'Weekend movie with friends'
        }
    ]
    
    # Generate past month data
    past_month_data[user_id] = generate_past_month_data(user_id)
    
    session['user_id'] = user_id
    session['user_name'] = name
    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/expenses')
def get_expenses():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    user_expenses = expenses.get(user_id, [])
    return jsonify(user_expenses)

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = session['user_id']
        
        # Validate required fields
        required_fields = ['title', 'amount', 'category']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate amount is a number
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': 'Amount must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid amount format'}), 400
        
        expense = {
            'id': str(uuid.uuid4()),
            'title': str(data['title']).strip(),
            'amount': amount,
            'category': str(data['category']).strip(),
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'description': str(data.get('description', '')).strip()
        }
        
        if user_id not in expenses:
            expenses[user_id] = []
        
        expenses[user_id].append(expense)
        return jsonify(expense)
        
    except Exception as e:
        print(f"Error adding expense: {str(e)}")  # For debugging
        return jsonify({'error': 'Failed to add expense'}), 500

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    user_expenses = expenses.get(user_id, [])
    
    expenses[user_id] = [exp for exp in user_expenses if exp['id'] != expense_id]
    return jsonify({'success': True})

@app.route('/api/stats')
def get_stats():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        user_expenses = expenses.get(user_id, [])
        
        # Find user data
        user = None
        for u in users.values():
            if u['id'] == user_id:
                user = u
                break
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Calculate statistics
        total_spent = sum(exp['amount'] for exp in user_expenses)
        budget = user.get('monthly_budget', 30000)
        remaining = budget - total_spent
        
        # Category breakdown
        category_totals = {}
        for exp in user_expenses:
            cat = exp['category']
            category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
        
        return jsonify({
            'total_spent': total_spent,
            'budget': budget,
            'remaining': remaining,
            'budget_used_percentage': (total_spent / budget * 100) if budget > 0 else 0,
            'category_totals': category_totals,
            'expense_count': len(user_expenses)
        })
        
    except Exception as e:
        print(f"Error getting stats: {str(e)}")  # For debugging
        return jsonify({'error': 'Failed to load statistics'}), 500

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('analytics.html')

@app.route('/api/past-month-data')
def get_past_month_data():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        
        # Ensure past month data exists for this user
        if user_id not in past_month_data:
            print(f"Generating past month data for user: {user_id}")
            past_month_data[user_id] = generate_past_month_data(user_id)
        
        past_data = past_month_data.get(user_id, [])
        print(f"Returning {len(past_data)} past month expenses totaling ₹{sum(exp['amount'] for exp in past_data)}")
        
        return jsonify(past_data)
        
    except Exception as e:
        print(f"Error getting past month data: {str(e)}")
        return jsonify({'error': 'Failed to load past month data'}), 500

@app.route('/api/analytics-summary')
def get_analytics_summary():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        past_data = past_month_data.get(user_id, [])
        
        # Calculate analytics
        total_spent = sum(exp['amount'] for exp in past_data)
        
        # Category breakdown
        category_totals = {}
        for exp in past_data:
            cat = exp['category']
            category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
        
        # Daily spending pattern
        daily_spending = {}
        for exp in past_data:
            date = exp['date']
            daily_spending[date] = daily_spending.get(date, 0) + exp['amount']
        
        # Identify unnecessary expenses with more detailed criteria
        unnecessary_expenses = []
        savings_potential = 0
        
        for exp in past_data:
            is_unnecessary = False
            saving_percentage = 0
            reason = ""
            
            # Food & Dining - expensive meals/dining out
            if exp['category'] == 'Food & Dining' and exp['amount'] > 400:
                is_unnecessary = True
                saving_percentage = 0.4  # 40% savings potential
                reason = "Expensive dining - consider home cooking"
            elif exp['category'] == 'Food & Dining' and exp['amount'] > 250:
                is_unnecessary = True
                saving_percentage = 0.25  # 25% savings potential
                reason = "Frequent dining out - reduce frequency"
            
            # Entertainment - high entertainment costs
            elif exp['category'] == 'Entertainment' and exp['amount'] > 800:
                is_unnecessary = True
                saving_percentage = 0.5  # 50% savings potential
                reason = "Expensive entertainment - find cheaper alternatives"
            elif exp['category'] == 'Entertainment' and exp['amount'] > 400:
                is_unnecessary = True
                saving_percentage = 0.3  # 30% savings potential
                reason = "High entertainment spending - consider free activities"
            
            # Shopping - non-essential purchases
            elif exp['category'] == 'Shopping' and exp['amount'] > 1500:
                is_unnecessary = True
                saving_percentage = 0.6  # 60% savings potential
                reason = "Expensive shopping - avoid impulse purchases"
            elif exp['category'] == 'Shopping' and exp['amount'] > 800:
                is_unnecessary = True
                saving_percentage = 0.35  # 35% savings potential
                reason = "Frequent shopping - create a budget"
            
            # Transportation - expensive rides
            elif exp['category'] == 'Transportation' and exp['amount'] > 200:
                is_unnecessary = True
                saving_percentage = 0.3  # 30% savings potential
                reason = "Expensive transport - use public transport"
            
            # Other categories with high amounts
            elif exp['category'] == 'Other' and exp['amount'] > 1000:
                is_unnecessary = True
                saving_percentage = 0.4  # 40% savings potential
                reason = "High miscellaneous spending - track expenses better"
            
            if is_unnecessary:
                exp_copy = exp.copy()
                exp_copy['saving_potential'] = exp['amount'] * saving_percentage
                exp_copy['saving_reason'] = reason
                exp_copy['saving_percentage'] = saving_percentage * 100
                unnecessary_expenses.append(exp_copy)
                savings_potential += exp['amount'] * saving_percentage
        
        # Generate more comprehensive savings recommendations
        recommendations = []
        
        # Food & Dining recommendations
        food_spending = category_totals.get('Food & Dining', 0)
        if food_spending > 12000:
            recommendations.append({
                'category': 'Food & Dining',
                'current': food_spending,
                'suggested': 10000,
                'savings': food_spending - 10000,
                'tip': 'Cook more meals at home, meal prep on weekends, and limit dining out to special occasions'
            })
        elif food_spending > 8000:
            recommendations.append({
                'category': 'Food & Dining',
                'current': food_spending,
                'suggested': 7000,
                'savings': food_spending - 7000,
                'tip': 'Try cooking 2-3 more meals at home per week and pack lunch for work'
            })
        
        # Entertainment recommendations
        entertainment_spending = category_totals.get('Entertainment', 0)
        if entertainment_spending > 4000:
            recommendations.append({
                'category': 'Entertainment',
                'current': entertainment_spending,
                'suggested': 2500,
                'savings': entertainment_spending - 2500,
                'tip': 'Explore free entertainment like parks, free museums, home movie nights, and community events'
            })
        elif entertainment_spending > 2500:
            recommendations.append({
                'category': 'Entertainment',
                'current': entertainment_spending,
                'suggested': 2000,
                'savings': entertainment_spending - 2000,
                'tip': 'Look for discounts, group deals, and free activities in your area'
            })
        
        # Shopping recommendations
        shopping_spending = category_totals.get('Shopping', 0)
        if shopping_spending > 6000:
            recommendations.append({
                'category': 'Shopping',
                'current': shopping_spending,
                'suggested': 4000,
                'savings': shopping_spending - 4000,
                'tip': 'Create a shopping list, wait 24 hours before non-essential purchases, and compare prices online'
            })
        elif shopping_spending > 4000:
            recommendations.append({
                'category': 'Shopping',
                'current': shopping_spending,
                'suggested': 3000,
                'savings': shopping_spending - 3000,
                'tip': 'Set a monthly shopping budget and stick to it. Avoid impulse purchases'
            })
        
        # Transportation recommendations
        transport_spending = category_totals.get('Transportation', 0)
        if transport_spending > 4000:
            recommendations.append({
                'category': 'Transportation',
                'current': transport_spending,
                'suggested': 3000,
                'savings': transport_spending - 3000,
                'tip': 'Use public transport, carpool, or walk/bike for short distances. Plan trips efficiently'
            })
        
        return jsonify({
            'total_spent': total_spent,
            'category_totals': category_totals,
            'daily_spending': daily_spending,
            'unnecessary_expenses': unnecessary_expenses,
            'savings_potential': savings_potential,
            'recommendations': recommendations,
            'expense_count': len(past_data)
        })
        
    except Exception as e:
        print(f"Error getting analytics summary: {str(e)}")  # For debugging
        return jsonify({'error': 'Failed to load analytics data'}), 500

@app.route('/api/regenerate-past-data', methods=['POST'])
def regenerate_past_data():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        print(f"Regenerating past month data for user: {user_id}")
        
        # Force regenerate past month data
        past_month_data[user_id] = generate_past_month_data(user_id)
        
        total_amount = sum(exp['amount'] for exp in past_month_data[user_id])
        expense_count = len(past_month_data[user_id])
        
        print(f"Generated {expense_count} expenses totaling ₹{total_amount}")
        
        return jsonify({
            'success': True, 
            'message': f'Generated {expense_count} expenses totaling ₹{total_amount:,.0f}',
            'total_amount': total_amount,
            'expense_count': expense_count
        })
        
    except Exception as e:
        print(f"Error regenerating past data: {str(e)}")
        return jsonify({'error': 'Failed to regenerate data'}), 500

@app.route('/api/categories')
def get_categories():
    return jsonify(categories)

if __name__ == '__main__':
    app.run(debug=True)