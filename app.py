import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from datetime import datetime
import json
import plotly.graph_objects as go


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
    patient_count_by_day = {}

    # Lặp qua từng item trong "patient/noitru"
    for patient_data in db.child("patient").child("noitru").get().each():
        date_in = patient_data.val().get("date_in", "")

        # Chuyển đổi date_in thành datetime object
        if date_in:
            date_in_obj = datetime.strptime(date_in, "%Y-%m-%d")

            # Cập nhật số lượng bệnh nhân đi vào mỗi ngày
            day_str = date_in_obj.strftime("%Y-%m-%d")
            patient_count_by_day[day_str] = patient_count_by_day.get(day_str, 0) + 1

    # Chuyển dictionary thành list và sắp xếp theo thời gian
    patient_count_list = sorted(patient_count_by_day.items(), key=lambda x: x[0])

    # Extracting x and y values from the patient_count_list
    x_values = [item[0] for item in patient_count_list]
    y_values = [item[1] for item in patient_count_list]

    fig = go.Figure([go.Bar(x=x_values, y=y_values)])
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)
    return render_template('dashboard.html', plot_div=plot_div)
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
        rows2 = db.child("medicine").child("med_tool").get()

        
        data1 = db.child("medicine").child("med_drink").get().val() 
        data2 = db.child("medicine").child("med_tool").get().val()  

        total1 = 0
        if data1 is not None:  # Check if data exists
            for item in data1.values():
                total1 += int(item["num"])

        total2 = 0
        if data2 is not None:  # Check if data exists
            for item in data2.values():
                total2 += int(item["num"])

        return render_template("medicine_drink.html", rows=rows, rows2=rows2, num1=total1, num2 = total2)
    else:
        return redirect(url_for('welcome'))

#Dung cu route
@app.route("/med/med_tool")
def medicine_tool():
    if person["is_logged_in"] == True:
        rows = db.child("medicine").child("med_tool").get()
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
        cackhoa = db.child("Khoa").get()
        return render_template("patient_input.html", cackhoa=cackhoa)
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
        date_birth = result["date_birth"]
        phone_number = result["phone_number"]
        khoa = result["khoa"]
        date_in = result["date_in"]
        chandoan = result["chandoan"]
        giuong = result["giuong"]

        data = {"name": name, "age": age,
                "date_birth": date_birth, "phone_number": phone_number,
                "khoa": khoa, "date_in": date_in, "chandoan": chandoan,
                "giuong": giuong}
        
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
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#BỆNH NHÂN NỘI TRÚ
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#THông tin chi tiết về bệnh nhân nội trú
@app.route("/noitru/<string:id>")
def route_handler_noi(id):
  # Lấy dữ liệu dựa trên id
    item = db.child('patient').child('noitru').child(id).get()
    rows = db.child("patient").child("noitru").child(id).child("xetnghiem").get()
    rows2 = db.child("patient").child("noitru").child(id).child("add_med").get()


    return render_template("patient_x_noitru.html", item=item, id=id, rows=rows, rows2=rows2)


#Trang hien ra benh nhan noi tru
@app.route("/patient/patient_noi")
def patient_noi():
    if person["is_logged_in"] == True:
        danhsach = db.child("patient").child("noitru").get()
        return render_template("patient_noi.html", danhsach=danhsach)
    else:
        return redirect(url_for('welcome'))
    


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#BỆNH NHÂN NGOẠI TRÚ
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#THông tin chi tiết về bệnh nhân ngoại trú
@app.route("/ngoaitru/<string:id>")
def route_handler_ngoai(id):
    # Lấy dữ liệu dựa trên id
    item = db.child('patient').child('ngoaitru').child(id).get()
    rows = db.child("patient").child("ngoaitru").child(id).child("xetnghiem").get()
    rows2 = db.child("patient").child("ngoaitru").child(id).child("add_med").get()

    return render_template("patient_x_ngoaitru.html", item=item, id=id, rows=rows, rows2=rows2)

@app.route("/patient/patient_ngoai")
def patient_ngoai():
    if person["is_logged_in"] == True:
        danhsach = db.child("patient").child("ngoaitru").get()
        return render_template("patient_ngoai.html", danhsach=danhsach)
    else:
        return redirect(url_for('welcome'))



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#XÉT NGHIỆM
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route("/xetnghiem/<string:id>")
def xet_nghiem(id):
  # Lấy dữ liệu dựa trên id
    if person["is_logged_in"] == True:
        
        return render_template("xetnghiem_input.html", id=id)
    else:
        return redirect(url_for('welcome'))


