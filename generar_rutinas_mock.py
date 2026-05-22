import pymysql
import pymysql.cursors
import random

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'galindo_fit'
DB_PORT = 3306

rutinas_data = [
    {
        "nombre": "Hipertrofia Principiante",
        "descripcion": "Rutina ideal para quienes buscan aumentar masa muscular de forma estructurada. Enfocada en grupos musculares grandes 3 días a la semana.",
        "dias": [
            {
                "nombre_dia": "Día 1: Pecho y Tríceps",
                "ejercicios": [
                    {"nombre": "Press de Banca Plano", "series": 4, "reps": "10-12", "descanso": 90, "notas": "Controlar la bajada (fase excéntrica)"},
                    {"nombre": "Press Inclinado con Mancuernas", "series": 3, "reps": "12", "descanso": 60, "notas": ""},
                    {"nombre": "Aperturas en Polea", "series": 3, "reps": "15", "descanso": 60, "notas": "Apretar el pecho al centro"},
                    {"nombre": "Extensión de Tríceps en Polea", "series": 4, "reps": "12-15", "descanso": 60, "notas": ""},
                    {"nombre": "Press Francés", "series": 3, "reps": "12", "descanso": 60, "notas": "Evitar mover los codos"}
                ]
            },
            {
                "nombre_dia": "Día 2: Espalda y Bíceps",
                "ejercicios": [
                    {"nombre": "Dominadas (o Jalón al Pecho)", "series": 4, "reps": "8-10", "descanso": 90, "notas": "Pecho fuera, retracción escapular"},
                    {"nombre": "Remo con Barra", "series": 4, "reps": "10-12", "descanso": 90, "notas": "Espalda recta"},
                    {"nombre": "Remo Gironda", "series": 3, "reps": "12", "descanso": 60, "notas": ""},
                    {"nombre": "Curl de Bíceps con Barra", "series": 4, "reps": "10-12", "descanso": 60, "notas": ""},
                    {"nombre": "Curl Martillo", "series": 3, "reps": "12-15", "descanso": 60, "notas": "Para el braquial"}
                ]
            },
            {
                "nombre_dia": "Día 3: Pierna Completa",
                "ejercicios": [
                    {"nombre": "Sentadilla Libre", "series": 4, "reps": "8-10", "descanso": 120, "notas": "Bajar rompiendo el paralelo si es posible"},
                    {"nombre": "Prensa Inclinada", "series": 4, "reps": "12", "descanso": 90, "notas": "Pies a la anchura de los hombros"},
                    {"nombre": "Extensiones de Cuádriceps", "series": 3, "reps": "15", "descanso": 60, "notas": "Apretar arriba 1 segundo"},
                    {"nombre": "Curl de Isquios Tumbado", "series": 4, "reps": "12", "descanso": 60, "notas": ""},
                    {"nombre": "Elevación de Talones (Gemelos)", "series": 4, "reps": "20", "descanso": 45, "notas": ""}
                ]
            }
        ]
    },
    {
        "nombre": "Fuerza 5x5 Avanzado",
        "descripcion": "Programa clásico de ganancia de fuerza pura en base a levantamientos compuestos.",
        "dias": [
            {
                "nombre_dia": "Día A: Sentadilla y Press",
                "ejercicios": [
                    {"nombre": "Sentadilla", "series": 5, "reps": "5", "descanso": 180, "notas": "Añadir 2.5kg respecto a la semana pasada"},
                    {"nombre": "Press de Banca", "series": 5, "reps": "5", "descanso": 180, "notas": "Pausar la barra en el pecho"},
                    {"nombre": "Remo Pendlay", "series": 5, "reps": "5", "descanso": 180, "notas": "La barra toca el suelo en cada rep"}
                ]
            },
            {
                "nombre_dia": "Día B: Peso Muerto y Militar",
                "ejercicios": [
                    {"nombre": "Sentadilla (Ligera)", "series": 3, "reps": "5", "descanso": 120, "notas": "Día de recuperación activa"},
                    {"nombre": "Press Militar de Pie", "series": 5, "reps": "5", "descanso": 180, "notas": "No arquear la espalda baja en exceso"},
                    {"nombre": "Peso Muerto", "series": 1, "reps": "5", "descanso": 240, "notas": "Solo 1 serie pesada al máximo esfuerzo"}
                ]
            }
        ]
    },
    {
        "nombre": "Pérdida de Grasa (Cardio + Pesas)",
        "descripcion": "Rutina metabólica de alta intensidad combinada con pesas ligeras, ideal para definición.",
        "dias": [
            {
                "nombre_dia": "Día 1: Tren Superior + HIIT",
                "ejercicios": [
                    {"nombre": "Flexiones", "series": 4, "reps": "Al fallo", "descanso": 60, "notas": ""},
                    {"nombre": "Remo con Mancuernas", "series": 4, "reps": "15", "descanso": 60, "notas": "Poco peso, movimiento continuo"},
                    {"nombre": "Press Militar con Mancuernas", "series": 4, "reps": "15", "descanso": 60, "notas": ""},
                    {"nombre": "Sprints en Cinta", "series": 8, "reps": "20 segs sprint", "descanso": 40, "notas": "Protocolo Tabata al final de la sesión"}
                ]
            },
            {
                "nombre_dia": "Día 2: Tren Inferior + Core",
                "ejercicios": [
                    {"nombre": "Sentadillas con Salto", "series": 4, "reps": "20", "descanso": 45, "notas": "Aterrizaje suave"},
                    {"nombre": "Zancadas Caminando", "series": 4, "reps": "24", "descanso": 60, "notas": "12 por pierna"},
                    {"nombre": "Plancha Abdominal", "series": 4, "reps": "60 segs", "descanso": 30, "notas": "Contraer glúteos y abdomen"},
                    {"nombre": "Crunches en Polea", "series": 3, "reps": "20", "descanso": 45, "notas": ""}
                ]
            }
        ]
    }
]

