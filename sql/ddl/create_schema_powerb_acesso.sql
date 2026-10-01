------criação de schema para os acessos powerbi------
create schema if not exists powerbi_acesso;

------------criação da tabela dimensão d_usuario-------------

CREATE TABLE powerbi_acesso.d_usuario (
	id_usuario serial4 NOT NULL,
	email_usuario varchar(255) NOT NULL,
	Entidade varchar(30) NULL,
	CONSTRAINT d_usuario_email_usuario_key UNIQUE (email_usuario),
	CONSTRAINT d_usuario_pkey PRIMARY KEY (id_usuario)
);

-----Tabela Fato: Acessos agregados------

create table if not exists powerbi_acesso.f_acessos_powerbi(
	id_fato SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES powerbi_acesso.d_usuario(id_usuario),
    report_opens INT,
    total_page_views INT,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-----------criação da coluna de siglas para campos, escola e união----------

alter table powerbi_acesso.d_usuario 
add column nivel_acesso varchar(30);