@app.route("/xetnghiem_logic/<string:id>", methods=["POST", "GET"])
def xet_nghiem_logic(id):
  # Lấy dữ liệu dựa trên id
    if request.method == "POST":
        result = request.form

        name = result["name"]
        date = result["date"]
        ketqua = result["ketqua"]
        patient = str(result["patient"]).strip()


        data = {"name": name, "date": date, "ketqua": ketqua}
        
        #Nếu đó là bệnh nhân nội trú
        if patient == "noitru":
            danhsach = db.child("patient").child("noitru").child(id).child("xetnghiem").push(data)

            return redirect(url_for("patient_noi"))
        #Nếu đó là bệnh nhân ngoại trú
        else:
            danhsach = db.child("patient").child("ngoaitru").child(id).child("xetnghiem").push(data)

            return redirect(url_for("patient_ngoai")) 
    else:
        return redirect(url_for('welcome'))
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#THÊM THUỐC
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@app.route("/add_med/<string:id>")
def add_med(id):
  # Lấy dữ liệu dựa trên id
    if person["is_logged_in"] == True:

        return render_template("patient_med_in.html", id=id)
    else:
        return redirect(url_for('welcome'))
    

@app.route("/patient_med_logic/<string:id>", methods=["POST", "GET"])
def patient_med_logic(id):
  # Lấy dữ liệu dựa trên id
    if request.method == "POST":
        result = request.form

        name = result["name"]
        soluong = result["soluong"]
        patient = str(result["patient"]).strip()


        data = {"name": name, "soluong": soluong}
        
        #Nếu đó là bệnh nhân nội trú
        if patient == "noitru":
            db.child("patient").child("noitru").child(id).child("add_med").push(data)

            return redirect(url_for("patient_noi"))
        #Nếu đó là bệnh nhân ngoại trú
        else:
            db.child("patient").child("ngoaitru").child(id).child("add_med").push(data)

            return redirect(url_for("patient_ngoai")) 
    else:
        return redirect(url_for('welcome'))
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++




#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#XỬ LÍ LIÊN QUAN ĐẾN TÀI CHÍNH

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#LIÊN QUAN ĐẾN INCOME
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route("/fiancial/income_input")
def income_input():
    if person["is_logged_in"] == True:
        return render_template("fiancial_income_input.html")
    else:
        return redirect(url_for("welcome"))

@app.route("/fiancial/income")
def fiancial_income():
    if person["is_logged_in"] == True:
        danhsach = db.child("fiancial").child("income").get()

        date_time_now = datetime.datetime.now()

        year = str(date_time_now.year)
        last_year = str(date_time_now.year-1)

        month = str(date_time_now.month)
        last_month = str(date_time_now.month-1)

        day = str(date_time_now.day)
        yesterday = str(date_time_now.day-1)

        ngay = db.child("fiancial").child("income").child(year).child(month).child(day).get().val()
        ngaytruoc = db.child("fiancial").child("income").child(year).child(month).child(yesterday).get().val()

        thang = db.child("fiancial").child("income").child(year).child(month).get().val()
        thangtruoc = db.child("fiancial").child("income").child(year).child(last_month).get().val()

        nam = db.child("fiancial").child("income").child(year).get().val()
        namtruoc = db.child("fiancial").child("income").child(last_year).get().val()
        # Chuyển đổi JSON thành từ điển

        total = [0,0, 0,0, 0,0]
        percent = []

        

        if ngay is not None:  # Check if data exists
            for item in ngay.values():
                total[0] += int(item["price"])
        if ngaytruoc is not None:  # Check if data exists
            for item in ngaytruoc.values():
                total[1] += int(item["price"])
        # Tính tổng giá trị của tháng hiện tại
        if thang is not None:  # Kiểm tra xem có dữ liệu tháng hiện tại không
            for day_data in thang.values():
                for item in day_data.values():
                    total[2] += int(item["price"])

        # Tính tổng giá trị của tháng trước đó
        if thangtruoc is not None:  # Kiểm tra xem có dữ liệu tháng trước đó không
            for day_data in thangtruoc.values():
                for item in day_data.values():
                    total[3] += int(item["price"])

        # Tính tổng giá trị của năm hiện tại
        if nam is not None:  # Kiểm tra xem có dữ liệu năm hiện tại không
            for month_data in nam.values():
                for day_data in month_data.values():
                    for item in day_data.values():
                        total[4] += int(item["price"])

        # Tính tổng giá trị của năm trước đó
        if namtruoc is not None:  # Kiểm tra xem có dữ liệu năm trước đó không
            for month_data in namtruoc.values():
                for day_data in month_data.values():
                    for item in day_data.values():
                        total[5] += int(item["price"])


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

        temp = round( ((total[0]-total[1])/total[1]*100), 2)
        percent.append(temp)
        temp = round( ((total[2]-total[3])/total[3]*100), 2)
        percent.append(temp)
        temp = round( ((total[4]-total[5])/total[5]*100), 2)
        percent.append(temp)

        
        return render_template("fiancial_income.html", rows=rows, total=total, percent=percent)
    else:
        return redirect(url_for('welcome'))
    
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
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#LIÊN QUAN ĐẾN EXPENSE
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route("/fiancial/expense_input")
def expense_input():
    if person["is_logged_in"] == True:
        return render_template("fiancial_expense_input.html")
    else:
        return redirect(url_for("welcome"))
    

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
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


if __name__ == "__main__":
    app.run()   