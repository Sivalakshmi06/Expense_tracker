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

@app.route('/api/debug/routes')
def list_routes():
    """Debug endpoint to list all available routes"""
    try:
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        return jsonify({
            'routes': routes,
            'total_routes': len(routes),
            'session_data': {
                'user_id': session.get('user_id'),
                'user_name': session.get('user_name'),
                'session_keys': list(session.keys())
            },
            'data_status': {
                'users_count': len(users),
                'expenses_users': list(expenses.keys()),
                'past_month_users': list(past_month_data.keys())
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/session')
def debug_session():
    """Debug endpoint to check session status"""
    try:
        return jsonify({
            'session_data': dict(session),
            'user_authenticated': 'user_id' in session,
            'user_id': session.get('user_id'),
            'user_name': session.get('user_name'),
            'session_keys': list(session.keys())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'ExpenseFlow is running'}), 200

@app.route('/api/debug/test-endpoints')
def test_endpoints():
    """Test all API endpoints to ensure they're working"""
    try:
        results = {}
        
        # Test health endpoint
        try:
            results['health'] = 'OK'
        except Exception as e:
            results['health'] = f'ERROR: {str(e)}'
        
        # Test if user is authenticated
        if 'user_id' in session:
            user_id = session['user_id']
            results['authentication'] = f'OK - User: {user_id}'
            
            # Test expenses endpoint
            try:
                user_expenses = expenses.get(user_id, [])
                results['expenses'] = f'OK - {len(user_expenses)} expenses'
            except Exception as e:
                results['expenses'] = f'ERROR: {str(e)}'
            
            # Test stats endpoint
            try:
                user_expenses = expenses.get(user_id, [])
                total_spent = sum(exp.get('amount', 0) for exp in user_expenses)
                results['stats'] = f'OK - Total spent: ₹{total_spent}'
            except Exception as e:
                results['stats'] = f'ERROR: {str(e)}'
            
            # Test past month data
            try:
                past_data = past_month_data.get(user_id, [])
                if not past_data:
                    past_month_data[user_id] = generate_past_month_data(user_id)
                    past_data = past_month_data[user_id]
                results['past_month_data'] = f'OK - {len(past_data)} past expenses'
            except Exception as e:
                results['past_month_data'] = f'ERROR: {str(e)}'
            
            # Test analytics summary
            try:
                past_data = past_month_data.get(user_id, [])
                total = sum(exp.get('amount', 0) for exp in past_data)
                results['analytics_summary'] = f'OK - Past month total: ₹{total}'
            except Exception as e:
                results['analytics_summary'] = f'ERROR: {str(e)}'
        else:
            results['authentication'] = 'ERROR - Not authenticated'
        
        return jsonify({
            'test_results': results,
            'timestamp': datetime.now().isoformat(),
            'session_info': {
                'user_id': session.get('user_id'),
                'user_name': session.get('user_name')
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    try:
        print("Expenses endpoint called")  # Debug log
        
        if 'user_id' not in session:
            print("User not authenticated for expenses")
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        print(f"Getting expenses for user: {user_id}")
        
        # Ensure user exists in expenses dict
        if user_id not in expenses:
            expenses[user_id] = []
            print(f"Initialized empty expenses for user: {user_id}")
        
        user_expenses = expenses.get(user_id, [])
        print(f"Found {len(user_expenses)} expenses")
        
        # Ensure all expenses have required fields
        valid_expenses = []
        for exp in user_expenses:
            if isinstance(exp, dict) and 'id' in exp and 'amount' in exp:
                # Ensure all required fields exist with defaults
                valid_exp = {
                    'id': exp.get('id', str(uuid.uuid4())),
                    'title': exp.get('title', 'Expense'),
                    'amount': exp.get('amount', 0),
                    'category': exp.get('category', 'Other'),
                    'date': exp.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'description': exp.get('description', '')
                }
                valid_expenses.append(valid_exp)
        
        # Update the stored expenses with validated data
        expenses[user_id] = valid_expenses
        
        return jsonify(valid_expenses)
        
    except Exception as e:
        print(f"Error getting expenses: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return empty array to prevent frontend errors
        return jsonify([])

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
        print("Stats endpoint called")  # Debug log
        
        if 'user_id' not in session:
            print("User not authenticated")
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        print(f"Getting stats for user: {user_id}")
        
        # Ensure user exists in expenses dict
        if user_id not in expenses:
            expenses[user_id] = []
            print(f"Initialized empty expenses for user: {user_id}")
        
        user_expenses = expenses.get(user_id, [])
        print(f"Found {len(user_expenses)} expenses for user")
        
        # Find user data - more robust search
        user = None
        for email, user_data in users.items():
            if user_data['id'] == user_id:
                user = user_data
                break
        
        if not user:
            print(f"User {user_id} not found in users database")
            # Create a default user to prevent errors
            user = {
                'id': user_id,
                'monthly_budget': 30000,
                'name': 'User',
                'email': 'user@example.com'
            }
            print(f"Created default user data for {user_id}")
        
        # Calculate statistics
        total_spent = sum(exp['amount'] for exp in user_expenses)
        budget = user.get('monthly_budget', 30000)
        remaining = max(0, budget - total_spent)  # Ensure remaining is not negative
        
        # Category breakdown
        category_totals = {}
        for exp in user_expenses:
            cat = exp.get('category', 'Other')  # Default category if missing
            category_totals[cat] = category_totals.get(cat, 0) + exp.get('amount', 0)
        
        stats_data = {
            'total_spent': total_spent,
            'budget': budget,
            'remaining': remaining,
            'budget_used_percentage': min(100, (total_spent / budget * 100)) if budget > 0 else 0,
            'category_totals': category_totals,
            'expense_count': len(user_expenses)
        }
        
        print(f"Returning stats: {stats_data}")
        return jsonify(stats_data)
        
    except Exception as e:
        print(f"Error getting stats: {str(e)}")  # For debugging
        import traceback
        traceback.print_exc()
        
        # Return default stats to prevent frontend errors
        default_stats = {
            'total_spent': 0,
            'budget': 30000,
            'remaining': 30000,
            'budget_used_percentage': 0,
            'category_totals': {},
            'expense_count': 0
        }
        return jsonify(default_stats)

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('analytics.html')

@app.route('/debug')
def debug_page():
    """Debug page to test endpoints"""
    return render_template('debug.html')

@app.route('/api/past-month-data')
def get_past_month_data():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        
        # Ensure past month data exists for this user
        if user_id not in past_month_data or not past_month_data[user_id]:
            print(f"Generating past month data for user: {user_id}")
            past_month_data[user_id] = generate_past_month_data(user_id)
        
        past_data = past_month_data.get(user_id, [])
        total_amount = sum(exp['amount'] for exp in past_data)
        
        print(f"Returning {len(past_data)} past month expenses totaling ₹{total_amount}")
        
        # If still no data, generate some basic sample data
        if not past_data:
            print("No past data found, creating minimal sample data")
            past_data = [
                {
                    'id': str(uuid.uuid4()),
                    'title': 'Sample Expense',
                    'amount': 50000,
                    'category': 'Other',
                    'date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
                    'description': 'Sample past month data'
                }
            ]
            past_month_data[user_id] = past_data
        
        return jsonify(past_data)
        
    except Exception as e:
        print(f"Error getting past month data: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return minimal sample data to prevent frontend errors
        sample_data = [
            {
                'id': str(uuid.uuid4()),
                'title': 'Sample Expense',
                'amount': 50000,
                'category': 'Other',
                'date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
                'description': 'Sample past month data'
            }
        ]
        return jsonify(sample_data)

@app.route('/api/analytics-summary')
def get_analytics_summary():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        
        # Ensure past month data exists
        if user_id not in past_month_data or not past_month_data[user_id]:
            print(f"Generating past month data for analytics: {user_id}")
            past_month_data[user_id] = generate_past_month_data(user_id)
        
        past_data = past_month_data.get(user_id, [])
        
        # If still no data, create minimal sample
        if not past_data:
            past_data = [
                {
                    'id': str(uuid.uuid4()),
                    'title': 'Sample Expense',
                    'amount': 50000,
                    'category': 'Other',
                    'date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
                    'description': 'Sample past month data'
                }
            ]
            past_month_data[user_id] = past_data
        
        # Calculate analytics
        total_spent = sum(exp['amount'] for exp in past_data)
        
        # Category breakdown
        category_totals = {}
        for exp in past_data:
            cat = exp.get('category', 'Other')
            category_totals[cat] = category_totals.get(cat, 0) + exp.get('amount', 0)
        
        # Daily spending pattern
        daily_spending = {}
        for exp in past_data:
            date = exp.get('date', datetime.now().strftime('%Y-%m-%d'))
            daily_spending[date] = daily_spending.get(date, 0) + exp.get('amount', 0)
        
        # Identify unnecessary expenses with more detailed criteria
        unnecessary_expenses = []
        savings_potential = 0
        
        for exp in past_data:
            is_unnecessary = False
            saving_percentage = 0
            reason = ""
            amount = exp.get('amount', 0)
            category = exp.get('category', 'Other')
            
            # Food & Dining - expensive meals/dining out
            if category == 'Food & Dining' and amount > 400:
                is_unnecessary = True
                saving_percentage = 0.4  # 40% savings potential
                reason = "Expensive dining - consider home cooking"
            elif category == 'Food & Dining' and amount > 250:
                is_unnecessary = True
                saving_percentage = 0.25  # 25% savings potential
                reason = "Frequent dining out - reduce frequency"
            
            # Entertainment - high entertainment costs
            elif category == 'Entertainment' and amount > 800:
                is_unnecessary = True
                saving_percentage = 0.5  # 50% savings potential
                reason = "Expensive entertainment - find cheaper alternatives"
            elif category == 'Entertainment' and amount > 400:
                is_unnecessary = True
                saving_percentage = 0.3  # 30% savings potential
                reason = "High entertainment spending - consider free activities"
            
            # Shopping - non-essential purchases
            elif category == 'Shopping' and amount > 1500:
                is_unnecessary = True
                saving_percentage = 0.6  # 60% savings potential
                reason = "Expensive shopping - avoid impulse purchases"
            elif category == 'Shopping' and amount > 800:
                is_unnecessary = True
                saving_percentage = 0.35  # 35% savings potential
                reason = "Frequent shopping - create a budget"
            
            # Transportation - expensive rides
            elif category == 'Transportation' and amount > 200:
                is_unnecessary = True
                saving_percentage = 0.3  # 30% savings potential
                reason = "Expensive transport - use public transport"
            
            # Other categories with high amounts
            elif category == 'Other' and amount > 1000:
                is_unnecessary = True
                saving_percentage = 0.4  # 40% savings potential
                reason = "High miscellaneous spending - track expenses better"
            
            if is_unnecessary:
                exp_copy = exp.copy()
                exp_copy['saving_potential'] = amount * saving_percentage
                exp_copy['saving_reason'] = reason
                exp_copy['saving_percentage'] = saving_percentage * 100
                unnecessary_expenses.append(exp_copy)
                savings_potential += amount * saving_percentage
        
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
        
        analytics_data = {
            'total_spent': total_spent,
            'category_totals': category_totals,
            'daily_spending': daily_spending,
            'unnecessary_expenses': unnecessary_expenses,
            'savings_potential': savings_potential,
            'recommendations': recommendations,
            'expense_count': len(past_data)
        }
        
        print(f"Returning analytics for {len(past_data)} expenses, total: ₹{total_spent}")
        return jsonify(analytics_data)
        
    except Exception as e:
        print(f"Error getting analytics summary: {str(e)}")  # For debugging
        import traceback
        traceback.print_exc()
        
        # Return minimal analytics data to prevent frontend errors
        default_analytics = {
            'total_spent': 50000,
            'category_totals': {'Other': 50000},
            'daily_spending': {datetime.now().strftime('%Y-%m-%d'): 50000},
            'unnecessary_expenses': [],
            'savings_potential': 0,
            'recommendations': [],
            'expense_count': 1
        }
        return jsonify(default_analytics)

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