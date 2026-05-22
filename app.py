from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'un_secreto_muy_rudo_12345')

# Configuración DB (Soporta Railway y Local)
DB_HOST = os.getenv('MYSQLHOST', 'localhost')
DB_USER = os.getenv('MYSQLUSER', 'root')
DB_PASSWORD = os.getenv('MYSQLPASSWORD', '')
DB_NAME = os.getenv('MYSQLDATABASE', 'galindo_fit')
DB_PORT = int(os.getenv('MYSQLPORT', 3307)) # Puerto local 3307 por defecto (XAMPP), Railway lo sobreescribirá

def get_db_connection():
    try:
        return pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None

def init_db_mocks():
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE username = 'admin'")
            if not cursor.fetchone():
                admin_hash = generate_password_hash('admin123')
                cursor.execute("""
                    INSERT INTO usuarios (id_rol, nombre, username, email, password_hash, estado_suscripcion)
                    VALUES (1, 'Entrenador Galindo', 'admin', 'admin@galindofit.com', %s, 'Activa')
                """, (admin_hash,))
                cursor.execute("SELECT id_plan FROM planes")
                if not cursor.fetchall():
                    cursor.execute("INSERT INTO planes (nombre_plan, descripcion, precio) VALUES ('Gratis', 'Plan Basico', 0.00), ('Básico', 'Plan Básico', 19.99), ('Elite Premium', 'Plan Elite', 49.99)")
                user_hash = generate_password_hash('user123')
                cursor.execute("""
                    INSERT INTO usuarios (id_rol, id_plan, nombre, username, email, password_hash, peso_kg, calorias_objetivo, estado_suscripcion, plan_nutricional)
                    VALUES (2, 2, 'Atleta Prueba', 'atleta1', 'atleta@prueba.com', %s, 75.5, 2500, 'Activa', 'Plan de prueba')
                """, (user_hash,))
            conn.commit()
    except Exception as e:
        print(f"Error inicializando mocks: {e}")
    finally:
        conn.close()

