import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Initialize Flask application
app = Flask(__name__)

# Production config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '7af2c690aae6babb4dbae4cb939fa0fd5bccaf86498f1d540390f44d1d2a7cca')

# Database config with PostgreSQL support
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Session Security Configuration
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Database Models
class userdetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    
    # NEW fields
    admin_id = db.Column(db.Integer, db.ForeignKey('userdetail.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    students = db.relationship('userdetail', backref=db.backref('admin', remote_side=[id]), lazy=True)
    quiz_attempts = db.relationship('QuizAttempt', backref='student', lazy=True)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('userdetail.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    students = db.relationship('userdetail', backref='class_enrolled', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    questions = db.relationship('Question', backref='chapter', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    marks = db.Column(db.Integer, nullable=False, default=1)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetail.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    quiz_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    
    # NEW fields
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('userdetail.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    passing_marks = db.Column(db.Integer, nullable=True)
    show_answers = db.Column(db.Boolean, default=True)
    shuffle_questions = db.Column(db.Boolean, default=False)
    
    chapter = db.relationship('Chapter', backref='quizzes')
    # Relationships
    assignments = db.relationship('QuizAssignment', backref='quiz', lazy=True)
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

class QuizAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('userdetail.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey('userdetail.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    max_attempts = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='pending')

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('userdetail.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    time_taken = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Float, default=0.0)
    total_marks = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, default=0.0)
    answers = db.relationship('StudentAnswer', backref='attempt', lazy=True, cascade='all, delete-orphan')

class StudentAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    marks_obtained = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Integer, nullable=True)

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return redirect(url_for('user'))

@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = userdetail.query.filter_by(username=username).first()
        
        # Check if password is hashed (starts with pbkdf2:sha256)
        if user and user.role == role:
            if user.password.startswith('pbkdf2:sha256'):
                # Use hashed password check
                if check_password_hash(user.password, password):
                    session['username'] = username
                    session['role'] = role
                    session['user_id'] = user.id
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    
                    if role == 'admin':
                        return redirect(url_for('admin', username=username))
                    else:
                        return redirect(url_for('userdash', username=username))
            else:
                # Legacy plaintext password check (for backward compatibility)
                if user.password == password:
                    session['username'] = username
                    session['role'] = role
                    session['user_id'] = user.id
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    
                    if role == 'admin':
                        return redirect(url_for('admin', username=username))
                    else:
                        return redirect(url_for('userdash', username=username))
        
        return render_template('user.html', error='Invalid credentials or role')
    
    return render_template('user.html')

@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')
        role = request.form.get('role')
        
        existing_user = userdetail.query.filter_by(username=username).first()
        if existing_user:
            return render_template('newuser.html', error='Username already exists')
        
        dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = userdetail(
            name=name,
            username=username,
            password=hashed_password,
            qualification=qualification,
            dob=dob_date,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('user'))
    
    return render_template('newuser.html')

@app.route('/userdash/<username>')
def userdash(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('user'))
    
    return render_template('userdash.html', n=username)

@app.route('/admin/<username>')
def admin(username):
    if 'username' not in session or session['username'] != username or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    subjects = Subject.query.all()
    
    for subject in subjects:
        for chapter in subject.chapters:
            chapter.num_questions = len(chapter.questions)
    
    return render_template('admin.html', n=username, subjects=subjects)

@app.route('/addsubject', methods=['GET', 'POST'])
def addsubject():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        
        return redirect(url_for('admin', username=session['username']))
    
    return render_template('addsubject.html')

@app.route('/addchapter/<int:subject_id>', methods=['GET', 'POST'])
def addchapter(subject_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        
        return redirect(url_for('admin', username=session['username']))
    
    return render_template('addchapter.html', subject=subject, chapter=None)

@app.route('/addquestion/<int:chapter_id>', methods=['GET', 'POST'])
def addquestion(chapter_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    chapters = Chapter.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        text = request.form.get('text')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')
        marks = request.form.get('marks')
        selected_chapter_id = request.form.get('chapter_id')
        
        new_question = Question(
            title=title,
            text=text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            marks=int(marks),
            chapter_id=int(selected_chapter_id)
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        return redirect(url_for('quiz', chapter_id=selected_chapter_id))
    
    return render_template('addquestion.html', chapter=chapter, chapters=chapters)

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    
    return redirect(url_for('admin', username=session['username']))

@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    
    return redirect(url_for('admin', username=session['username']))

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    subject = chapter.subject
    
    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.description = request.form.get('description')
        db.session.commit()
        
        return redirect(url_for('admin', username=session['username']))
    
    return render_template('addchapter.html', subject=subject, chapter=chapter)

@app.route('/quiz/<int:chapter_id>', methods=['GET', 'POST'])
def quiz(chapter_id):
    if 'username' not in session:
        return redirect(url_for('user'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    questions = chapter.questions
    
    if request.method == 'POST':
        return redirect(url_for('admin', username=session['username']))
    
    return render_template('quiz.html', chapter=chapter, questions=questions)

@app.route('/newquiz', methods=['GET', 'POST'])
def new_quiz():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        quiz_date = request.form.get('quiz_date')
        duration = request.form.get('duration')
        total_marks = request.form.get('total_marks')
        
        quiz_date_obj = datetime.strptime(quiz_date, '%Y-%m-%d').date()
        
        new_quiz = Quiz(
            chapter_id=int(chapter_id),
            quiz_date=quiz_date_obj,
            duration=int(duration),
            total_marks=int(total_marks)
        )
        
        db.session.add(new_quiz)
        db.session.commit()
        
        return redirect(url_for('admin', username=session['username']))
    
    chapters = Chapter.query.all()
    return render_template('NewQuiz.html', chapters=chapters)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user'))

# Student Management Routes
@app.route('/admin/<username>/students')
def manage_students(username):
    """Admin view to manage their students"""
    if 'username' not in session or session['username'] != username or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    admin = userdetail.query.filter_by(username=username, role='admin').first()
    if not admin:
        return redirect(url_for('user'))
    
    students = userdetail.query.filter_by(admin_id=admin.id, role='user').all()
    return render_template('manage_students.html', admin=admin, students=students)

@app.route('/admin/add_student', methods=['POST'])
def add_student():
    """Admin creates a student account"""
    if 'role' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    admin_id = request.form['admin_id']
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
    qualification = request.form['qualification']
    class_id = request.form.get('class_id')
    
    # Check if username already exists
    existing_user = userdetail.query.filter_by(username=username).first()
    if existing_user:
        flash('Username already exists!', 'danger')
        return redirect(url_for('manage_students', username=session.get('username')))
    
    # Hash password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    new_student = userdetail(
        name=name,
        username=username,
        password=hashed_password,
        dob=dob,
        qualification=qualification,
        role='user',
        admin_id=admin_id,
        class_id=int(class_id) if class_id else None
    )
    
    db.session.add(new_student)
    db.session.commit()
    
    flash('Student added successfully!', 'success')
    return redirect(url_for('manage_students', username=session.get('username')))

# Quiz Assignment Routes
@app.route('/admin/assign_quiz', methods=['POST'])
def assign_quiz():
    """Assign quiz to students"""
    if 'role' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    quiz_id = request.form['quiz_id']
    student_ids = request.form.getlist('student_ids')
    due_date = request.form.get('due_date')
    max_attempts = request.form.get('max_attempts', 1)
    
    for student_id in student_ids:
        assignment = QuizAssignment(
            quiz_id=quiz_id,
            student_id=student_id,
            assigned_by=session.get('user_id'),
            due_date=datetime.strptime(due_date, '%Y-%m-%d') if due_date else None,
            max_attempts=max_attempts
        )
        db.session.add(assignment)
    
    db.session.commit()
    flash(f'Quiz assigned to {len(student_ids)} students!', 'success')
    return redirect(url_for('admin', username=session.get('username')))

# Quiz Taking Routes
@app.route('/student/quiz/<int:quiz_id>/start', methods=['POST'])
def start_quiz(quiz_id):
    """Start a quiz attempt"""
    if 'user_id' not in session:
        return redirect(url_for('user'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    student_id = session.get('user_id')
    
    # Check if already attempted
    existing_attempt = QuizAttempt.query.filter_by(
        quiz_id=quiz_id, 
        student_id=student_id,
        completed_at=None
    ).first()
    
    if existing_attempt:
        return redirect(url_for('take_quiz', attempt_id=existing_attempt.id))
    
    # Create new attempt
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=student_id,
        total_marks=quiz.total_marks,
        started_at=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.commit()
    
    return redirect(url_for('take_quiz', attempt_id=attempt.id))

@app.route('/quiz/take/<int:attempt_id>')
def take_quiz(attempt_id):
    """Quiz taking interface with timer"""
    if 'user_id' not in session:
        return redirect(url_for('user'))
    
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    quiz = attempt.quiz
    
    # Security check
    if attempt.student_id != session.get('user_id'):
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('userdash', username=session.get('username')))
    
    # Check if already completed
    if attempt.completed_at:
        flash('This quiz has already been submitted!', 'warning')
        return redirect(url_for('view_results', attempt_id=attempt_id))
    
    # Get questions for this quiz
    questions = Question.query.filter_by(chapter_id=quiz.chapter_id).all()
    
    # Shuffle if enabled
    if quiz.shuffle_questions:
        import random
        random.shuffle(questions)
    
    return render_template('take_quiz.html', 
                         quiz=quiz, 
                         questions=questions, 
                         attempt=attempt)

@app.route('/quiz/submit/<int:attempt_id>', methods=['POST'])
@csrf.exempt  # We'll handle CSRF manually in the template
def submit_quiz(attempt_id):
    """Submit quiz and calculate score"""
    if 'user_id' not in session:
        return redirect(url_for('user'))
    
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Security check
    if attempt.student_id != session.get('user_id'):
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('userdash', username=session.get('username')))
    
    # Check if already completed
    if attempt.completed_at:
        flash('This quiz has already been submitted!', 'warning')
        return redirect(url_for('view_results', attempt_id=attempt_id))
    
    quiz = attempt.quiz
    questions = Question.query.filter_by(chapter_id=quiz.chapter_id).all()
    
    score = 0
    time_taken = int(request.form.get('time_taken', 0))
    
    for question in questions:
        selected = request.form.get(f'question_{question.id}')
        if selected:
            is_correct = (selected == question.correct_option)
            marks = question.marks if is_correct else 0
            score += marks
            
            # Save answer
            answer = StudentAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_option=selected,
                is_correct=is_correct,
                marks_obtained=marks
            )
            db.session.add(answer)
    
    # Update attempt
    attempt.completed_at = datetime.utcnow()
    attempt.time_taken = time_taken
    attempt.score = score
    attempt.percentage = (score / quiz.total_marks) * 100 if quiz.total_marks > 0 else 0
    
    db.session.commit()
    
    flash(f'Quiz submitted! Your score: {score}/{quiz.total_marks} ({attempt.percentage:.1f}%)', 'success')
    return redirect(url_for('view_results', attempt_id=attempt.id))

# Results & Analytics Routes
@app.route('/student/results/<int:attempt_id>')
def view_results(attempt_id):
    """View detailed quiz results"""
    if 'user_id' not in session:
        return redirect(url_for('user'))
    
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Security check
    if attempt.student_id != session.get('user_id') and session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('userdash', username=session.get('username')))
    
    quiz = attempt.quiz
    answers = StudentAnswer.query.filter_by(attempt_id=attempt_id).all()
    
    # Get questions with answers
    question_results = []
    for answer in answers:
        question = Question.query.get(answer.question_id)
        question_results.append({
            'question': question,
            'answer': answer
        })
    
    return render_template('quiz_results.html', 
                         attempt=attempt, 
                         quiz=quiz, 
                         question_results=question_results)

@app.route('/admin/<username>/analytics')
def admin_analytics(username):
    """Admin analytics dashboard"""
    if 'username' not in session or session['username'] != username or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    admin = userdetail.query.filter_by(username=username, role='admin').first()
    if not admin:
        return redirect(url_for('user'))
    
    # Get all students
    students = userdetail.query.filter_by(admin_id=admin.id, role='user').all()
    
    # Get all quiz attempts by admin's students
    attempts = QuizAttempt.query.join(userdetail).filter(
        userdetail.admin_id == admin.id,
        QuizAttempt.completed_at != None
    ).all()
    
    # Calculate statistics
    total_students = len(students)
    total_quizzes_taken = len(attempts)
    average_score = sum(a.percentage for a in attempts) / len(attempts) if attempts else 0
    
    return render_template('admin_analytics.html',
                         admin=admin,
                         students=students,
                         attempts=attempts,
                         stats={
                             'total_students': total_students,
                             'total_quizzes': total_quizzes_taken,
                             'average_score': average_score
                         })

# Health check endpoint
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

# Production server config
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)