from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"  # Requerido para usar flash messages

# Tarifas por hora (modificables desde la interfaz)
rate_per_hour = {"Lunes-Viernes": 1250, "Sábado": 1500}

# Días de la semana que se considerarán
days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

# Diccionario global para almacenar los registros diarios de cada empleado.
schedules = {}

def format_hours(float_hours):
    """
    Convierte un número de horas en formato flotante a un string con formato H:MM,
    redondeando los minutos.
    """
    total_minutes = round(float_hours * 60)  # redondea el total de minutos
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}:{minutes:02d}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        employee = request.form.get("employee", "").strip()
        day = request.form.get("day", "")
        entrada_str = request.form.get("entrada", "")
        salida_str = request.form.get("salida", "")

        if not employee:
            flash("Por favor, ingrese el nombre del empleado.", "error")
            return redirect(url_for("index"))
        if day not in days:
            flash("Seleccione un día válido.", "error")
            return redirect(url_for("index"))

        # Se valida que se hayan ingresado ambos horarios
        if entrada_str and salida_str:
            try:
                entrada = datetime.strptime(entrada_str, "%H:%M")
                salida = datetime.strptime(salida_str, "%H:%M")
                if salida <= entrada:
                    flash(f"En {day}, la hora de salida debe ser mayor que la de entrada.", "error")
                    return redirect(url_for("index"))
                diff_seconds = (salida - entrada).seconds
                hours_float = diff_seconds / 3600.0
            except ValueError:
                flash(f"Formato de hora inválido en {day}. Use el formato HH:MM.", "error")
                return redirect(url_for("index"))
        else:
            flash("Debe ingresar ambas horas: entrada y salida.", "error")
            return redirect(url_for("index"))

        # Si el empleado no existe en el diccionario, se crea su registro
        if employee not in schedules:
            schedules[employee] = {}

        tarifa = rate_per_hour["Sábado"] if day == "Sábado" else rate_per_hour["Lunes-Viernes"]
        pago_dia = round(hours_float * tarifa, 2)

        schedules[employee][day] = {
            "entrada": entrada_str,
            "salida": salida_str,
            "horas_float": hours_float,
            "horas": format_hours(hours_float),
            "pago": pago_dia
        }
        flash(f"Registro guardado para {employee} en {day}: {format_hours(hours_float)} horas, Gana: ${pago_dia}", "success")
        return redirect(url_for("index"))
    
    return render_template("index.html", schedules=schedules, days=days, rate_per_hour=rate_per_hour)

@app.route("/resumen/<employee>")
def resumen_empleado(employee):
    if employee not in schedules:
        flash("Empleado no encontrado.", "error")
        return redirect(url_for("index"))
    
    employee_schedule = schedules[employee]
    total_float = sum(employee_schedule[day]["horas_float"] for day in employee_schedule)
    total_pago = sum(employee_schedule[day]["pago"] for day in employee_schedule)
    total_formatted = format_hours(total_float)
    
    return render_template("resumen_empleado.html", employee=employee, schedule=employee_schedule, total=total_formatted, total_pago=total_pago, days=days)

@app.route("/update_rate", methods=["POST"])
def update_rate():
    rate_per_hour["Lunes-Viernes"] = int(request.form.get("rate_week", 1250))
    rate_per_hour["Sábado"] = int(request.form.get("rate_saturday", 1500))
    flash("Tarifas actualizadas correctamente.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

