
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secreto"

# Diccionario para almacenar horarios y tarifas
schedules = {}
rate_per_hour = {"Lunes-Viernes": 1250, "Sábado": 1500}
days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        employee = request.form["employee"]
        day = request.form["day"]
        entrada = request.form["entrada"]
        salida = request.form["salida"]

        # Validar que las horas sean correctas
        if entrada >= salida:
            flash("La hora de salida debe ser mayor que la de entrada.", "danger")
            return redirect(url_for("index"))

        # Calcular horas trabajadas
        entrada_horas, entrada_minutos = map(int, entrada.split(":"))
        salida_horas, salida_minutos = map(int, salida.split(":"))
        horas_trabajadas = (salida_horas + salida_minutos / 60) - (entrada_horas + entrada_minutos / 60)

        # Determinar tarifa por hora
        tarifa = rate_per_hour["Lunes-Viernes"] if day in days[:-1] else rate_per_hour["Sábado"]
        pago = round(horas_trabajadas * tarifa, 2)

        # Guardar en `schedules`
        if employee not in schedules:
            schedules[employee] = {}
        schedules[employee][day] = {"entrada": entrada, "salida": salida, "horas": horas_trabajadas, "pago": pago}

        flash(f"Registro guardado para {employee} el {day}.", "success")
        return redirect(url_for("index"))

    return render_template("index.html", schedules=schedules, days=days, rate_per_hour=rate_per_hour)

@app.route("/update_rate", methods=["POST"])
def update_rate():
    rate_per_hour["Lunes-Viernes"] = int(request.form.get("rate_week", 1250))
    rate_per_hour["Sábado"] = int(request.form.get("rate_saturday", 1500))
    flash("Tarifas actualizadas correctamente.", "success")
    return redirect(url_for("index"))

@app.route("/resumen/<employee>")
def resumen_empleado(employee):
    if employee not in schedules:
        flash("Empleado no encontrado.", "danger")
        return redirect(url_for("index"))

    schedule = schedules[employee]
    total_horas = sum(entry["horas"] for entry in schedule.values())
    total_pago = sum(entry["pago"] for entry in schedule.values())

    return render_template("resumen_empleado.html", employee=employee, schedule=schedule, days=days, total=total_horas, total_pago=total_pago)

if __name__ == "__main__":
    app.run(debug=True)

