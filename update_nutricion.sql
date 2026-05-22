USE galindo_fit;

-- =============================================
-- Tabla de comidas estructuradas por atleta
-- =============================================
CREATE TABLE IF NOT EXISTS comidas_plan (
    id_comida INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    tipo_comida ENUM('Desayuno', 'Almuerzo', 'Cena', 'Snack') NOT NULL,
    descripcion TEXT NOT NULL,
    calorias INT DEFAULT 0,
    proteinas_g DECIMAL(6,1) DEFAULT 0,
    carbohidratos_g DECIMAL(6,1) DEFAULT 0,
    grasas_g DECIMAL(6,1) DEFAULT 0,
    orden INT DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- =============================================
-- Campos de objetivos de macros en el perfil
-- =============================================
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS proteinas_objetivo DECIMAL(6,1) DEFAULT 0;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS carbohidratos_objetivo DECIMAL(6,1) DEFAULT 0;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS grasas_objetivo DECIMAL(6,1) DEFAULT 0;
