# PittFixer - Ferramenta para correção de pitts e manipulação de banco
# Descrição: Este código ajusta os valores de 'prof', 'compr' e 'larg' em eventos
#            que atendem a critérios específicos, salvando os valores originais
#            no campo 'comentario'.
#            Atualizado para manipulação de banco de dados.
# Autor: [Breno Menezes]
# Versão: V1.8

import sqlite3
import random
import csv
import sys
import subprocess

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
    print(f"Log exportado para {nome_arquivo}")

def correcao_padrao(caminho_banco, nome_tabela):
# Conecta ao banco #
    try:
        conn = sqlite3.connect(caminho_banco)
        cursor = conn.cursor()

        # Consulta os eventos #
        # Neste caso onde 'tipo' contém '*' e ('larg' < 9 OU 'compr' < 9) #
        cursor.execute(f'''
        SELECT id, prof, compr, larg, tipo, posAxi FROM {nome_tabela}
        WHERE tipo LIKE '%*%' AND (larg < 9 OR compr < 9)
        ''')

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
                    cursor.execute(f'''
                    UPDATE {nome_tabela}
                    SET prof = ?, compr = ?, larg = ?, comentario = ?
                    WHERE id = ?
                    ''', (prof_novo, compr_novo, larg_novo, comentario, id_evento))
                else:
                    # Atualiza apenas 'prof' e 'compr' #
                    cursor.execute(f'''
                    UPDATE {nome_tabela}
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

            
            # Atualiza os tipos #
            print("Atualizando tipos 'PM' e '*PM' para 'CORR'...")
            ids_corrigidos = ",".join(map(str, [evento[0] for evento in eventos_corrigidos]))

            for tipo_antigo, tipo_novo in [("PM", "CORR"), ("ASC", "COSC"), ("RSC", "ASCI")]:
                print(f"Atualizando tipos '{tipo_antigo}' e '*{tipo_antigo}' para '{tipo_novo}'...")
                cursor.execute(f'''
                UPDATE {nome_tabela}
                SET tipo = ?
                WHERE (tipo = ? OR tipo = ?)
                AND (id IN (SELECT id FROM {nome_tabela} WHERE tipo NOT LIKE '%*%') OR id IN ({ids_corrigidos}))
                ''', (tipo_novo, tipo_antigo, f"*{tipo_antigo}"))

            conn.commit()
            print("\nTipos atualizados com sucesso.")
            exportar_relatorio(eventos_corrigidos)

        else:
            print("\nNenhum evento encontrado.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\nErro durante a execução: {e}")
        print("Alterações não salvas. Rollback realizado.")

    finally:
        if conn:
            conn.close()
            print("\nConexão com o banco de dados fechada.")


# Função 2: Substituir valores x < 9 por 10 #
def substituir_valores_baixos(caminho_banco, nome_tabela):
    try:
        conn = sqlite3.connect(caminho_banco)
        cursor = conn.cursor()

        # Busca registros com qualquer valor <10 #
        cursor.execute(f'''
        SELECT id, prof, compr, larg, tipo, posAxi FROM {nome_tabela}
        WHERE prof < 10 OR compr < 10 OR larg < 10
        ''')

        eventos = cursor.fetchall()

        if eventos:
            print("\nEventos encontrados. Atualizando...")
            eventos_corrigidos = []
            for evento in eventos:
                id_evento, prof_original, compr_original, larg_original, tipo_original, posAxi = evento

                prof_novo = prof_original if prof_original >= 10 else 10
                compr_novo = compr_original if compr_original >= 10 else 10
                larg_novo = larg_original if larg_original >= 10 else 10

                comentario = f"Valores substituídos: Prof({prof_original}→{prof_novo}), Compr({compr_original}→{compr_novo}), Larg({larg_original}→{larg_novo})"

                # Atualiza o registro #
                cursor.execute(f'''
                UPDATE {nome_tabela}
                SET prof = ?, compr = ?, larg = ?, comentario = ?
                WHERE id = ?
                ''', (prof_novo, compr_novo, larg_novo, comentario, id_evento))

                print(f"\nEvento ID {id_evento} atualizado:")
                print(f"  Comentário: {comentario}")
                print(f"  Novos valores: prof={prof_novo}, compr={compr_novo}, larg={larg_novo}")

                eventos_corrigidos.append([
                    id_evento, tipo_original, prof_original, compr_original, larg_original,
                    tipo_original,
                    prof_novo, compr_novo, larg_novo, posAxi, comentario
                ])

            conn.commit()
            print("\nAlterações salvas no banco de dados.")
            exportar_relatorio(eventos_corrigidos, "log_substituicao.csv")

        else:
            print("\nNenhum evento menor que 10 encontrado.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\nErro durante a execução: {e}")
        print("Alterações não salvas. Rollback realizado.")

    finally:
        if conn:
            conn.close()
            print("\nConexão com o banco de dados fechada.")


# Menu interno do PittFixer #
def menu_pittfixer():
    print("\n" + "=" * 50)
    print("PITTFIXER - Ferramenta para correção de pitts e manipulação de banco\nAutor: [Breno Menezes]\nV1.8".center(50))
    print("=" * 50)

    caminho_banco = input("\nDigite o caminho completo do banco de dados: (Ex:/home/usuario/dados/corrida.prdb) ").strip()
    if not os.path.exists(caminho_banco):
        print("\nErro: Banco de dados não encontrado!")
        return

    nome_tabela = input("Digite o nome da tabela de anomalias: (Ex: catadef) ")

    while True:
        print("\nOpções:")
        print("1. Correção de Pitts (eventos com '*' e dimensões baixas)")
        print("2. Substituir valores X<10 por 10")
        print("3. Voltar ao menu principal")

        escolha = input("\nDigite a opção desejada: ")

        if escolha == "1":
            correcao_padrao(caminho_banco, nome_tabela)
        elif escolha == "2":
            substituir_valores_baixos(caminho_banco, nome_tabela)
        elif escolha == "3":
            print("\nRetornando ao menu do AnalystToolBox...")
            subprocess.Popen(['python', 'menu.py'], shell=True)
            sys.exit(0)
        else:
            print("\nOpção inválida!")

def main():
    print("\n" + "="*50)
    print("PITTFIXER V1.8 - Copyright (c) [2025] [PIPEWAY ENGENHARIA LTDA] ".center(50))
    print("="*50)
    menu_pitfixer()

if __name__ == "__main__":
    main()