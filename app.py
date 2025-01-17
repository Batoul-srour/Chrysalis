
from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
import psycopg2 
import psycopg2.extras
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
 
app = Flask(__name__)
app.secret_key = 'mariam'
 
DB_HOST = "localhost"
DB_NAME = "Chrysalis"
DB_USER = "postgres"
DB_PASS = "butterfly"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 





def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# admin login w signup part
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and user['password'] == password and user['is_admin']:
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('admin_login.html')


@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

# admin managing users
@app.route('/admin/users')
@admin_required
def admin_users():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute('SELECT u.id, u.name, u.email, r.title AS liked_recipe_title '
                       'FROM users u '
                       'LEFT JOIN likes l ON u.id = l.user_id '
                       'LEFT JOIN recipes r ON l.recipe_id = r.id')
        users = cursor.fetchall()
    
    users_dict = {}
    for user in users:
        user_id = user['id']
        if user_id not in users_dict:
            users_dict[user_id] = {
                'id': user_id,
                'name': user['name'],
                'email': user['email'],
                'liked_recipes': []
            }
        if user['liked_recipe_title']:
            users_dict[user_id]['liked_recipes'].append(user['liked_recipe_title'])

    return render_template('admin/users.html', users=list(users_dict.values()))



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to perform this action', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/like/<int:recipe_id>', methods=['POST'])
@login_required
def like_recipe(recipe_id):
    user_id = session['user_id']
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM likes WHERE user_id = %s AND recipe_id = %s', (user_id, recipe_id))
    if cursor.fetchone():
        cursor.execute('DELETE FROM likes WHERE user_id = %s AND recipe_id = %s', (user_id, recipe_id))
        conn.commit()
        liked = False
    else:
        cursor.execute('INSERT INTO likes (user_id, recipe_id) VALUES (%s, %s)', (user_id, recipe_id))
        conn.commit()
        liked = True
    cursor.close()
    return jsonify({'liked': liked})

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    user_id = session['user_id']
    cursor = conn.cursor()
    cursor.execute('DELETE FROM comments WHERE id = %s AND user_id = %s', (comment_id, user_id))
    conn.commit()
    cursor.close()
    return redirect(request.referrer)


@app.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    user_id = session['user_id']
    content = request.form['content']
    cursor = conn.cursor()
    cursor.execute('UPDATE comments SET content = %s WHERE id = %s AND user_id = %s', (content, comment_id, user_id))
    conn.commit()
    cursor.close()
    return redirect(request.referrer)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
    return redirect(url_for('admin_users'))


# manage recipes
@app.route('/admin/recipes', methods=['GET', 'POST'])
@admin_required
def admin_recipes():
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            category = request.form['category']
            ingredients = request.form['ingredients']
            preparation = request.form['preparation']
            image = request.form['image']

            # fi error hon cz it's not printing
            print(f"Captured Data: Title={title}, Description={description}, Category={category}, Ingredients={ingredients}, Preparation={preparation}, Image={image}")

            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO recipes (title, description, category, ingredients, preparation, image) VALUES (%s, %s, %s, %s, %s, %s)',
                (title, description, category, ingredients, preparation, image)
            )
            conn.commit()
            cursor.close()

            flash('Recipe added successfully', 'success')
            return redirect(url_for('admin_recipes'))
        except Exception as e:
            conn.rollback()
            print(f"Error occurred: {e}")
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('admin_recipes'))

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT r.*, COUNT(l.id) AS like_count, COUNT(c.id) AS comment_count FROM recipes r LEFT JOIN likes l ON r.id = l.recipe_id LEFT JOIN comments c ON r.id = c.recipe_id GROUP BY r.id')
    recipes = cursor.fetchall()
    cursor.close()
    return render_template('admin/manage_recipes.html', recipes=recipes)

@app.route('/admin/recipes/delete/<int:recipe_id>', methods=['POST'])
@admin_required
def delete_recipe(recipe_id):
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM recipes WHERE id = %s', (recipe_id,))
        cursor.execute('DELETE FROM likes WHERE recipe_id = %s', (recipe_id,))
        cursor.execute('DELETE FROM comments WHERE recipe_id = %s', (recipe_id,))
        conn.commit()
    return redirect(url_for('admin_recipes'))

@app.route('/admin/recipes/edit/<int:recipe_id>', methods=['GET', 'POST'])
@admin_required
def edit_recipe(recipe_id):
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        ingredients = request.form['ingredients']
        preparation = request.form['preparation']
        image = request.form['image']

        cursor = conn.cursor()
        cursor.execute('UPDATE recipes SET title = %s, category = %s, ingredients = %s, preparation = %s, image = %s WHERE id = %s',
                       (title, category, ingredients, preparation, image, recipe_id))
        conn.commit()
        cursor.close()
        flash('Recipe updated successfully', 'success')
        return redirect(url_for('admin_recipes'))

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
    recipe = cursor.fetchone()
    cursor.close()
    return render_template('admin/edit_recipe.html', recipe=recipe)

@app.route('/admin/comments/delete/<int:comment_id>', methods=['POST'])
@admin_required
def admin_delete_comment(comment_id):
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM comments WHERE id = %s', (comment_id,))
        conn.commit()
    return redirect(url_for('admin_recipes'))




