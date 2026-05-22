-- ==========================================================
-- SCRIPT DE BASE DE DATOS PARA "GALINDO FIT"
-- ==========================================================

CREATE DATABASE IF NOT EXISTS galindo_fit;
USE galindo_fit;

-- 1. ROLES (Admin, Atleta)
CREATE TABLE IF NOT EXISTS roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

-- 2. PLANES DE SUSCRIPCIÓN
CREATE TABLE IF NOT EXISTS planes (
    id_plan INT AUTO_INCREMENT PRIMARY KEY,
    nombre_plan VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) DEFAULT 0.00
);

-- 3. USUARIOS (Atletas y Entrenadores)
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT NOT NULL,
    id_plan INT,
    nombre VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    peso_kg DECIMAL(5,2),
    calorias_objetivo INT,
    estado_suscripcion ENUM('Activa', 'Inactiva', 'Pendiente') DEFAULT 'Inactiva',
    fecha_vencimiento DATE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol),
    FOREIGN KEY (id_plan) REFERENCES planes(id_plan)
);

-- 4. SEGUIMIENTO DE PROGRESO (Para el gráfico de peso del Atleta)
CREATE TABLE IF NOT EXISTS progreso_peso (
    id_progreso INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    peso_kg DECIMAL(5,2) NOT NULL,
    fecha_registro DATE NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- 5. LIBRERÍA DE EJERCICIOS (Para crear rutinas)
CREATE TABLE IF NOT EXISTS ejercicios (
    id_ejercicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    grupo_muscular VARCHAR(50),
    url_video VARCHAR(255)
);

-- 6. RUTINAS (Cabecera de la rutina asignada al usuario)
CREATE TABLE IF NOT EXISTS rutinas (
    id_rutina INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    nombre_rutina VARCHAR(100) NOT NULL,
    dia_semana ENUM('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- 7. DETALLE DE RUTINAS (Los ejercicios que componen la rutina)
CREATE TABLE IF NOT EXISTS rutina_ejercicios (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_rutina INT NOT NULL,
    id_ejercicio INT NOT NULL,
    series INT DEFAULT 3,
    repeticiones VARCHAR(50) DEFAULT '10-12',
    notas TEXT,
    FOREIGN KEY (id_rutina) REFERENCES rutinas(id_rutina) ON DELETE CASCADE,
    FOREIGN KEY (id_ejercicio) REFERENCES ejercicios(id_ejercicio) ON DELETE CASCADE
);

-- ==========================================================
-- DATOS INICIALES (Mocks Iniciales)
-- ==========================================================

-- Insertar roles básicos
INSERT INTO roles (nombre_rol) VALUES ('Admin'), ('Atleta');

-- Insertar planes iniciales
INSERT INTO planes (nombre_plan, descripcion, precio) VALUES 
('Gratis', 'Acceso básico al contenido gratuito.', 0.00),
('Básico', 'Rutinas pregrabadas y plan de nutrición general.', 19.99),
('Elite Premium', 'Coaching 1 a 1, revisiones semanales y contacto directo.', 49.99),
('Aliado Corporativo', 'Plan especial para empresas y empleados.', 29.99);

-- Insertar el usuario Administrador (Contraseña temporal genérica, esto se encriptará luego en Python)
INSERT INTO usuarios (id_rol, nombre, username, email, password_hash, estado_suscripcion) 
VALUES (1, 'Entrenador Galindo', 'admin', 'admin@galindofit.com', 'pbkdf2:sha256:600000$superhashgenerico', 'Activa');