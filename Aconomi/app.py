from flask import Flask, render_template, request, g
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'carbon_footprint.db'

# Коэффициенты для расчёта (кг CO2)
CO2_FACTORS = {
    "transport": 0.2,
    "flights": 90,
    "diet": {
        "vegan": 50,
        "vegetarian": 100,
        "flexitarian": 150,
        "meat_eater": 200
    },
    "energy": 0.5
}
GOOD_THRESHOLD = 250

# Подключение к БД
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def save_calculation(data):
    """Сохраняем расчёт в БД."""
    query = '''
        INSERT INTO calculations 
        (transport_km, flight_hours, diet_type, energy_kwh, total_co2)
        VALUES (?, ?, ?, ?, ?)
    '''
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, (
        data['transport_km'],
        data['flight_hours'],
        data['diet_type'],
        data['energy_kwh'],
        data['total_co2']
    ))
    conn.commit()

def get_history():
    """Получаем последние 5 расчётов из БД."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT transport_km, flight_hours, diet_type, energy_kwh, total_co2, timestamp
        FROM calculations
        ORDER BY timestamp DESC
        LIMIT 5
    ''')
    return cursor.fetchall()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Получаем данные из формы
        transport_km = float(request.form.get("transport", 0))
        flight_hours = float(request.form.get("flights", 0))
        diet_type = request.form.get("diet")
        energy_kwh = float(request.form.get("energy", 0))
        
        # Расчёты
        total_co2 = (
            transport_km * CO2_FACTORS["transport"] +
            (flight_hours * CO2_FACTORS["flights"]) / 12 +
            CO2_FACTORS["diet"].get(diet_type, 200) +
            energy_kwh * CO2_FACTORS["energy"]
        )

        is_good_result = total_co2 < GOOD_THRESHOLD
            
        
        # Сохраняем в БД
        save_calculation({
            "transport_km": transport_km,
            "flight_hours": flight_hours,
            "diet_type": diet_type,
            "energy_kwh": energy_kwh,
            "total_co2": total_co2
        })

        # Советы
        tips = [
            "🚗 Используйте общественный транспорт.",
            "✈️ Летайте реже.",
            "🌱 Уменьшите потребление мяса.",
            "💡 Перейдите на зелёную энергию."
        ]
        
        # История из БД
        history = get_history()
        
        return render_template(
            "index.html",
            calculated=True,
            total=round(total_co2, 1),
            tips=tips,
            history=history
        )
        
    return render_template("index.html", calculated=False)
if __name__ == "__main__":
    app.run(debug=True)