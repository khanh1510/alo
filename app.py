import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import datetime
import json

app = Flask(__name__)

#Key FireBase detail
config = {
    'apiKey': "AIzaSyBFNw4UVBT8vHWNvh-JmTnk04YZuNGpTjE",
    'authDomain': "authentical-34a24.firebaseapp.com",
    'projectId': "authentical-34a24",
    'storageBucket': "authentical-34a24.appspot.com",
    'messagingSenderId': "911914926881",
    'appId': "1:911914926881:web:74c81134ba21c3b3e6b460",
    'measurementId': "G-NSHQRDWQTN",
    'databaseURL': "https://authentical-34a24-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()  
db = firebase.database()


person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}
#End setup website

#Login
#/////////////////////////////////////////////////////
@app.route("/")
def login():
    if person["is_logged_in"] == True:
        return redirect(url_for('welcome'))
    else:
        return render_template("sign-in.html")
#/////////////////////////////////////////////////////
    

#/////////////////////////////////////////////////////

#Home page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("index.html")
    else:
        return redirect(url_for('login'))
#/////////////////////////////////////////////////////






#XỬ LÍ ĐĂNG NHẬP ĐĂNG XUẤT
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#Sign up - Register
@app.route("/signup")
def signup():
    if person["is_logged_in"] == True:
        return redirect(url_for('welcome'))
    else:
        return render_template("sign-up.html")

#Log out - redirect to login page
@app.route("/logout", methods=["POST", "GET"])
def logout():
    global person
    person["is_logged_in"] = False
    person["uid"] = ""
    person["email"] = ""
    person["name"] = ""
    return redirect(url_for('welcome'))


#Xu li viec dang nhap co thanh cong hay khong
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        try:

            user = auth.sign_in_with_email_and_password(email, password)

            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]

            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]

            #set user session 
            #session['user'] = person["email"]

            return redirect(url_for('welcome'))
        except:

            return redirect(url_for('login'))
    else:
        if person['is_logged_in'] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))
        
#Xu li logic viec register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        name = result["name"]

        try:
            auth.create_user_with_email_and_password(email, password)

            user = auth.sign_in_with_email_and_password(email, password)

            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["name"] = name
            person["uid"] = user["localId"]

            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)

            #request.cookies.pop()
            return redirect(url_for('welcome'))
        except:
            return redirect(url_for('register'))
    else:
        return redirect(url_for('welcome'))



@app.after_request
def add_nocache_headers(response):
  response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Expires'] = '0'
  return response
#/////////////////////////////////////////////////////






#/////////////////////////////////////////////////////
#Dashboard
@app.route("/dashboard")
def dashboard():
    if person["is_logged_in"] == True:
        return render_template("dashboard.html")
    else:
        return redirect(url_for('welcome'))
#/////////////////////////////////////////////////////





#XỬ LÍ LIÊN QUAN ĐẾN BÁC SĨ
#/////////////////////////////////////////////////////
#Xu li de in ra ket qua cua nhan vien y bac si
@app.route("/doctor")
def process_logic():
    if person["is_logged_in"] == True:
        source = request.args.get('source')
        if source == "a":
            nhan_vien = db.child("Khoa").child("Capcuu").get()
        if source == "b":
            nhan_vien = db.child("Khoa").child("Noi").get()
        if source == "c":
            nhan_vien = db.child("Khoa").child("Ngoai").get()
        if source == "d":
            nhan_vien = db.child("Khoa").child("Rang").get()
        if source == "e":
            nhan_vien = db.child("Khoa").child("Timmach").get()
        if source == "f":
            nhan_vien = db.child("Khoa").child("Mat").get()

        return render_template("doctor.html", nhan_vien=nhan_vien)
    else:
        return redirect(url_for('welcome'))
    
@app.route("/doctor_input")
def doctor_input():
    if person["is_logged_in"] == True:
        cackhoa = db.child("Khoa").get()
        return render_template("doctor_input.html", cackhoa=cackhoa)
    else:
        return redirect(url_for("welcome"))

