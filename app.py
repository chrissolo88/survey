from flask import Flask, request, render_template, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)

app.config['SECRET_KEY'] = 'surveys1234'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

@app.route('/')
def start_page():
    return render_template('start.html', surveys=surveys)

@app.route('/title', methods=["POST"])
def title_page():
    survey_key = request.form['survey']
    session['survey_key'] = survey_key
    title = surveys[survey_key].title
    instructions = surveys[survey_key].instructions
    return render_template('title.html', title=title, instructions=instructions)

@app.route("/new")
def new_responses():
    
    #initalize session['responses'] and set survey_key from session for selcted survey
    session['responses'] = []
    survey_key = session['survey_key']
    
    #Check if survey has been finished before in this browser,
    #if True redirect to /end with flash message alerting user
    if session.get('finished'):
        if survey_key in session['finished']:
            flash(f"Looks like you already completed {surveys[survey_key].title}")
            return redirect('/end')
        
    #Check if session['started'] exists, if False create session['started'] as empty dict
    if session.get('started') == None:
        session['started'] = {}
    
    started = session['started']
    
    #Check if selected survey has not been started before,
    #if True create dict pair in session['started'] with survey_key and session['responses']
    #redirect to question 0
    #if False store previous answers in response and then save responses to session['responses']
    #redirect to question based on the length of responses
    if survey_key not in started:
        started[survey_key] = session['responses']
        session['started'] = started
        return redirect("/question/0")
    else:
        responses = started[survey_key]
        session['responses'] = responses
        return redirect(f'/question/{len(responses)}')

@app.route('/question/<int:number>')
def question_display(number):
    session['qnumber'] = number
    qnumber = session['qnumber']
    survey_key = session.get('survey_key')
    responses = session.get('responses')
    response = ''
    if len(surveys[survey_key].questions) == len(responses):
        return redirect('/end')
    elif qnumber <= len(responses) and qnumber >= 0:
        question = surveys[survey_key].questions[qnumber].question
        choices = surveys[survey_key].questions[qnumber].choices
        allow_text = surveys[survey_key].questions[qnumber].allow_text
        if qnumber < len(responses):
            response = responses[qnumber]
        number = len(surveys[survey_key].questions)
        return render_template('question.html',question=question,number=number,choices=choices, allow_text=allow_text, response=response)
    else:
        flash(f"Invalid question, redirecting to '/question/{len(responses)}'")
        return redirect(f'/question/{len(responses)}')

@app.route('/answer',methods=["POST"])
def record_answer():
    survey_key = session['survey_key']
    responses = session['responses']
    started = session['started']
    qnumber = session['qnumber']
    response = [request.form['answer'],request.form.get('comment')] if request.form.get('comment') else request.form['answer']
    if qnumber == len(responses):
        responses.append(response)
    else:
        responses[qnumber] = response
    started[survey_key] = responses 
    session['responses'] = responses
    session['started'] = started
    print('**********')
    print(f'started{started}')
    print(f"finished{session.get('finished')}")
    print('**********')
    if len(surveys[survey_key].questions) > len(responses):
        return redirect(f'/question/{qnumber+1}')
    else:
        return redirect('/end')
    
@app.route('/end')
def thanks_page():
    survey_key = session['survey_key']
    responses = session['responses']
    questions = surveys[survey_key].questions
    
    if session.get('finished') == None:
        session['finished'] = {}
        
    finished = session['finished']
    
    if survey_key in finished:
        responses = finished[survey_key]
            
    if survey_key not in finished:
        finished[survey_key] = responses
        session['finished'] = finished
        started = session['started']
        del started[survey_key]
        session['started'] = started
    num = len(responses)
    print('**********')
    print(f'started{session["started"]}')
    print(f"finished{session.get('finished')}")
    print('**********')
    return render_template('end.html', num=num, responses=responses, questions=questions)

@app.route('/back', methods=["POST"])
def back_page():
    qnumber = session['qnumber']
    return redirect(f'/question/{qnumber-1}')