try:
    print("Conectando a la base de datos...")
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )
    
    rutinas_ids = []
    
    with conn.cursor() as cursor:
        print("Creando rutinas de prueba...")
        for r in rutinas_data:
            # 1. Insertar Rutina
            cursor.execute("INSERT INTO rutinas (nombre, descripcion) VALUES (%s, %s)", (r['nombre'], r['descripcion']))
            id_rutina = cursor.lastrowid
            rutinas_ids.append(id_rutina)
            
            # 2. Insertar Días
            orden_dia = 1
            for d in r['dias']:
                cursor.execute("INSERT INTO dias_rutina (id_rutina, nombre_dia, orden) VALUES (%s, %s, %s)", 
                               (id_rutina, d['nombre_dia'], orden_dia))
                id_dia = cursor.lastrowid
                orden_dia += 1
                
                # 3. Insertar Ejercicios
                orden_ej = 1
                for ej in d['ejercicios']:
                    cursor.execute("""
                        INSERT INTO ejercicios_dia (id_dia, nombre_ejercicio, series, repeticiones, descanso_seg, notas, orden)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (id_dia, ej['nombre'], ej['series'], ej['reps'], ej['descanso'], ej['notas'], orden_ej))
                    orden_ej += 1
        
        print("Obteniendo usuarios atletas...")
        cursor.execute("SELECT id_usuario FROM usuarios WHERE id_rol = 2")
        atletas = cursor.fetchall()
        
        print(f"Asignando rutinas al azar a {len(atletas)} atletas...")
        for atleta in atletas:
            rutina_asignada = random.choice(rutinas_ids)
            cursor.execute("UPDATE usuarios SET id_rutina = %s WHERE id_usuario = %s", (rutina_asignada, atleta['id_usuario']))
            
    conn.commit()
    print("¡Listo! Las rutinas se han creado y asignado exitosamente.")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
