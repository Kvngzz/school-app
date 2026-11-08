from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret"

@app.route("/")
def home():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", students=students)

@app.route("/register", methods=["POST"])
def register():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    gender = request.form.get("gender", "")
    course = request.form.get("course", "")
    phone = request.form.get("phone", "").strip()

    if not all([full_name, email, gender, course, phone]):
        flash("Please fill in every field.", "error")
        return redirect(url_for("home"))

    connection = get_connection()
    cursor = connection.cursor()

    try:
        sql = """
            INSERT INTO students
            (full_name, email, gender, course, phone)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (full_name, email, gender, course, phone)
        cursor.execute(sql, values)
        connection.commit()

        flash("Student registered successfully!", "success")

    except Exception as error:
        connection.rollback()

        if getattr(error, "errno", None) == 1062:
            flash("This email address is already registered.", "error")
        else:
            app.logger.exception("Student registration failed")
            flash("Registration failed. Please try again.", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("home"))

@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            gender = request.form.get("gender", "")
            course = request.form.get("course", "")
            phone = request.form.get("phone", "").strip()

            if not all([full_name, email, gender, course, phone]):
                flash("Please fill in every field.", "error")
                return redirect(url_for("edit_student", student_id=student_id))

            cursor.execute("""
                UPDATE students
                SET full_name=%s, email=%s, gender=%s,
                    course=%s, phone=%s
                WHERE id=%s
            """, (full_name, email, gender, course, phone, student_id))

            connection.commit()
            flash("Student updated successfully!", "success")
            return redirect(url_for("home"))

        cursor.execute(
            "SELECT * FROM students WHERE id=%s", (student_id,)
        )
        student = cursor.fetchone()

        if student is None:
            flash("Student not found.", "error")
            return redirect(url_for("home"))

        return render_template("edit.html", student=student)

    except Exception:
        connection.rollback()
        app.logger.exception("Student edit failed")
        flash("Unable to update the student.", "error")
        return redirect(url_for("home"))

    finally:
        cursor.close()
        connection.close()

@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM students WHERE id=%s", (student_id,)
        )
        connection.commit()

        if cursor.rowcount:
            flash("Student deleted successfully!", "success")
        else:
            flash("Student not found.", "error")

    except Exception:
        connection.rollback()
        app.logger.exception("Student deletion failed")
        flash("Unable to delete the student.", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)