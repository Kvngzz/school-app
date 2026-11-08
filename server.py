from flask import Flask, render_template, request, redirect, url_for, flash
from mongodb import get_connection

from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)

app.secret_key = "change-this-to-a-random-secret"

# Connect to MongoDB
db = get_connection()

# Create students collection
students_collection = db["students"]

# Prevent duplicate email addresses
students_collection.create_index("email", unique=True)

# HOME ROUTE - DISPLAY ALL STUDENTS
@app.route("/")
def home():

    students = list(
        students_collection.find().sort("_id", -1)
    )

    return render_template("index.html", students=students)

# REGISTER STUDENT
@app.route("/register", methods=["POST"])
def register():

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    gender = request.form.get("gender", "")
    course = request.form.get("course", "")
    phone = request.form.get("phone", "").strip()
    occupation = request.form.get("occupation", "").strip()

    if not all([full_name, email, gender, course, phone]):

        flash("Please fill in every field.", "error")

        return redirect(url_for("home"))

    student = {
        "full_name": full_name,
        "email": email,
        "gender": gender,
        "course": course,
        "phone": phone,
        "occupation": occupation
    }

    try:

        students_collection.insert_one(student)

        flash("Student registered successfully!", "success")

    except DuplicateKeyError:

        flash("This email address is already registered.", "error")

    except Exception:

        app.logger.exception("Student registration failed")

        flash("Registration failed. Please try again.", "error")

    return redirect(url_for("home"))

# EDIT STUDENT
@app.route("/edit/<student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    if not ObjectId.is_valid(student_id):

        flash("Invalid student ID.", "error")

        return redirect(url_for("home"))

    student_object_id = ObjectId(student_id)

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        gender = request.form.get("gender", "")
        course = request.form.get("course", "")
        phone = request.form.get("phone", "").strip()
        occupation = request.form.get("occupation", "").strip()

        if not all([full_name, email, gender, course, phone, occupation]):

            flash("Please fill in every field.", "error")

            return redirect(url_for("edit_student", student_id=student_id))

        updated_student = {
            "full_name": full_name,
            "email": email,
            "gender": gender,
            "course": course,
            "phone": phone,
            "occupation": occupation
        }

        try:

            result = students_collection.update_one(
                {"_id": student_object_id},
                {"$set": updated_student}
            )

            if result.matched_count:

                flash("Student updated successfully!", "success")

            else:

                flash("Student not found.", "error")

        except DuplicateKeyError:

            flash("This email address is already registered.", "error")

        except Exception:

            app.logger.exception("Student update failed")

            flash("Unable to update the student.", "error")

        return redirect(url_for("home"))

    student = students_collection.find_one(
        {"_id": student_object_id}
    )

    if student is None:

        flash("Student not found.", "error")

        return redirect(url_for("home"))

    return render_template("edit.html", student=student)

# DELETE STUDENT
@app.route("/delete/<student_id>", methods=["POST"])
def delete_student(student_id):

    if not ObjectId.is_valid(student_id):

        flash("Invalid student ID.", "error")

        return redirect(url_for("home"))

    try:

        result = students_collection.delete_one(
            {"_id": ObjectId(student_id)}
        )

        if result.deleted_count:

            flash("Student deleted successfully!", "success")

        else:

            flash("Student not found.", "error")

    except Exception:

        app.logger.exception("Student deletion failed")

        flash("Unable to delete the student.", "error")

    return redirect(url_for("home"))

if __name__ == "__main__":

    app.run(debug=True)