@app.route("/doctor_input_logic", methods=['POST', 'GET'])
def doctor_input_logic():
    if request.method == "POST":
        result = request.form

        name = result["name"]
        gender = result["gender"]
        date_birth = result["date_birth"]
        phone_number = result["phone_number"]
        email = result["email"]
        khoa = str(result["khoa"]).strip()
        date_join = result["date_join"]


        data = {"name": name, "gender": gender,
                 "date_birth": date_birth, "phone_number": phone_number,
                   "email": email, "date_join": date_join}

        db.child("Khoa").child(khoa).push(data)

        # Render template với dữ liệu từ Firebase
        return redirect(url_for('doctor_input'))
    else:
        return redirect(url_for('welcome'))
#/////////////////////////////////////////////////////





#XỬ LÍ LIÊN QUAN ĐẾN THUỐC THANG
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
@app.route("/med/med_input")
def med_input():
    if person["is_logged_in"] == True:
        return render_template("medicine_input.html")
    else:
        return redirect(url_for('welcome'))


@app.route("/med_logic", methods=["POST", "GET"])
def med_logic_input():
    if request.method == "POST":
        result = request.form

        med = str(result["med"]).strip()
        name = result["name"]
        name_supply = result["name_supply"]
        num = result["num"]
        date = result["date"]

        data = {"name": name, "name_supply": name_supply, "num": num, "date": date}
        
        if med == "med_drink":
            db.child("medicine").child(med).push(data)
        else:
            db.child("medicine").child(med).push(data)

        return redirect(url_for("med_input"))
    else:
        return render_template("medicine_input.html")



#THuoc uong route
@app.route("/med/med_drink")
def medicine_drink():
    if person["is_logged_in"] == True:
        rows = db.child("medicine").child("med_drink").get()
        return render_template("medicine_drink.html", rows=rows)
    else:
        return redirect(url_for('welcome'))

#Dung cu route
@app.route("/med/med_tool")
def medicine_tool():
    if person["is_logged_in"] == True:
        rows = db.child("medicine").child("tool").get()
        return render_template("medicine_tool.html", rows=rows)
    else:
        return redirect(url_for('welcome'))
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\




#XỬ LÍ LIÊN QUAN ĐẾN BỆNH NHÂN
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#Dieu huong trang nhap du lieu benh nhan
@app.route("/patient/patient_input")
def patient_input():
    if person["is_logged_in"] == True:
        return render_template("patient_input.html")
    else:
        return redirect(url_for("welcome"))
    

#xử lí logic của khi nhấn input dữ liệu bệnh nhân
@app.route("/patient_logic", methods=["POST", "GET"])
def patient_logic_input():
    if request.method == "POST":
        result = request.form

        type_patient = result["patient"]
        name = result["name"]
        age = result["age"]
        date_in = result["date_in"]
        date_out = result["date_out"]

        data = {"name": name, "age": age, "date_in": date_in, "date_out": date_out}
        
        #Nếu đó là bệnh nhân nội trú
        if type_patient == "noitru":
            danhsach = db.child("patient").child("noitru").push(data)

            return redirect(url_for("patient_noi", danhsach=danhsach))
        #Nếu đó là bệnh nhân ngoại trú
        else:
            danhsach = db.child("patient").child("ngoaitru").push(data)

            return redirect(url_for("patient_ngoai", danhsach=danhsach))   
    else:
        return render_template("patient_input.html")

#THông tin chi tiết về bệnh nhân nội trú
@app.route("/noitru/<string:id>")
def route_handler_noi(id):
  # Lấy dữ liệu dựa trên id
  item = db.child('patient').child('noitru').child(id).get()

  return render_template("patient_x_noitru.html", item=item)

@app.route('/submit_prescription', methods=['POST'])
def submit_prescription():
    patient_name = request.form['patient_name']
    medications = request.form.getlist('medication[]')
    quantities = request.form.getlist('quantity[]')
    
    # Lưu dữ liệu vào Firebase
    prescriptions_ref = db.child("test")
    
    for medication, quantity in zip(medications, quantities):
        prescriptions_ref.push({    
            'patient_name': patient_name,
            'medication': medication,
            'quantity': quantity
        })
    
    return 'Đã lưu đơn thuốc thành công!'


#THông tin chi tiết về bệnh nhân ngoại trú
@app.route("/ngoaitru/<string:id>")
def route_handler_ngoai(id):
  # Lấy dữ liệu dựa trên id
  item = db.child('patient').child('ngoaitru').child(id).get()

  return render_template("patient_x_ngoaitru.html", item=item)


