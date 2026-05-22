-- ============================================
-- MÓDULO DE RUTINAS - GALINDO FIT
-- Ejecutar en phpMyAdmin sobre la BD galindo_fit
-- ============================================

-- Tabla de rutinas maestras (catálogo)
CREATE TABLE IF NOT EXISTS rutinas (
    id_rutina INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Días de cada rutina
CREATE TABLE IF NOT EXISTS dias_rutina (
    id_dia INT AUTO_INCREMENT PRIMARY KEY,
    id_rutina INT NOT NULL,
    nombre_dia VARCHAR(100) NOT NULL,
    orden INT DEFAULT 1,
    FOREIGN KEY (id_rutina) REFERENCES rutinas(id_rutina) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Ejercicios de cada día
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

-- Columna de asignación de rutina en usuarios
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS id_rutina INT DEFAULT NULL;
