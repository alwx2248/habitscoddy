from flask import *
from datetime import *

app = Flask(__name__)
habits = {}
next_id = 1

def save_habit(name, goal):
    global next_id
    habit = {
        'id': next_id,
        'name': name,
        'goal': goal,
        'created_at': str(date.today()),
        'logs': {},
        'active': True  # Добавили статус активности по умолчанию
    }
    habits[next_id] = habit
    next_id += 1
    return habit

def get_stats(habit):
    logs = habit['logs']
    total_days = len(logs)
    completed_days = sum(1 for completed in logs.values() if completed)
    current_streak = 0
    dates = sorted(logs.keys(), reverse=True)
    for log_date in dates:
        if logs.get(log_date):
            current_streak += 1
        else:
            break

    succes_rate = (completed_days / total_days * 100) if total_days > 0 else 0
    return {
        'total_days': total_days,
        'completed': completed_days,
        'missed': total_days - completed_days,
        'current_streak': current_streak,
        'succes_rate': round(succes_rate, 1)
    }

@app.route('/')
def index():
    habits_list = list(habits.values())
    for habit in habits_list:
        habit['stats'] = get_stats(habit)
    return render_template('index.html', habits=habits_list)

@app.route('/add', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        name = request.form.get('name')
        try:
            goal = int(request.form.get('goal', 1))
        except ValueError:
            goal = 1
            
        if name:
            save_habit(name, goal)
            return redirect(url_for('index'))
    return render_template('add_habit.html')

@app.route('/habit/<int:habit_id>')
def habit_detail(habit_id):
    habit = habits.get(habit_id)
    if not habit:
        return "Привычка не найдена", 404
        
    logs = sorted(habit['logs'].items(), reverse=True)
    stats = get_stats(habit)
    
    return render_template('habit_detail.html',
                habit=habit,
                logs=logs,
                stats=stats,
                today=str(date.today()))

@app.route('/log/<int:habit_id>', methods=['POST'])
def log_habit(habit_id):
    habit = habits.get(habit_id)
    if habit:
        today = str(date.today())
        habit['logs'][today] = True
    return redirect(url_for('habit_detail', habit_id=habit_id))

@app.route('/skip/<int:habit_id>', methods=['POST'])
def skip_habit(habit_id):
    habit = habits.get(habit_id)
    if habit:
        today = str(date.today())
        habit['logs'][today] = False
    return redirect(url_for('habit_detail', habit_id=habit_id))

@app.route('/delete/<int:habit_id>')
def delete_habit(habit_id):
    if habit_id in habits:
        del habits[habit_id]
    return redirect(url_for('index'))

@app.route('/edit/<int:habit_id>', methods=['GET', 'POST'])
def edit_habit(habit_id):
    habit = habits.get(habit_id)
    if not habit:
        return "Привычка не найдена", 404
        
    if request.method == 'POST':
        new_name = request.form.get('name')
        try:
            new_goal = int(request.form.get('goal', habit['goal']))
        except ValueError:
            new_goal = habit['goal']
            
        if new_name:
            habit['name'] = new_name
        habit['goal'] = new_goal
        return redirect(url_for('habit_detail', habit_id=habit_id))
        
    return render_template('add_habit.html', habit=habit) # Используем тот же шаблон или создайте edit_habit.html

@app.route('/toggle/<int:habit_id>')
def toggle_habit(habit_id): # Переименовали, чтобы не было конфликта
    habit = habits.get(habit_id)
    if habit:
        habit['active'] = not habit.get('active', True)
    return redirect(url_for('index'))

# Тестовые данные
if not habits:
    h1 = save_habit("Зарядка", 30)
    h1['logs']['2024-01-15'] = True
    h1['logs']['2024-01-16'] = True
    
    h2 = save_habit("Читать книги", 30)
    h2['logs']['2024-01-15'] = True

if __name__ == '__main__':
    print("=" * 50)
    print("Сервер запущен!")
    app.run(debug=True)
