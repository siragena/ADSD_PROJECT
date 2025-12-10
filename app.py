from flask import Flask, render_template, request, redirect, url_for
from models import Class, Employer, Shift




app = Flask(__name__)


# ---------------- HOME ----------------

@app.route("/")
def index():
    num_classes = Class.select().count()
    num_employers = Employer.select().count()
    num_shifts = Shift.select().count()

    return render_template(
        "index.html",
        num_classes=num_classes,
        num_employers=num_employers,
        num_shifts=num_shifts,
    )


# ---------------- EMPLOYERS CRUD ----------------

@app.route("/employers")
def list_employers():
    employers = Employer.select()
    return render_template("employers_list.html", employers=employers)


@app.route("/employers/add", methods=["GET", "POST"])
def add_employer():
    if request.method == "POST":
        name = request.form.get("name")
        rate = request.form.get("hourly_rate")

        if name and rate:
            Employer.create(name=name, hourly_rate=float(rate))
            return redirect(url_for("list_employers"))

    return render_template("employer_add.html")


@app.route("/employers/<int:employer_id>/edit", methods=["GET", "POST"])
def edit_employer(employer_id):
    employer = Employer.get_or_none(Employer.id == employer_id)
    if employer is None:
        return "Employer not found", 404

    if request.method == "POST":
        name = request.form.get("name")
        rate = request.form.get("hourly_rate")

        if name and rate:
            employer.name = name
            employer.hourly_rate = float(rate)
            employer.save()
            return redirect(url_for("list_employers"))

    return render_template("employer_edit.html", employer=employer)


@app.route("/employers/<int:employer_id>/delete", methods=["POST"])
def delete_employer(employer_id):
    employer = Employer.get_or_none(Employer.id == employer_id)
    if employer:
        employer.delete_instance()
    return redirect(url_for("list_employers"))


# ---------------- CLASSES CRUD ----------------

@app.route("/classes")
def list_classes():
    classes = Class.select()
    return render_template("classes_list.html", classes=classes)


@app.route("/classes/add", methods=["GET", "POST"])
def add_class():
    if request.method == "POST":
        name = request.form.get("name")
        day = request.form.get("day_of_week")
        start = request.form.get("start_time")
        end = request.form.get("end_time")
        location = request.form.get("location")

        if name and day and start and end:
            Class.create(
                name=name,
                day_of_week=day,
                start_time=start,
                end_time=end,
                location=location,
            )
            return redirect(url_for("list_classes"))

    return render_template("class_add.html")


@app.route("/classes/<int:class_id>/edit", methods=["GET", "POST"])
def edit_class(class_id):
    c = Class.get_or_none(Class.id == class_id)
    if c is None:
        return "Class not found", 404

    if request.method == "POST":
        c.name = request.form.get("name")
        c.day_of_week = request.form.get("day_of_week")
        c.start_time = request.form.get("start_time")
        c.end_time = request.form.get("end_time")
        c.location = request.form.get("location")
        c.save()
        return redirect(url_for("list_classes"))

    return render_template("class_edit.html", c=c)


@app.route("/classes/<int:class_id>/delete", methods=["POST"])
def delete_class(class_id):
    c = Class.get_or_none(Class.id == class_id)
    if c:
        c.delete_instance()
    return redirect(url_for("list_classes"))


# ---------------- SHIFTS CRUD ----------------

@app.route("/shifts")
def list_shifts():
    shifts = Shift.select().order_by(Shift.date, Shift.start_time)
    return render_template("shifts_list.html", shifts=shifts)


@app.route("/shifts/add", methods=["GET", "POST"])
def add_shift():
    employers = Employer.select()

    if request.method == "POST":
        employer_id = request.form.get("employer_id")
        date_str = request.form.get("date")
        start = request.form.get("start_time")
        end = request.form.get("end_time")
        notes = request.form.get("notes")

        if employer_id and date_str and start and end:
            Shift.create(
                employer=employer_id,   # peewee accepts PK here
                date=date_str,
                start_time=start,
                end_time=end,
                notes=notes,
            )
            return redirect(url_for("list_shifts"))

    return render_template("shift_add.html", employers=employers)


@app.route("/shifts/<int:shift_id>/edit", methods=["GET", "POST"])
def edit_shift(shift_id):
    shift = Shift.get_or_none(Shift.id == shift_id)
    if shift is None:
        return "Shift not found", 404

    employers = Employer.select()

    if request.method == "POST":
        employer_id = request.form.get("employer_id")
        shift.employer = employer_id
        shift.date = request.form.get("date")
        shift.start_time = request.form.get("start_time")
        shift.end_time = request.form.get("end_time")
        shift.notes = request.form.get("notes")
        shift.save()
        return redirect(url_for("list_shifts"))

    return render_template("shift_edit.html", shift=shift, employers=employers)


@app.route("/shifts/<int:shift_id>/delete", methods=["POST"])
def delete_shift(shift_id):
    shift = Shift.get_or_none(Shift.id == shift_id)
    if shift:
        shift.delete_instance()
    return redirect(url_for("list_shifts"))


if __name__ == "__main__":
    app.run(debug=True)
