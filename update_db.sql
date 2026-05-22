USE galindo_fit;

-- Agregar columna para el plan nutricional del atleta
ALTER TABLE usuarios ADD COLUMN plan_nutricional TEXT;