@app.context_processor
def override_url_for():
    return dict(url_with_timestamp=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            if os.path.exists(file_path):
                values['q'] = int(os.path.getmtime(file_path))
    return url_for(endpoint, **values)

# ==========================================
# RUTAS PÚBLICAS Y AUTENTICACIÓN
# ==========================================
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        if not conn:
            flash('Error de conexión a la base de datos.', 'error')
            return render_template('login.html')
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE username = %s OR email = %s", (username, username))
            user = cursor.fetchone()
            if user and check_password_hash(user['password_hash'], password):
                if user['id_rol'] == 1:
                    flash('Esta entrada es para Atletas. Entrenadores deben usar su acceso especial.', 'error')
                else:
                    session['user_id'] = user['id_usuario']
                    session['id_rol'] = user['id_rol']
                    session['nombre'] = user['nombre']
                    return redirect(url_for('mi_portal'))
            else:
                flash('Credenciales incorrectas.', 'error')
        conn.close()
    return render_template('login.html')

@app.route('/login_entrenador', methods=['GET', 'POST'])
def login_entrenador():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        if not conn:
            flash('Error de conexión a la base de datos.', 'error')
            return render_template('login_entrenador.html')
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE username = %s OR email = %s", (username, username))
            user = cursor.fetchone()
            if user and check_password_hash(user['password_hash'], password):
                if user['id_rol'] == 2:
                    flash('Esta entrada es exclusiva para Entrenadores.', 'error')
                else:
                    session['user_id'] = user['id_usuario']
                    session['id_rol'] = user['id_rol']
                    session['nombre'] = user['nombre']
                    return redirect(url_for('dashboard'))
            else:
                flash('Credenciales incorrectas.', 'error')
        conn.close()
    return render_template('login_entrenador.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_pw = generate_password_hash(password)
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO usuarios (id_rol, id_plan, nombre, email, password_hash) VALUES (2, 1, %s, %s, %s)", (nombre, email, hashed_pw))
                conn.commit()
                flash('Registro exitoso. ¡Inicia sesión!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash('El correo ya está en uso o hubo un error.', 'error')
            finally:
                conn.close()
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ==========================================
# RUTAS DEL ATLETA (CLIENTE)
# ==========================================
@app.route('/mi_portal')
def mi_portal():
    if 'user_id' not in session or session.get('id_rol') != 2:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if not conn:
        return "Error DB", 500
    rutina = None
    dias_rutina = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT u.*, p.nombre_plan FROM usuarios u LEFT JOIN planes p ON u.id_plan = p.id_plan WHERE u.id_usuario = %s", (session['user_id'],))
            atleta = cursor.fetchone()
            cursor.execute("SELECT * FROM progreso_peso WHERE id_usuario = %s ORDER BY fecha_registro ASC", (session['user_id'],))
            progreso = cursor.fetchall()
            cursor.execute("SELECT * FROM comidas_plan WHERE id_usuario = %s ORDER BY FIELD(tipo_comida, 'Desayuno', 'Almuerzo', 'Cena', 'Snack'), orden ASC", (session['user_id'],))
            comidas = cursor.fetchall()
            
            if atleta and atleta.get('id_rutina'):
                cursor.execute("SELECT * FROM rutinas WHERE id_rutina = %s", (atleta['id_rutina'],))
                rutina = cursor.fetchone()
                if rutina:
                    cursor.execute("SELECT * FROM dias_rutina WHERE id_rutina = %s ORDER BY orden ASC", (rutina['id_rutina'],))
                    dias_rutina = cursor.fetchall()
                    for dia in dias_rutina:
                        cursor.execute("SELECT * FROM ejercicios_dia WHERE id_dia = %s ORDER BY orden ASC", (dia['id_dia'],))
                        dia['ejercicios'] = cursor.fetchall()
    finally:
        conn.close()
    return render_template('portal_atleta.html', atleta=atleta, progreso=progreso, comidas=comidas, rutina=rutina, dias_rutina=dias_rutina)

@app.route('/registrar_peso', methods=['POST'])
def registrar_peso():
    if 'user_id' not in session or session.get('id_rol') != 2:
        return redirect(url_for('login'))
    peso = request.form.get('peso_kg')
    conn = get_db_connection()
    if conn and peso:
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO progreso_peso (id_usuario, peso_kg, fecha_registro) VALUES (%s, %s, %s)", (session['user_id'], peso, date.today()))
                cursor.execute("UPDATE usuarios SET peso_kg = %s WHERE id_usuario = %s", (peso, session['user_id']))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('mi_portal'))

# ==========================================
# RUTAS DEL ADMINISTRADOR (ENTRENADOR)
# ==========================================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    search = request.args.get('search', '')
    plan_filter = request.args.get('plan', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    conn = get_db_connection()
    error_db = False
    planes = []
    usuarios = []
    total_pages = 1
    
    if not conn:
        error_db = True
    else:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM planes")
                planes = cursor.fetchall()
                
                # Construir base de la consulta
                base_query = "FROM usuarios u LEFT JOIN planes p ON u.id_plan = p.id_plan WHERE u.id_rol = 2"
                params = []
                
                if search:
                    base_query += " AND (u.nombre LIKE %s OR u.email LIKE %s)"
                    params.extend([f"%{search}%", f"%{search}%"])
                if plan_filter:
                    base_query += " AND u.id_plan = %s"
                    params.append(plan_filter)
                
                # Contar totales para paginación
                count_query = f"SELECT COUNT(*) as total {base_query}"
                cursor.execute(count_query, tuple(params))
                total_records = cursor.fetchone()['total']
                import math
                total_pages = math.ceil(total_records / per_page) if total_records > 0 else 1
                
                # Consulta final con LIMIT y OFFSET
                offset = (page - 1) * per_page
                query = f"SELECT u.*, p.nombre_plan {base_query} ORDER BY u.id_usuario DESC LIMIT %s OFFSET %s"
                params.extend([per_page, offset])
                
                cursor.execute(query, tuple(params))
                usuarios = cursor.fetchall()
        except Exception as e:
            error_db = True
        finally:
            conn.close()
    return render_template('dashboard.html', planes=planes, usuarios=usuarios, search=search, plan_filter=plan_filter, error_db=error_db, page=page, total_pages=total_pages)

@app.route('/nuevo_atleta', methods=['GET', 'POST'])
def nuevo_atleta():
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        id_plan = request.form.get('id_plan')
        peso_kg = request.form.get('peso_kg') or None
        calorias_objetivo = request.form.get('calorias_objetivo') or None
        hashed_pw = generate_password_hash('cambiame123')
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO usuarios (id_rol, id_plan, nombre, email, password_hash, peso_kg, calorias_objetivo)
                    VALUES (2, %s, %s, %s, %s, %s, %s)
                """, (id_plan, nombre, email, hashed_pw, peso_kg, calorias_objetivo))
                
                if peso_kg:
                    nuevo_id = cursor.lastrowid
                    cursor.execute("INSERT INTO progreso_peso (id_usuario, peso_kg, fecha_registro) VALUES (%s, %s, %s)", (nuevo_id, peso_kg, date.today()))
                    
            conn.commit()
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Error al crear: El correo ya existe.', 'error')
        finally:
            conn.close()
    # GET
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM planes")
            planes = cursor.fetchall()
    finally:
        conn.close()
    return render_template('nuevo_atleta.html', planes=planes)

@app.route('/perfil_atleta/<int:id>', methods=['GET'])
def perfil_atleta(id):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('dashboard'))
    rutina = None
    dias_rutina = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT u.*, p.nombre_plan FROM usuarios u LEFT JOIN planes p ON u.id_plan = p.id_plan WHERE u.id_usuario = %s AND u.id_rol = 2", (id,))
            atleta = cursor.fetchone()
            cursor.execute("SELECT * FROM progreso_peso WHERE id_usuario = %s ORDER BY fecha_registro ASC", (id,))
            progreso = cursor.fetchall()
            cursor.execute("SELECT * FROM comidas_plan WHERE id_usuario = %s ORDER BY FIELD(tipo_comida, 'Desayuno', 'Almuerzo', 'Cena', 'Snack'), orden ASC", (id,))
            comidas = cursor.fetchall()
            
            if atleta and atleta.get('id_rutina'):
                cursor.execute("SELECT * FROM rutinas WHERE id_rutina = %s", (atleta['id_rutina'],))
                rutina = cursor.fetchone()
                if rutina:
                    cursor.execute("SELECT * FROM dias_rutina WHERE id_rutina = %s ORDER BY orden ASC", (rutina['id_rutina'],))
                    dias_rutina = cursor.fetchall()
                    for dia in dias_rutina:
                        cursor.execute("SELECT * FROM ejercicios_dia WHERE id_dia = %s ORDER BY orden ASC", (dia['id_dia'],))
                        dia['ejercicios'] = cursor.fetchall()
    finally:
        conn.close()
    if not atleta:
        return redirect(url_for('dashboard'))
    return render_template('perfil_atleta.html', atleta=atleta, progreso=progreso, comidas=comidas, rutina=rutina, dias_rutina=dias_rutina)

@app.route('/editar_atleta/<int:id>', methods=['GET'])
def editar_atleta(id):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('dashboard'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s AND id_rol = 2", (id,))
            atleta = cursor.fetchone()
            cursor.execute("SELECT * FROM planes")
            planes = cursor.fetchall()
            cursor.execute("SELECT * FROM comidas_plan WHERE id_usuario = %s ORDER BY FIELD(tipo_comida, 'Desayuno', 'Almuerzo', 'Cena', 'Snack'), orden ASC", (id,))
            comidas = cursor.fetchall()
            cursor.execute("SELECT * FROM rutinas ORDER BY nombre ASC")
            rutinas_list = cursor.fetchall()
    finally:
        conn.close()
    if not atleta:
        return redirect(url_for('dashboard'))
    return render_template('editar_atleta.html', atleta=atleta, planes=planes, comidas=comidas, rutinas=rutinas_list)

@app.route('/guardar_edicion/<int:id>', methods=['POST'])
def guardar_edicion(id):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    id_plan = request.form.get('id_plan')
    peso_kg = request.form.get('peso_kg') or None
    calorias_objetivo = request.form.get('calorias_objetivo') or None
    plan_nutricional = request.form.get('plan_nutricional')
    proteinas_objetivo = request.form.get('proteinas_objetivo') or 0
    carbohidratos_objetivo = request.form.get('carbohidratos_objetivo') or 0
    grasas_objetivo = request.form.get('grasas_objetivo') or 0
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                id_rutina = request.form.get('id_rutina') or None
                cursor.execute("""
                    UPDATE usuarios 
                    SET nombre=%s, email=%s, id_plan=%s, peso_kg=%s, calorias_objetivo=%s, 
                        plan_nutricional=%s, proteinas_objetivo=%s, carbohidratos_objetivo=%s, grasas_objetivo=%s, id_rutina=%s
                    WHERE id_usuario=%s AND id_rol=2
                """, (nombre, email, id_plan, peso_kg, calorias_objetivo, plan_nutricional, proteinas_objetivo, carbohidratos_objetivo, grasas_objetivo, id_rutina, id))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('perfil_atleta', id=id))

@app.route('/agregar_comida/<int:id>', methods=['POST'])
def agregar_comida(id):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    tipo_comida = request.form.get('tipo_comida')
    descripcion = request.form.get('descripcion')
    calorias = request.form.get('calorias') or 0
    proteinas_g = request.form.get('proteinas_g') or 0
    carbohidratos_g = request.form.get('carbohidratos_g') or 0
    grasas_g = request.form.get('grasas_g') or 0
    conn = get_db_connection()
    if conn and descripcion:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO comidas_plan (id_usuario, tipo_comida, descripcion, calorias, proteinas_g, carbohidratos_g, grasas_g)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (id, tipo_comida, descripcion, calorias, proteinas_g, carbohidratos_g, grasas_g))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('editar_atleta', id=id))

@app.route('/eliminar_comida/<int:id_comida>/<int:id_usuario>', methods=['POST'])
def eliminar_comida(id_comida, id_usuario):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM comidas_plan WHERE id_comida = %s AND id_usuario = %s", (id_comida, id_usuario))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('editar_atleta', id=id_usuario))

@app.route('/eliminar_usuario/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s AND id_rol = 2", (id,))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('dashboard'))

# ==========================================
# RUTAS DE RUTINAS DE ENTRENAMIENTO
# ==========================================
@app.route('/rutinas')
def rutinas():
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    rutinas = []
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.*, COUNT(d.id_dia) as num_dias
                    FROM rutinas r
                    LEFT JOIN dias_rutina d ON r.id_rutina = d.id_rutina
                    GROUP BY r.id_rutina
                    ORDER BY r.id_rutina DESC
                """)
                rutinas = cursor.fetchall()
        finally:
            conn.close()
    return render_template('rutinas.html', rutinas=rutinas)

@app.route('/nueva_rutina', methods=['GET', 'POST'])
def nueva_rutina():
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        conn = get_db_connection()
        if conn and nombre:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO rutinas (nombre, descripcion) VALUES (%s, %s)", (nombre, descripcion))
                conn.commit()
                return redirect(url_for('rutinas'))
            except Exception as e:
                flash('Error al crear la rutina.', 'error')
            finally:
                conn.close()
    return render_template('nueva_rutina.html')

@app.route('/editar_rutina/<int:id>')
def editar_rutina(id):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('rutinas'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM rutinas WHERE id_rutina = %s", (id,))
            rutina = cursor.fetchone()
            if not rutina:
                return redirect(url_for('rutinas'))
            
            cursor.execute("SELECT * FROM dias_rutina WHERE id_rutina = %s ORDER BY orden ASC", (id,))
            dias = cursor.fetchall()
            
            for dia in dias:
                cursor.execute("SELECT * FROM ejercicios_dia WHERE id_dia = %s ORDER BY orden ASC", (dia['id_dia'],))
                dia['ejercicios'] = cursor.fetchall()
    finally:
        conn.close()
    return render_template('editar_rutina.html', rutina=rutina, dias=dias)

@app.route('/agregar_dia/<int:id_rutina>', methods=['POST'])
def agregar_dia(id_rutina):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    nombre_dia = request.form.get('nombre_dia')
    conn = get_db_connection()
    if conn and nombre_dia:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COALESCE(MAX(orden), 0) + 1 as next_orden FROM dias_rutina WHERE id_rutina = %s", (id_rutina,))
                next_orden = cursor.fetchone()['next_orden']
                cursor.execute("INSERT INTO dias_rutina (id_rutina, nombre_dia, orden) VALUES (%s, %s, %s)", (id_rutina, nombre_dia, next_orden))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('editar_rutina', id=id_rutina))

@app.route('/eliminar_dia/<int:id_dia>/<int:id_rutina>', methods=['POST'])
def eliminar_dia(id_dia, id_rutina):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM dias_rutina WHERE id_dia = %s", (id_dia,))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('editar_rutina', id=id_rutina))

@app.route('/agregar_ejercicio/<int:id_dia>/<int:id_rutina>', methods=['POST'])
def agregar_ejercicio(id_dia, id_rutina):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    nombre_ejercicio = request.form.get('nombre_ejercicio')
    series = request.form.get('series') or 4
    repeticiones = request.form.get('repeticiones') or '12'
    peso_sugerido = request.form.get('peso_sugerido') or None
    descanso_seg = request.form.get('descanso_seg') or 60
    notas = request.form.get('notas') or None
    conn = get_db_connection()
    if conn and nombre_ejercicio:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COALESCE(MAX(orden), 0) + 1 as next_orden FROM ejercicios_dia WHERE id_dia = %s", (id_dia,))
                next_orden = cursor.fetchone()['next_orden']
                cursor.execute("""
                    INSERT INTO ejercicios_dia (id_dia, nombre_ejercicio, series, repeticiones, peso_sugerido, descanso_seg, notas, orden)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (id_dia, nombre_ejercicio, series, repeticiones, peso_sugerido, descanso_seg, notas, next_orden))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('editar_rutina', id=id_rutina))

@app.route('/eliminar_ejercicio/<int:id_ejercicio>/<int:id_rutina>', methods=['POST'])
def eliminar_ejercicio(id_ejercicio, id_rutina):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM ejercicios_dia WHERE id_ejercicio = %s", (id_ejercicio,))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('editar_rutina', id=id_rutina))

@app.route('/eliminar_rutina/<int:id>', methods=['POST'])
def eliminar_rutina(id):
    if 'user_id' not in session or session.get('id_rol') != 1:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE usuarios SET id_rutina = NULL WHERE id_rutina = %s", (id,))
                cursor.execute("DELETE FROM rutinas WHERE id_rutina = %s", (id,))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('rutinas'))

if __name__ == '__main__':
    init_db_mocks()
    app.run(debug=True)