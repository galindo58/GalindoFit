import pymysql
import random
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'galindo_fit'
DB_PORT = 3306

def generar_datos():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    
    nombres = ["Carlos Ruiz", "Maria Gomez", "Luis Fernandez", "Ana Martinez", "Jorge Lopez", 
               "Sofia Torres", "Pedro Diaz", "Laura Sanchez", "Diego Moreno", "Marta Alvarez",
               "David Romero", "Elena Navarro", "Miguel Castro", "Lucia Ortiz", "Andres Silva"]
    
    comidas_ejemplo = [
        ('Desayuno', 'Avena con manzana y nueces', 350, 10, 50, 12),
        ('Desayuno', 'Huevos revueltos con tostadas', 400, 25, 30, 20),
        ('Almuerzo', 'Pechuga de pollo con arroz y ensalada', 600, 45, 60, 15),
        ('Almuerzo', 'Salmón a la plancha con quinoa', 650, 40, 50, 25),
        ('Cena', 'Ensalada César con pollo', 450, 35, 20, 25),
        ('Cena', 'Pescado blanco con vegetales al vapor', 380, 35, 15, 10),
        ('Snack', 'Yogur griego con almendras', 200, 15, 10, 10),
        ('Snack', 'Batido de proteína de suero', 150, 25, 5, 2)
    ]
    
    hashed_pw = generate_password_hash('cambiame123')
    
    try:
        with conn.cursor() as cursor:
            for i, nombre in enumerate(nombres):
                # Generar usuario
                email = f"{nombre.lower().replace(' ', '.')}@gmail.com"
                id_plan = random.choice([1, 2, 3])
                peso_inicial = round(random.uniform(60.0, 100.0), 1)
                calorias = random.choice([1800, 2000, 2500, 2800])
                prot = round(calorias * 0.3 / 4, 1)
                carb = round(calorias * 0.4 / 4, 1)
                fat = round(calorias * 0.3 / 9, 1)
                
                print(f"Insertando {nombre}...")
                cursor.execute("""
                    INSERT INTO usuarios (id_rol, id_plan, nombre, email, password_hash, peso_kg, calorias_objetivo, proteinas_objetivo, carbohidratos_objetivo, grasas_objetivo, plan_nutricional)
                    VALUES (2, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Recuerda beber mucha agua.')
                """, (id_plan, nombre, email, hashed_pw, peso_inicial, calorias, prot, carb, fat))
                
                user_id = cursor.lastrowid
                
                # Generar progreso de peso (últimos 30 días, 5 registros)
                peso_actual = peso_inicial + random.uniform(2.0, 5.0) # Empezó pesando más
                for dias_atras in [30, 21, 14, 7, 0]:
                    fecha = date.today() - timedelta(days=dias_atras)
                    # El peso va bajando poco a poco hacia el peso inicial de hoy
                    peso_registro = peso_actual - ((30 - dias_atras) / 30) * (peso_actual - peso_inicial)
                    peso_registro += random.uniform(-0.5, 0.5) # Ruido
                    cursor.execute("""
                        INSERT INTO progreso_peso (id_usuario, peso_kg, fecha_registro) 
                        VALUES (%s, %s, %s)
                    """, (user_id, round(peso_registro, 1), fecha))
                
                # Generar algunas comidas
                for _ in range(4): # 4 comidas aleatorias por atleta
                    comida = random.choice(comidas_ejemplo)
                    cursor.execute("""
                        INSERT INTO comidas_plan (id_usuario, tipo_comida, descripcion, calorias, proteinas_g, carbohidratos_g, grasas_g)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, comida[0], comida[1], comida[2], comida[3], comida[4], comida[5]))
                    
        conn.commit()
        print("¡15 atletas creados exitosamente con progresos y dietas!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    generar_datos()
