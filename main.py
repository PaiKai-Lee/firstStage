from flask import Flask,request,render_template,redirect,session,url_for,jsonify
import mysql.connector
import json

app=Flask(__name__)
app.secret_key=b'8$"\xf9.o\xa0e0Yg\xd7\xdd\xdb\xfc\xaf'

mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="abcd1234",
    database="website"
)
mycursor=mydb.cursor()
apiUsers={}
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("member"))
    else:
        return render_template("index.html")

@app.route("/signin", methods=["POST"])
def signin():
    user=request.form["user"]
    password=request.form["password"]
    
    mycursor.execute("SELECT username,password,name FROM user WHERE username=%s and password=%s",(user,password)) #在資料庫中選擇與輸入相同的帳密
    DBinf=mycursor.fetchone()
    if DBinf != None:      #判斷帳號密碼是否存在資料庫
            session["username"]=user
            session["name"]=DBinf[2]
            session.permanent= True
            return redirect(url_for("member"))
    return redirect(url_for("error",Message="帳號或密碼輸入錯誤"))

@app.route("/signup",methods=["POST"])
def signup():
    name=request.form["name"]
    user=request.form["user"]
    password=request.form["password"]
    valid=request.form["validation"]

    if name=="" or user=="" or password=="":    #註冊資料不可空白
        return redirect(url_for("error",Message="資料不可空白"))
    elif valid != password:                     #密碼驗證
        return redirect(url_for("error",Message="密碼驗證錯誤"))
    mycursor.execute("SELECT username FROM user where username = %s",(user,))#在資料庫中選擇與輸入相同的username
    DBuser=mycursor.fetchone()     
    if DBuser != None:   #判斷帳號是否重複(是否存在資料庫)
        return redirect(url_for("error",Message="帳號已被註冊"))

    sql=("INSERT INTO user(name,username,password) VALUES (%s,%s,%s)") #輸入SQL語法
    val=(name,user,password)
    mycursor.execute(sql,val)   #執行SQL語法
    mydb.commit()               #更改資料記得要commit
    return redirect(url_for("index"))

@app.route("/signout")
def signout():
    session.pop("username",None)
    session.pop("name",None)
    return redirect(url_for("index"))

@app.route("/member/")
def member():
    user=session["name"]
    return render_template("member.html",user=user)

@app.route("/error/")
def error():
    if "username" in session:
        return redirect(url_for("member"))
    Message=request.args.get("Message")
    return render_template("error.html",errorMessage=Message)

#user資料API
@app.route("/api/users/")
def api():
    val=request.args.get("username")
    mycursor.execute("SELECT id,name,username From user where username=%s",(val,))
    DBuser=mycursor.fetchone()
    if DBuser==None:
        apiUsers["data"]=DBuser
        return jsonify(apiUsers)
    userID=DBuser[0]
    name=DBuser[1]
    userName=DBuser[2]
    apiUsers["data"]={"id":userID,"name":name,"username":userName}
    return jsonify(apiUsers)

if __name__=="__main__":
    app.run(port=3000)