#Trang hien ra benh nhan noi tru
@app.route("/patient/patient_noi")
def patient_noi():
    if person["is_logged_in"] == True:
        danhsach = db.child("patient").child("noitru").get()
        return render_template("patient_noi.html", danhsach=danhsach)
    else:
        return redirect(url_for('welcome'))
    
#Trang hien ra benh nhan ngoai tru
@app.route("/patient/patient_ngoai")
def patient_ngoai():
    if person["is_logged_in"] == True:
        danhsach = db.child("patient").child("ngoaitru").get()
        return render_template("patient_ngoai.html", danhsach=danhsach)
    else:
        return redirect(url_for('welcome'))
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\




    

#XỬ LÍ LIÊN QUAN ĐẾN TÀI CHÍNH
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#Fiancial route
@app.route("/fiancial/expense")
def fiancial_expense():
    if person["is_logged_in"] == True:
        danhsach = db.child("fiancial").child("expense").get()
        # Chuyển đổi JSON thành từ điển

        # Trích xuất dữ liệu và biến thành danh sách các dòng
        # Trích xuất dữ liệu và biến thành danh sách các dòng
        rows = []
        for year in danhsach.each():
            year_data = year.val()
            for month in year_data:
                month_data = year_data[month]
                for day in month_data:
                    day_data = month_data[day]
                    for key, item in day_data.items():
                        rows.append({
                            'date': item['date'],
                            'name': item['name'],
                            'price': item['price']
                        })
        return render_template("fiancial_expense.html", rows=rows)
    else:
        return redirect(url_for('welcome'))
    
@app.route("/fiancial/income")
def fiancial_income():
    if person["is_logged_in"] == True:
        danhsach = db.child("fiancial").child("income").get()
        # Chuyển đổi JSON thành từ điển

        # Trích xuất dữ liệu và biến thành danh sách các dòng
        # Trích xuất dữ liệu và biến thành danh sách các dòng
        rows = []
        for year in danhsach.each():
            year_data = year.val()
            for month in year_data:
                month_data = year_data[month]
                for day in month_data:
                    day_data = month_data[day]
                    for key, item in day_data.items():
                        rows.append({
                            'date': item['date'],
                            'name': item['name'],
                            'price': item['price']
                        })
        return render_template("fiancial_income.html", rows=rows)
    else:
        return redirect(url_for('welcome'))
    
@app.route("/fiancial/expense_input")
def expense_input():
    if person["is_logged_in"] == True:
        return render_template("fiancial_expense_input.html")
    else:
        return redirect(url_for("welcome"))


@app.route("/fiancial/income_input")
def income_input():
    if person["is_logged_in"] == True:
        return render_template("fiancial_income_input.html")
    else:
        return redirect(url_for("welcome"))

#xử lí logic của khi nhấn input dữ liệu bệnh nhân
@app.route("/expense_logic", methods=["POST", "GET"])
def expense_logic_input():
    if request.method == "POST":
        result = request.form

        name = result["name"]
        date = result["date"]
        price = result["price"]

        date_time_now = datetime.datetime.now()

        # Lấy năm từ ngày và giờ hiện tại và chuyển thành string
        year = str(date_time_now.year)
        month = str(date_time_now.month)
        day = str(date_time_now.day)


        data = {"name": name, "date": date, "price": price}

        db.child("fiancial").child("expense").child(year).child(month).child(day).push(data)

        # Render template với dữ liệu từ Firebase
        return redirect(url_for('fiancial_expense'))
            
    else:
        return render_template("fiancial_expense.html")
    


#xử lí logic của khi nhấn input dữ liệu bệnh nhân
@app.route("/income_logic", methods=["POST", "GET"])
def income_logic_input():
    if request.method == "POST":
        result = request.form

        name = result["name"]
        date = result["date"]
        price = result["price"]

        date_time_now = datetime.datetime.now()

        # Lấy năm từ ngày và giờ hiện tại và chuyển thành string
        year = str(date_time_now.year)
        month = str(date_time_now.month)
        day = str(date_time_now.day)


        data = {"name": name, "date": date, "price": price}

        db.child("fiancial").child("income").child(year).child(month).child(day).push(data)

        # Render template với dữ liệu từ Firebase
        return redirect(url_for('fiancial_income'))
    else:
        return render_template("fiancial_income.html")
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\




if __name__ == "__main__":
    app.run()   