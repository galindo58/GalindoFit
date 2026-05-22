import pymysql
import pymysql.cursors

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'galindo_fit'
DB_PORT = 3306

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rutinas (
            id_rutina INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dias_rutina (
            id_dia INT AUTO_INCREMENT PRIMARY KEY,
            id_rutina INT NOT NULL,
            nombre_dia VARCHAR(100) NOT NULL,
            orden INT DEFAULT 1,
            FOREIGN KEY (id_rutina) REFERENCES rutinas(id_rutina) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ejercicios_dia (
            id_ejercicio INT AUTO_INCREMENT PRIMARY KEY,
            id_dia INT NOT NULL,
            nombre_ejercicio VARCHAR(150) NOT NULL,
            series INT DEFAULT 3,
            repeticiones VARCHAR(50) DEFAULT '12',
            peso_sugerido VARCHAR(50),
            descanso_seg INT DEFAULT 60,
            notas TEXT,
            orden INT DEFAULT 1,
            FOREIGN KEY (id_dia) REFERENCES dias_rutina(id_dia) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Add id_rutina column to usuarios if it doesn't exist
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN id_rutina INT DEFAULT NULL;")
        except Exception as e:
            # Column might already exist
            pass
            
    conn.commit()
    print("Database tables for routines created successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
