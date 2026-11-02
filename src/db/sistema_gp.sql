CREATE DATABASE IF NOT EXISTS sistema_gp;
USE sistema_gp;

CREATE TABLE IF NOT EXISTS tipousuario (id_tipousuario INT AUTO_INCREMENT PRIMARY KEY, descricao VARCHAR(20) NOT NULL);

CREATE TABLE IF NOT EXISTS usuario (id_usuario INT AUTO_INCREMENT PRIMARY KEY, id_tipousuario INT NOT NULL, nome VARCHAR(100), FOREIGN KEY (id_tipousuario) REFERENCES tipousuario(id_tipousuario));

CREATE TABLE IF NOT EXISTS escuderia (id_escuderia INT AUTO_INCREMENT PRIMARY KEY, id_mentor INT NOT NULL, nome_escuderia VARCHAR(100) NOT NULL, turma VARCHAR(20) NOT NULL, curso VARCHAR(100) NULL, etapa VARCHAR(50) NULL, periodo VARCHAR(50) NULL, escola VARCHAR(150) NULL, FOREIGN KEY (id_mentor) REFERENCES usuario(id_usuario));

CREATE TABLE IF NOT EXISTS criterio (id_criterio INT AUTO_INCREMENT PRIMARY KEY, descricao VARCHAR(250) NOT NULL, peso DECIMAL(3,2) NOT NULL DEFAULT 0.25);

CREATE TABLE IF NOT EXISTS avaliacao (id_avaliacao INT AUTO_INCREMENT PRIMARY KEY, id_escuderia INT NOT NULL, id_avaliador INT NOT NULL, id_criterio INT NOT NULL, nota DECIMAL(4,2) NOT NULL, comentario TEXT NULL, UNIQUE(id_escuderia, id_avaliador, id_criterio), FOREIGN KEY (id_escuderia) REFERENCES escuderia(id_escuderia), FOREIGN KEY (id_avaliador) REFERENCES usuario(id_usuario), FOREIGN KEY (id_criterio) REFERENCES criterio(id_criterio));

CREATE TABLE IF NOT EXISTS divulgacao (id_divulgacao INT AUTO_INCREMENT PRIMARY KEY, mostrar_resultado BOOLEAN NOT NULL DEFAULT FALSE, data_divulgacao DATETIME NOT NULL);

CREATE TABLE IF NOT EXISTS resultado (id_resultado INT AUTO_INCREMENT PRIMARY KEY, id_escuderia INT NOT NULL, id_divulgacao INT NOT NULL, nota_final DECIMAL(4,2) NOT NULL, FOREIGN KEY (id_escuderia) REFERENCES escuderia(id_escuderia), FOREIGN KEY (id_divulgacao) REFERENCES divulgacao(id_divulgacao), UNIQUE(id_escuderia, id_divulgacao));

SELECT id_escuderia, AVG(nota) as nota_final FROM avaliacao GROUP BY id_escuderia;
