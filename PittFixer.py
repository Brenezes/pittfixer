# PittFixer - Ferramenta para correção de dimensionamento de pits
# Descrição: Este código ajusta os valores de 'prof', 'compr' e 'larg' em eventos
#            que atendem a critérios específicos, salvando os valores originais
#            no campo 'comentario'.
# Autor: [Breno Menezes]
# Versão: 1.0

import sqlite3
import random
import csv

# Gerar valores #
def gerar_valores_aleatorios():
    prof = random.randint(10, 19)  # 10 < X < 19 #
    compr = random.randint(10, 15)  # 10 < X < 15 #
    larg = random.randint(10, 15)  # 10 < X < 15 #
    
    while compr == larg:
        larg = random.randint(10, 15)
    return prof, compr, larg
    
# Exportar log CSV #
def exportar_relatorio(eventos_corrigidos, nome_arquivo="log_pitfixer.csv"):
    with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        # Cabeçalho #
        writer.writerow(["ID", "Tipo Original", "Prof Original", "Compr Original", "Larg Original", 
                         "Tipo Novo", "Prof Novo", "Compr Novo", "Larg Novo", "posAxi", "Comentário"])
        # Grava dados #
        for evento in eventos_corrigidos:
            writer.writerow(evento)
    print(f"Relatório exportado para {nome_arquivo}")    
    
# Solicita o nome do banco de dados ao analista #
nome_banco = input("Digite o nome do banco de dados (com extensão .prdb): ")

# Conecta ao banco #
try:
    conn = sqlite3.connect(nome_banco)
    cursor = conn.cursor()

    # Consulta os eventos #
    # Neste caso onde 'tipo' contém '*' e ('larg' < 9 OU 'compr' < 9) #
    cursor.execute('''
    SELECT id, prof, compr, larg, tipo, posAxi FROM catadef
    WHERE tipo LIKE '%*%' AND (larg < 9 OR compr < 9)
    ''')

    # Recupera todos os resultados #
    eventos = cursor.fetchall()

    # Se houver eventos, atualiza as colunas #
    if eventos:
        print("Eventos encontrados. Atualizando...")
        eventos_corrigidos = []  # Armazena IDs dos eventos corrigidos #
        for evento in eventos:
            id_evento, prof_original, compr_original, larg_original, tipo_original, posAxi = evento # Pega os valores originais #
            prof_novo, compr_novo, larg_novo = gerar_valores_aleatorios()  # Gera novos valores aleatórios #
            
            # Formata o campo de comentário com os valores originais #
            comentario = f"Original Prof: {prof_original} / Compr: {compr_original} / Larg: {larg_original}"
            
            # Atualiza o campo 'comentario' e as colunas 'prof', 'compr' e 'larg' #
            # Verifica se a substituição deve incluir 'larg' #
            if larg_original < 9:
                # Atualiza 'prof', 'compr' e 'larg' #
                cursor.execute('''
                UPDATE catadef
                SET prof = ?, compr = ?, larg = ?, comentario = ?
                WHERE id = ?
                ''', (prof_novo, compr_novo, larg_novo, comentario, id_evento))
            else:
                # Atualiza apenas 'prof' e 'compr' #
                cursor.execute('''
                UPDATE catadef
                SET prof = ?, compr = ?, comentario = ?
                WHERE id = ?
                ''', (prof_novo, compr_novo, comentario, id_evento))
            
            print(f"Evento ID {id_evento} atualizado:")
            print(f"  Comentário: {comentario}")
            print(f"  Novos valores: prof={prof_novo}, compr={compr_novo}, larg={larg_novo if larg_original < 9 else larg_original}")
        
	     # Adiciona os dados ao relatório #
            eventos_corrigidos.append([
                id_evento, tipo_original, prof_original, compr_original, larg_original,
                "CORR" if tipo_original in ("PM", "*PM") else 
                "COSC" if tipo_original in ("ASC", "*ASC") else 
                "ASCI" if tipo_original in ("RSC", "*RSC") else tipo_original,
                prof_novo, compr_novo, larg_novo if larg_original < 9 else larg_original, posAxi, comentario
            ])
            
            conn.commit()
            print("Alterações salvas no banco de dados.")

            
        # Atualiza os tipos "PM" e "*PM" para "CORR" #
        print("Atualizando tipos 'PM' e '*PM' para 'CORR'...")
        ids_corrigidos = ",".join(map(str, [evento[0] for evento in eventos_corrigidos]))
        cursor.execute(f'''
        UPDATE catadef
        SET tipo = 'CORR'
        WHERE (tipo = 'PM' OR tipo = '*PM')
          AND (id IN (SELECT id FROM catadef WHERE tipo NOT LIKE '%*%') OR id IN ({ids_corrigidos}))
        ''')
        
        # Atualiza os tipos "ASC" e "*ASC" para "COSC"
        print("Atualizando tipos 'ASC' e '*ASC' para 'COSC'...")
        cursor.execute(f'''
        UPDATE catadef
        SET tipo = 'COSC'
        WHERE (tipo = 'ASC' OR tipo = '*ASC')
          AND (id IN (SELECT id FROM catadef WHERE tipo NOT LIKE '%*%') OR id IN ({ids_corrigidos}))
        ''')
        
        # Atualiza os tipos "RSC" e "*RSC" para "ASCI"
        print("Atualizando tipos 'RSC' e '*RSC' para 'ASCI'...")
        cursor.execute(f'''
        UPDATE catadef
        SET tipo = 'ASCI'
        WHERE (tipo = 'RSC' OR tipo = '*RSC')
          AND (id IN (SELECT id FROM catadef WHERE tipo NOT LIKE '%*%') OR id IN ({ids_corrigidos}))
        ''')
        
        # Salva as alterações #
        conn.commit()
        print("Tipos atualizados com sucesso.")
        
        # Exporta o log #
        exportar_relatorio(eventos_corrigidos)
        
    else:
        print("Nenhum evento encontrado.")

except Exception as e:
    # Em caso de erro, desfaz as alterações #
    if conn:
        conn.rollback()
    print(f"Erro durante a execução: {e}")
    print("Alterações não salvas. Rollback realizado.")

finally:
    # Fecha a conexão com o banco de dados #
    if conn:
        conn.close()
        print("Conexão com o banco de dados fechada.")
