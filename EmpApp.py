from crypt import methods
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
import datetime

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("Home.html")

@app.route("/addnewemp", methods=['GET','POST'])
def diradd():
    return render_template("AddNewEmp.html")

@app.route("/editemp", methods=['GET','POST'])
def diredit():
    return render_template("EditEmp.html")

@app.route("/editdetails", methods=['GET','POST'])
def empedit():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    contact_no = request.form['contact_no']
    email = request.form['email']
    position = request.form['position']
    hiredate = request.form['hiredate']
    salary = request.form['salary']
    
    update_sql = "UPDATE employee SET first_name = %s, last_name = %s, contact_no = %s, email = %s, position = %s, hiredate = %s, salary = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()
    
    changefield = (first_name, last_name, contact_no, email, position, hiredate, salary, emp_id)
    cursor.execute(update_sql, (changefield))
    db_conn.commit()
    cursor.close()
    return render_template("EditOut.html")

@app.route("/getemp", methods=['GET','POST'])
def dirget():
    return render_template("GetEmpData.html")

@app.route("/empatt", methods=['GET','POST'])
def diratt():
    return render_template("EmpAtt.html")

@app.route("/payroll", methods=['GET','POST'])
def dirupdate():
    return render_template('Payroll.html')

@app.route("/payupdate", methods=['GET','POST'])
def dirpay():
    emp_id = request.form['emp_id']
    salary = request.form['salary']

    updatesql = "UPDATE employee SET salary= %s WHERE emp_id = %s"
    mycursor = db_conn.cursor()
    changefield = (salary, emp_id)
    mycursor.execute(updatesql, (changefield))
    db_conn.commit()
    mycursor.close()
    return render_template("PayOut.html")

@app.route("/delemp", methods=['GET','POST'])
def dirdel():
    return render_template("DelEmp.html")

@app.route("/empattend", methods=['POST'])
def EmpAtt():
    

    emp_id = request.form['emp_id']
    attstatus = request.form['attstatus']

    insert_sql = "INSERT INTO attendance VALUES (%s, %s)"
    cursor = db_conn.cursor()
    
    
    try:

        cursor.execute(insert_sql, (emp_id, attstatus))
        db_conn.commit()
        status = "Employee " + emp_id + " has checked in at the date 10 April 2020." 

    except Exception as e:
            return str(e)

    finally:
        cursor.close()

    return render_template('EmpAttOut.html', status=status)


@app.route("/fetchdata", methods=['GET','POST'])
def GetEmpData():
    emp_id = request.form['emp_id']
    mycursor = db_conn.cursor()
    getempdata = "select * from employee WHERE emp_id = %s"
    mycursor.execute(getempdata,(emp_id))
    result = mycursor.fetchall()
    (emp_id,first_name,last_name,contact_no,email,position,hiredate,salary) = result[0]   

    return render_template('GetEmpDataOut.html', emp_id=emp_id,first_name=first_name,last_name=last_name,contact_no=contact_no,email=email,position=position,hiredate=hiredate,salary=salary)


@app.route("/delempsuc", methods=['GET','POST'])
def DeleteEmp():

    return render_template('DelEmpOut.html')

@app.route("/addemp", methods=['GET','POST'])
def AddNewEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    contact_no = request.form['contact_no']
    email = request.form['email']
    position = request.form['position']
    hiredate = request.form['hiredate']
    salary = request.form['salary']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, contact_no, email, position, hiredate, salary))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddNewEmpOut.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

