import wolframalpha
from flask import Flask,session,render_template,request,redirect,jsonify
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import os

app=Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
bcrypt = Bcrypt(app)

client=MongoClient('mongodb://localhost:27017/')
db=client['HackathonChatBot']
users=db['users']
chat=db['chat_messages']

client= wolframalpha.Client('6WAEP9-R9GHYET35U')

@app.route('/',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = db.users.find_one({'username':username})
        if existing_user and bcrypt.check_password_hash(existing_user['password'],password):
            session['user_id'] = str(existing_user['_id'])
            return redirect('/bot-new')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = {'username':username, 'password':hashed_password}
            db.users.insert_one(user)
            session['user_id'] = str(user['_id'])
            return redirect('/bot-new')
    else:
        return render_template("register.html")

@app.route('/bot-new',methods=['GET','POST'])
def bot_history():
    if 'user_id' in session:
        user_id = session['user_id']
        chat_history = list(db.chat.find({'user_id':user_id}))
        #print(chat_history)
        return render_template("bot-new.html", chat_history=chat_history)
    else:
        return "User ID not found or not in session"
    
@app.route('/store_message',methods=['POST'])
def store_message():
    user_id = session['user_id']
    query = request.form['dbt']
    res = client.query(query)
    output = next(res.results).text
    db.chat.insert_one({'user_id':user_id,'Query':query,'Output':output})
    return redirect('/bot-new')

@app.route('/api/get-chat-messages')
def get_chat_messages():
    user_id = session['user_id']
    chat_history = list(db.chat.find({'user_id': user_id}))
    #print(chat_history)
    return jsonify(success=True, messages=chat_history)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)