#  manage reviews
@app.route('/admin/reviews', methods=['GET', 'POST'])
@admin_required
def admin_reviews():
    if request.method == 'POST':
        recipe_id = request.form['recipe_id']
        user_id = request.form['user_id']
        content = request.form['content']
        rating = request.form['rating']

        cursor = conn.cursor()
        cursor.execute('INSERT INTO reviews (recipe_id, user_id, content, rating) VALUES (%s, %s, %s, %s)',
                       (recipe_id, user_id, content, rating))
        conn.commit()
        cursor.close()
        flash('Review added successfully', 'success')
        return redirect(url_for('admin_reviews'))

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM reviews')
    reviews = cursor.fetchall()
    cursor.close()
    return render_template('admin/reviews.html', reviews=reviews)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        if not name or not email or not message:
            flash('Please fill out all fields', 'error')
        else:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO contact_requests (name, email, message) VALUES (%s, %s, %s)',
                (name, email, message)
            )
            conn.commit()
            cursor.close()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))

    return render_template('index.html')

@app.route('/admin/contact_messages')
@admin_required
def admin_contact_messages():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM contact_requests ORDER BY created_at DESC')
    messages = cursor.fetchall()
    cursor.close()
    return render_template('admin/contact_messages.html', messages=messages)

@app.route('/admin/contact_messages/delete/<int:message_id>', methods=['POST'])
@admin_required
def delete_contact_message(message_id):
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM contact_requests WHERE id = %s', (message_id,))
        conn.commit()
    flash('Message deleted successfully', 'success')
    return redirect(url_for('admin_contact_messages'))



# manage likes and comments lal admin
@app.route('/admin/interactions')
@admin_required
def admin_interactions():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM likes')
    likes = cursor.fetchall()
    cursor.execute('SELECT * FROM comments')
    comments = cursor.fetchall()
    cursor.close()
    return render_template('admin/interactions.html', likes=likes, comments=comments)

@app.route('/comment/<int:recipe_id>', methods=['POST'])
@login_required
def add_comment(recipe_id):
    print("entered add comment function")
    user_id = session['user_id']
    print(f'u------->ser session ${user_id}')
    content = request.form['content']
    cursor = conn.cursor()
    cursor.execute('INSERT INTO comments (user_id, recipe_id, content) VALUES (%s, %s, %s)', (user_id, recipe_id, content))
    conn.commit()
    cursor.close()
    return redirect(url_for('recipe', recipe_id=recipe_id))




@app.route('/')
def index():
    return render_template('index.html')

def get_recipes_by_category(category):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM recipes WHERE category = %s', (category,))
    recipes = cursor.fetchall()
    cursor.close()
    return recipes

@app.route('/recipes')
def recipes():
    recipes = get_recipes_by_category('main')
    dessert_recipes = get_recipes_by_category('dessert')
    drink_recipes = get_recipes_by_category('drink')
    appetizer_recipes = get_recipes_by_category('app')
    gallery_items = get_gallery_items()
    reviews = get_reviews()
    return render_template('recipes.html', recipes=recipes, dessert_recipes=dessert_recipes,drink_recipes=drink_recipes,appetizer_recipes=appetizer_recipes,gallery_items=gallery_items,reviews=reviews)


@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
    recipe = cursor.fetchone()

    cursor.execute('SELECT c.id, c.content, c.created_at, u.name FROM comments c JOIN users u ON c.user_id = u.id WHERE c.recipe_id = %s ORDER BY c.created_at DESC', (recipe_id,))
    comments = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM likes WHERE recipe_id = %s', (recipe_id,))
    likes_count = cursor.fetchone()[0]

    if 'user_id' in session:
        cursor.execute('SELECT 1 FROM likes WHERE user_id = %s AND recipe_id = %s', (session['user_id'], recipe_id))
        user_liked = cursor.fetchone() is not None
    else:
        user_liked = False

    cursor.close()
    return render_template('recipe.html', recipe=recipe, comments=comments, likes_count=likes_count, user_liked=user_liked)


def get_gallery_items():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM gallery')
    gallery_items = cursor.fetchall()
    cursor.close()
    return gallery_items

def get_reviews():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM reviews')
    reviews = cursor.fetchall()
    cursor.close()
    return reviews


def get_mental_articles_by_category(category):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM mental_health_articles WHERE category = %s', (category,))
    articles = cursor.fetchall()
    cursor.close()
    return articles

@app.route('/mentalHealth')
def mental_health():
    mindfulness_articles = get_mental_articles_by_category('mindfulness')
    therapy_articles = get_mental_articles_by_category('therapy')
    selfcare_articles = get_mental_articles_by_category('selfcare')
    book_items = get_mental_book_items()
    reviews = get_mental_reviews()
    return render_template('mentalHealth.html', 
                           mindfulness_articles=mindfulness_articles, 
                           therapy_articles=therapy_articles, 
                           selfcare_articles=selfcare_articles, 
                           book_items=book_items, 
                           reviews=reviews)

def get_mental_book_items():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM MentalHealthBooks')
    book_items = cursor.fetchall()
    cursor.close()
    return book_items

def get_mental_reviews():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM mental_health_reviews')
    reviews = cursor.fetchall()
    cursor.close()
    return reviews


# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         message = request.form['message']

#         if not name or not email or not message:
#             flash('Please fill out all fields', 'error')
#         else:
#             cursor = conn.cursor()
#             cursor.execute(
#                 'INSERT INTO contact_requests (name, email, message) VALUES (%s, %s, %s)',
#                 (name, email, message)
#             )
#             conn.commit()
#             cursor.close()
#             conn.close()
#             flash('Your message has been sent successfully!', 'success')
#             return redirect(url_for('contact'))

#     return render_template('/templates/index.html')









@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and user['password'] == password:
            print("logged in success")
            flash('Login successful', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
        
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, password))
        conn.commit()
        cursor.close()
        
        flash('Sign up successful', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/fitness')
def fitness():
    return render_template('fitness.html')

@app.route('/store')
def store():
    return render_template('store.html')
@app.route('/privacyPolicy')
def privacy_policy():
    return render_template('privacyPolicy.html')

@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')



@app.route('/logout')
@login_required
def logout():
    session.clear()
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()