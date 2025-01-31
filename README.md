# PittFixer

O *PittFixer* é uma ferramenta Python para corrigir e ajustar eventos em um banco de dados SQLite. Ele atualiza valores de colunas como prof, compr, larg e tipo, além de gerar um relatório CSV com os detalhes das alterações.

## Funcionalidades ##

- Corrige eventos com * no tipo e larg < 9.
- Atualiza os tipos PM, *PM, ASC, *ASC, RSC e *RSC para CORR, COSC e ASCI, respectivamente.
- Gera um relatório CSV com os valores originais, novos valores e a coluna posAxi.

## Pré-requisitos ##

- Python 3.x instalado.
- Um banco de dados (prdb) SQLite com a tabela catadef e as colunas necessárias (id, tipo, prof, compr, larg, posAxi, comentario).

## Como Executar ##

1. *Clone o repositório* (se aplicável):
   ```bash
   git clone https://github.com/brxnvzs/pitttfixer.git
   cd pitfixer
