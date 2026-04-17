from flask import Flask,render_template,request,redirect,jsonify,session
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

users = []   # [{id, name, email, password}]
blogs = []   # [{id, user_id, content}]
votes = []   # [{user_id, blog_id, vote_type}]

###### HOME ######

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')  
    # Create a new list to hold formatted blog data for the HTML
    display_blogs = []
    for b in blogs:
        # 1. Find the author's name
        author_name = "Unknown"
        for u in users:
            if u['id'] == b['user_id']:
                author_name = u['name']
                break      
        # 2. Count the votes for this specific blog
        upvotes = 0
        downvotes = 0
        for v in votes:
            if v['blog_id'] == b['id']:
                if v['vote_type'] == 'up':
                    upvotes += 1
                elif v['vote_type'] == 'down':
                    downvotes += 1             
        # 3. Add all this data together for the HTML
        display_blogs.append({
            'id': b['id'],
            'author': author_name,
            'content': b['content'],
            'upvotes': upvotes,
            'downvotes': downvotes
        })
    # Send the new display_blogs list instead of the raw blogs list
    return render_template("blogging.html", blogs=display_blogs)

###### SIGNUP ######

@app.route('/signup', methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        # check duplicate user
        for user in users:
            if user['email'] == email:
                return "User already exists!"
        user_id = len(users) + 1
        users.append({
            "id": user_id,
            "name": name,
            "email": email,
            "password": password
        })
        return redirect('/login')
    
###### LOGIN ######

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        for user in users:
            if user['email'] == email and user['password'] == password:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                return redirect('/')
        return "Invalid credentials"
    
##### LOGOUT ######

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')    

###### CREATE BLOG ######

@app.route('/create', methods=["GET","POST"])
def create():
    if request.method == "GET":
        return render_template("create.html")
    elif request.method == "POST":
        content = request.form.get("content")
        blog_id = len(blogs) + 1
        blogs.append({
            "id": blog_id,
            "user_id": session['user_id'],
            "content": content
        })
        return redirect('/')
    
###### VOTE ######

@app.route('/vote/<int:blog_id>/<vote_type>')
def vote(blog_id, vote_type):
    user_id = session['user_id']
    # find blog
    blog = None
    for b in blogs:
        if b['id'] == blog_id:
            blog = b
            break
    # prevent self vote
    if blog and blog['user_id'] == user_id:
        return "You cannot vote your own blog"
    # check existing vote
    for v in votes:
        if v['user_id'] == user_id and v['blog_id'] == blog_id:
            v['vote_type'] = vote_type
            return redirect('/')
    # add vote
    votes.append({
        "user_id": user_id,
        "blog_id": blog_id,
        "vote_type": vote_type
    })
    return redirect('/')

##### MAIN FUNCTION #####

if __name__ == "__main__":
    app.run(debug=True)