import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

def get_db_connection():
    conn = psycopg2.connect(
        host = "localhost",
        database = "projectv1",
        user = "postgres",
        password = "postgres"
    )
    return conn
    
@app.route('/', methods = ['GET'])
def take():
    return render_template("login.html")

@app.route('/<userName>', methods = ['GET'])
def homepage(userName):
    return render_template("home.html", userName = userName)

@app.route('/home', methods = ['POST'])
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT userName FROM users WHERE userName = {} AND password = {};" .format('$$' + request.form["Username"] + '$$', '$$' + request.form["Password"] + '$$'))
    out = cur.fetchall()
    if(len(out) == 0):
        return redirect('/')
    return redirect('/' + str(request.form["Username"]))

@app.route('/<userName>/<quizId>', methods = ['GET'])
def quiz(userName, quizId):
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if Quiz is already attempted or user has access
    cur.execute("SELECT quizMarks FROM userQuizStats WHERE quizId = {} AND userId = (SELECT userId FROM users WHERE userName = {})" .format(quizId, '$$' + userName + '$$'))
    l = cur.fetchall()
    if(len(l) == 0):
        return redirect('/' + userName)

    if(l[0][0] != None):
        return redirect('/' + str(userName) + '/' + str(quizId) + '/results')

    # Render Quiz
    cur.execute("SELECT * FROM questions WHERE questionId IN (SELECT questionId FROM quizzes WHERE quizId = {});" .format(quizId))
    questions = cur.fetchall()
    return render_template("questions.html", questions = questions, quizId = quizId)

@app.route('/<userName>/questions', methods = ['POST'])
def questions(userName):
    conn = get_db_connection()
    cur = conn.cursor()

    # Finding UserId
    cur.execute("SELECT userId FROM users WHERE userName = {};" .format('$$' + str(userName) + '$$'))
    userId = cur.fetchall()[0][0]

    # Selecting 10 Random Questions
    cur.execute("SELECT * FROM questions, categories WHERE questions.categoryId = categories.categoryId and categories.categoryName = 'HISTORY' ORDER BY RANDOM() limit 10;")
    questions = cur.fetchall()

    # Selecting QuizId
    cur.execute("SELECT max(quizId) FROM userQuizStats")
    quizId = cur.fetchall()[0][0] + 1

    # Updating userQuizStats
    cur.execute("INSERT INTO userQuizStats (quizId,userId,quizMarks) VALUES ({}, {}, NULL);" .format(quizId, userId))

    # Updating Quizzes
    for question in questions:
        cur.execute("INSERT INTO quizzes (quizId,questionId,chosenOption,correctOption) VALUES ({}, {}, NULL, {});" .format(quizId, question[0], '$$' + str(question[3]) + '$$'))
    
    conn.commit()
    return redirect('/' + str(userName) + '/' + str(quizId))

@app.route('/<userName>/<quizId>/results', methods = ['GET'])
def display_results(userName, quizId):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT quizMarks FROM userQuizStats WHERE quizId = {} AND userId = (SELECT userId FROM users WHERE userName = {})" .format(quizId, '$$' + userName + '$$'))
    marks = cur.fetchall()

    # Check if user has access/ User has completed attempt
    if(len(marks) == 0):
        return redirect('/' + userName)

    if(marks[0][0] == None):
        return redirect('/' + str(userName) + '/' + str(quizId))

    # Render results
    cur.execute("SELECT question, chosenOption, correctOption FROM questions, quizzes WHERE questions.questionId = quizzes.questionId AND questions.questionId IN (SELECT questionId FROM quizzes WHERE quizId = {}) AND quizzes.quizId = {};" .format(quizId, quizId))
    questions = cur.fetchall()
    return render_template("results.html", questions = questions, quizMarks = marks[0][0])

@app.route('/<quizId>/results', methods = ['POST'])
def results(quizId):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT userName FROM users WHERE userId = (SELECT userId FROM userQuizStats WHERE quizId = {});" .format(quizId))
    userName = cur.fetchall()[0][0]

    # Select the required Quiz
    cur.execute("SELECT * FROM quizzes WHERE quizId = {};" .format(quizId))
    rows = cur.fetchall()

    # Update Answers
    for row in rows:
        if(str(row[1]) not in request.form):
            cur.execute("UPDATE quizzes SET chosenOption = 'NONE' WHERE quizId = {} AND questionId = {};" .format(row[1], quizId, row[1]))
        elif(request.form[str(row[1])] == "option1"):
            cur.execute("UPDATE quizzes SET chosenOption = (SELECT option1 FROM questions WHERE questionId = {}) WHERE quizId = {} AND questionId = {};" .format(row[1], quizId, row[1]))
        elif(request.form[str(row[1])] == "option2"):
            cur.execute("UPDATE quizzes SET chosenOption = (SELECT option2 FROM questions WHERE questionId = {}) WHERE quizId = {} AND questionId = {};" .format(row[1], quizId, row[1]))
        elif(request.form[str(row[1])] == "option3"):
            cur.execute("UPDATE quizzes SET chosenOption = (SELECT option3 FROM questions WHERE questionId = {}) WHERE quizId = {} AND questionId = {};" .format(row[1], quizId, row[1]))
        elif(request.form[str(row[1])] == "option4"):
            cur.execute("UPDATE quizzes SET chosenOption = (SELECT option4 FROM questions WHERE questionId = {}) WHERE quizId = {} AND questionId = {};" .format(row[1], quizId, row[1]))

    # Update Quiz Marks
    cur.execute("UPDATE userQuizStats SET quizMarks = (SELECT count(*) FROM quizzes WHERE quizId = {} AND chosenOption = correctOption) WHERE quizId = {};" .format(quizId, quizId))
    conn.commit()

    return redirect('/' + str(userName) + '/' + str(quizId) + '/results')