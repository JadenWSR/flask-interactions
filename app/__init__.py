# to run this website and watch for changes: 
# $ set FLASK_ENV=development; flask run


from flask import Flask, g, render_template, request

import numpy as np
import pandas as pd
import pickle
import sqlite3

import io
import base64

app = Flask(__name__)

def get_message_db():
    # Check whether there is a database called message_db in the g attribute of the app
    if 'message_db' not in g:
        #  If not, then connect to that database, ensuring that the connection is an attribute of g
        g.message_db = sqlite3.connect("messages_db.sqlite")

    if g.message_db is not None:
        cursor = g.message_db.cursor()
        # Check whether a table called messages exists in message_db, and create it if not
        sql_create_messages_table = """ CREATE TABLE IF NOT EXISTS messages (
                                    id integer,
                                    handle text,
                                    messages text
                                ); """
        cursor.execute(sql_create_messages_table)
    # Return the connection
    return g.message_db


def insert_message(request):
    # open the connection
    g.message_db = get_message_db()
    cursor = g.message_db.cursor()
    # Extract message and handle
    message = request.form["message"]
    handle = request.form["handle"]
    
    # get nrow and assign unique id
    n_row = cursor.execute('select * from messages;')
    nrow = len(n_row.fetchall()) + 1
    
    # add a new row to messages database
    cursor.execute("INSERT INTO messages (id, handle, messages) VALUES ({nrow}, '{handle}', '{message}')".format(
         nrow = nrow, handle = handle, message = message))
    # Save the change
    g.message_db.commit()
    # close the connection
    g.message_db.close()


def random_messages(n):
    # open the connection
    g.message_db = get_message_db()
    # Get a collection of n random messages from the message_db, or fewer if necessary
    messages = pd.read_sql_query("SELECT * FROM messages WHERE id IN (SELECT id FROM messages ORDER BY RANDOM() LIMIT {n})".format(n = n), g.message_db)
    # close the connection
    g.message_db.close()
    return messages


# Create main page
@app.route('/')
def main():
    return render_template("main.html")

@app.route('/submit/', methods=['POST', 'GET'])
def submit():
    if request.method == 'GET':
        return render_template('submit.html')
    else: # if request.method == 'POST'
        try:
            insert_message(request)
            return render_template('submit.html', thanks = True)
        except:
            return render_template('submit.html')


@app.route('/view/')
def view():
    try:
        messages = random_messages(5)
        return render_template('view.html', messages = messages)
    except:
        return render_template('view.html', error = True)

