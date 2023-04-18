CREATE TABLE tabela_csv (
    id INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    arquivo_csv LONGBLOB NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
                            );

CREATE TABLE usuarios (
    id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE tabela_csv MODIFY arquivo_csv LONGBLOB;