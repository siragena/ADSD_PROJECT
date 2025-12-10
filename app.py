from flask import Flask, render_template, request, redirect, url_for
from models import Class, Employer, Shift
from datetime import datetime, date



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


# ---------------- HELPERS ----------------

def times_overlap(start1, end1, start2, end2):
    """Return True if time interval [start1, end1) overlaps [start2, end2)."""
    return (start1 < end2) and (start2 < end1)


def compute_conflicts():
    all_classes = list(Class.select())
    all_shifts = list(Shift.select().join(Employer).order_by(Shift.date, Shift.start_time))

    class_conflicts = []
    shift_conflicts = []

    # Class vs Shift
    for shift in all_shifts:
        day_name = shift.date.strftime("%A")
        for c in all_classes:
            if c.day_of_week == day_name and times_overlap(
                shift.start_time, shift.end_time, c.start_time, c.end_time
            ):
                class_conflicts.append({"shift": shift, "cls": c})

    # Shift vs Shift
    n = len(all_shifts)
    for i in range(n):
        for j in range(i + 1, n):
            s1 = all_shifts[i]
            s2 = all_shifts[j]
            if s1.date == s2.date and times_overlap(
                s1.start_time, s1.end_time, s2.start_time, s2.end_time
            ):
                shift_conflicts.append({"s1": s1, "s2": s2})

    return class_conflicts, shift_conflicts


def compute_summary(start_date, end_date):
    query = Shift.select().join(Employer)
    if start_date:
        query = query.where(Shift.date >= start_date)
    if end_date:
        query = query.where(Shift.date <= end_date)

    shifts = list(query.order_by(Shift.date, Shift.start_time))

    total_hours = 0.0
    total_earnings = 0.0
    per_employer = {}

    for s in shifts:
        start_dt = datetime.combine(date.today(), s.start_time)
        end_dt = datetime.combine(date.today(), s.end_time)
        duration_hours = (end_dt - start_dt).total_seconds() / 3600.0

        total_hours += duration_hours
        earned = duration_hours * s.employer.hourly_rate
        total_earnings += earned

        name = s.employer.name
        if name not in per_employer:
            per_employer[name] = {"hours": 0.0, "earnings": 0.0}
        per_employer[name]["hours"] += duration_hours
        per_employer[name]["earnings"] += earned

    employer_stats = [
        {"name": name, "hours": data["hours"], "earnings": data["earnings"]}
        for name, data in per_employer.items()
    ]

    return shifts, total_hours, total_earnings, employer_stats


# ---------------- CONFLICTS + DOWNLOAD ----------------

@app.route("/conflicts")
def view_conflicts():
    class_conflicts, shift_conflicts = compute_conflicts()
    return render_template(
        "conflicts.html",
        class_conflicts=class_conflicts,
        shift_conflicts=shift_conflicts,
    )


@app.route("/conflicts/download")
def conflicts_download():
    class_conflicts, shift_conflicts = compute_conflicts()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    y = 800  # vertical position

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Schedule Conflicts Report")
    y -= 30

    # -------- Class vs Shift --------
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Class vs Shift Conflicts")
    y -= 20
    p.setFont("Helvetica", 10)

    if class_conflicts:
        for item in class_conflicts:
            if y < 50:  # new page if too low
                p.showPage()
                y = 800
                p.setFont("Helvetica", 10)

            s = item["shift"]
            c = item["cls"]
            line = (
                f"{s.date} {s.start_time}-{s.end_time} | {s.employer.name} ({s.notes}) "
                f"conflicts with {c.name} on {c.day_of_week} "
                f"{c.start_time}-{c.end_time} at {c.location}"
            )
            p.drawString(50, y, line)
            y -= 15
    else:
        p.drawString(50, y, "No class vs shift conflicts.")
        y -= 20

    # -------- Shift vs Shift --------
    if y < 80:
        p.showPage()
        y = 800

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Shift vs Shift Conflicts")
    y -= 20
    p.setFont("Helvetica", 10)

    if shift_conflicts:
        for pair in shift_conflicts:
            if y < 50:
                p.showPage()
                y = 800
                p.setFont("Helvetica", 10)

            s1 = pair["s1"]
            s2 = pair["s2"]
            line = (
                f"{s1.date} | {s1.start_time}-{s1.end_time} @ {s1.employer.name} ({s1.notes}) "
                f"overlaps {s2.start_time}-{s2.end_time} @ {s2.employer.name} ({s2.notes})"
            )
            p.drawString(50, y, line)
            y -= 15
    else:
        p.drawString(50, y, "No overlapping shifts.")
        y -= 20

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=conflicts.pdf"
    return response


# ---------------- SUMMARY + DOWNLOAD ----------------

@app.route("/summary", methods=["GET", "POST"])
def summary():
    start_date = None
    end_date = None

    # read from form (POST) or query string (GET)
    source = request.form if request.method == "POST" else request.args
    start_str = source.get("start_date")
    end_str = source.get("end_date")

    if start_str:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    if end_str:
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

    shifts, total_hours, total_earnings, employer_stats = compute_summary(
        start_date, end_date
    )

    return render_template(
        "summary.html",
        shifts=shifts,
        start_date=start_date,
        end_date=end_date,
        total_hours=total_hours,
        total_earnings=total_earnings,
        employer_stats=employer_stats,
    )


@app.route("/summary/download")
def summary_download():
    start_str = request.args.get("start_date")
    end_str = request.args.get("end_date")

    start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
    end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None

    shifts, total_hours, total_earnings, employer_stats = compute_summary(
        start_date, end_date
    )

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    y = 800

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Work Summary Report")
    y -= 25

    # Date range
    p.setFont("Helvetica", 10)
    if start_date or end_date:
        p.drawString(
            50,
            y,
            f"Date range: "
            f"{start_date if start_date else '...'} to {end_date if end_date else '...'}",
        )
        y -= 20

    # Totals
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total hours: {total_hours:.2f}")
    y -= 15
    p.drawString(50, y, f"Total earnings: ${total_earnings:.2f}")
    y -= 25

    # By employer
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "By employer:")
    y -= 18
    p.setFont("Helvetica", 10)

    if employer_stats:
        for row in employer_stats:
            if y < 50:
                p.showPage()
                y = 800
                p.setFont("Helvetica", 10)

            line = (
                f"{row['name']}: {row['hours']:.2f} hours, "
                f"${row['earnings']:.2f}"
            )
            p.drawString(50, y, line)
            y -= 15
    else:
        p.drawString(50, y, "No shifts in this period.")
        y -= 20

    if y < 80:
        p.showPage()
        y = 800

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Shifts included:")
    y -= 18
    p.setFont("Helvetica", 10)

    if shifts:
        for s in shifts:
            if y < 50:
                p.showPage()
                y = 800
                p.setFont("Helvetica", 10)

            start_dt = datetime.combine(date.today(), s.start_time)
            end_dt = datetime.combine(date.today(), s.end_time)
            duration_hours = (end_dt - start_dt).total_seconds() / 3600.0

            line = (
                f"{s.date} {s.start_time}-{s.end_time} | "
                f"{s.employer.name} ({s.notes}) "
                f"[{duration_hours:.2f} hours]"
            )
            p.drawString(50, y, line)
            y -= 15
    else:
        p.drawString(50, y, "No shifts to list.")
        y -= 20

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=summary.pdf"
    return response
pyth

if __name__ == "__main__":
    app.run(debug=True)
