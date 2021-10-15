import logging
import sqlite3
from logging.config import dictConfig

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, Response
from werkzeug.exceptions import abort

totalConnections = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global totalConnections
    app.logger.debug("Getting the connection for database")
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    totalConnections += 1 # this will increment in the total connections
    return connection

# Function to get a post using its ID
def get_post(post_id):
    app.logger.debug("Getting the Post from the database of ID "+ str(post_id))
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


# Define the main route of the web application 
@app.route('/')
def index():
    app.logger.info("Index page requested")
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    app.logger.info("Post requested of ID " + str(post_id))
    post = get_post(post_id)
    if post is None:
        app.logger.warn("Could not found the post with ID " + str(post_id))
        return render_template('404.html'), 404
    else:
        app.logger.info("Returning the post Title=" + post['title'] +", Content="+ post['content'])
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("About page requested")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    app.logger.info("POST create page requested")
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            app.logger.info("Inserting the new post Title=" + title +", Content="+ content)
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


# Health Check Endpoint for the application
@app.route('/healthz')
def healthz():
    app.logger.info("Health endpoint requested")
    connection = get_db_connection()
    app.logger.debug("going to perform DB check")
    DBCheck = connection.execute('SELECT 1 as dbcheck').fetchone()
    app.logger.debug("DBCheck received" + str(DBCheck['dbcheck']))
    connection.close()
    if DBCheck['dbcheck'] == 1:
        app.logger.debug("Everything seems fine. nothing to worry about")
        return jsonify(
            status="healthy",
            message="everything is working as expected"
        ) , 200, {'ContentType':'application/json'}
    else:
        app.logger.error("DB seems to be not responding. Need to check immediately")
        return jsonify(
            status="unhealthy",
            message="getting error while quering the database"
        ) , 500, {'ContentType':'application/json'}

# Health Check Endpoint for the application
@app.route('/metrics')
def metrics():
    global totalConnections
    app.logger.info("Metrics endpoint requested")
    connection = get_db_connection()
    postsCount = connection.execute('SELECT COUNT(*) as total FROM posts').fetchone()
    app.logger.debug("Total number of posts in the databse are " + str(postsCount))
    connection.close()
    return jsonify(
        db_connection_count=totalConnections,
        post_count=postsCount['total']
    ), 200, {'ContentType': 'application/json'}


# start the application on port 3111
if __name__ == "__main__":
    app.logger.info("Starting the HTTP server")
    app.run(host='0.0.0.0', port='3111')
