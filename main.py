import mysql.connector
from tabulate import tabulate

cursor = None
conexao = None

try:
    # Estabelecendo a conexão com o banco de dados
    conexao = mysql.connector.connect(
        host='localhost',
        user='USER',
        password= 'PASSWORD',
        database='mydb'
    )

    cursor = conexao.cursor()

    def create():
        try:
            product_name = input("Insira o nome do produto: ")
            category = input("Insira a categoria do produto: ")
            price = float(input("Insira o preço do produto: "))
            units_in_stock = int(input("Insira o número de unidades: "))
            stock_entry_date = input("Insira a data de adição ao estoque (YYYY-MM-DD): ")

            comando = "INSERT INTO product_gen (product_name, category, price, units_in_stock, stock_entry_date) VALUES (%s, %s, %s, %s, %s)"
            valores = (product_name, category, price, units_in_stock, stock_entry_date)
            cursor.execute(comando, valores)
            conexao.commit()  # edita o banco de dados
            print("Produto criado!")
        except ValueError as err:
            print(f"Erro de Valor: {err}")
        except Exception as error:
            print(f"Erro de Valor: {error}")

    def update():
        try:
            product_id = int(input("Insira o ID do produto que deseja atualizar: "))
            # Obtendo o nome do produto
            cursor.execute("SELECT product_name FROM product_gen WHERE product_id = %s", (product_id,))
            produto = cursor.fetchone()
            if produto is None:
                print("Não há produtos com este ID!")
                return

            product_name = produto[0]

            print(f"Produto encontrado: {product_name}")
            new_price = float(input("Insira o novo preço do produto: "))
            new_quantity = int(input("Insira a nova quantidade em estoque: "))

            comando = 'UPDATE product_gen SET price = %s, units_in_stock = %s WHERE product_id = %s'
            valores = (new_price, new_quantity, product_id)
            cursor.execute(comando, valores)
            conexao.commit()
            print("Produto atualizado!")
        except ValueError as err:
            print(f"Erro de Valor: {err}")
        except Exception as error:
            print(f"Erro de Valor: {error}")

    def delete():
        try:
            product_id = int(input("Insira o ID do produto que deseja deletar: "))
            # Obtendo o nome do produto para exibir na confirmação
            cursor.execute("SELECT product_name FROM product_gen WHERE product_id = %s", (product_id,))
            produto = cursor.fetchone()

            if produto is None:
                print("Não há produtos com este ID!")
                return

            product_name = produto[0]  # Obtém o nome do produto

            confirmar = input(f"Produto encontrado: {product_name}\n"
                              "Deseja mesmo deletar este produto? Esta ação é irreversível. (SIM/NAO)").upper()
            if confirmar == 'SIM':
                comando = f'DELETE FROM product_gen WHERE product_id = %s'
                cursor.execute(comando, (product_id,))
                conexao.commit()
                print("Produto deletado com sucesso.")
            elif confirmar == 'NAO':
                print("Ação cancelada. Nenhum produto foi deletado.")
                return # Retorna ao menu
            else:
                print('Resposta inválida. Por favor responda com "SIM" ou "NAO".\n'
                      'Nenhum produto foi deletado.')
                return
        except ValueError as err:
            print(f"Erro de Valor: {err}")
        except Exception as error:
            print(f"Erro de Valor: {error}")

    def read():
        try:
            filtro = int(input("Classificar por:\n"
                               "1. Ordem alfabética\n"
                               "2. Categoria\n"
                               "3. Preço\n"
                               "4. Unidades em Estoque\n"
                               "5. Data de Adição\n"
                               "6. Todos os produtos\n"))

            if filtro == 6:
                comando = 'SELECT * FROM product_gen'
            else:
                ordem = input("1. Ordem Crescente\n"
                              "2. Ordem Decrescente\n")

            if filtro == 1:
                comando = f'SELECT * FROM product_gen ORDER BY product_name {"ASC" if ordem == "1" else "DESC"}'
            elif filtro == 2:
                comando = f'SELECT * FROM product_gen ORDER BY category {"ASC" if ordem == "1" else "DESC"}'
            elif filtro == 3:
                comando = f'SELECT * FROM product_gen ORDER BY price {"ASC" if ordem == "1" else "DESC"}'
            elif filtro == 4:
                comando = f'SELECT * FROM product_gen ORDER BY units_in_stock {"ASC" if ordem == "1" else "DESC"}'
            elif filtro == 5:
                comando = f'SELECT * FROM product_gen ORDER BY stock_entry_date {"ASC" if ordem == "1" else "DESC"}'

            cursor.execute(comando)
            resultado = cursor.fetchall()
            # Formatação e imprimindo
            header = ["ID", "Nome do Produto", "Categoria", "Preço", "Unidades em Estoque", "Data de Entrada"]
            resultado_formatado = tabulate(resultado, headers=header, tablefmt="pretty")
            print(resultado_formatado)
        except ValueError as err:
            print(f"Erro de Valor: {err}")
        except Exception as error:
            print(f"Erro de Valor: {error}")

    def relatorio():
        while True:
            try:
                tipo = int(input("Selecione o tipo de relatório: \n"
                                 "1. Baixa quantidade em estoque\n"
                                 "2. Adicionados recentemente\n"
                                 "3. Fora de estoque\n"
                                 "4. Mais caros\n"
                                 "5. Mais baratos\n"
                                 "6. Voltar ao menu\n"
                                 "-> "))

                if tipo == 6:
                    return

                comandos = {
                    1: 'SELECT * FROM product_gen WHERE units_in_stock < 10 ORDER BY units_in_stock',
                    2: 'SELECT * FROM product_gen WHERE stock_entry_date BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE() ORDER BY stock_entry_date DESC',
                    3: 'SELECT * FROM product_gen WHERE units_in_stock = 0 ORDER BY product_name',
                    4: 'SELECT * FROM product_gen WHERE price >= (SELECT AVG(price) FROM product_gen) ORDER BY price DESC',
                    5: 'SELECT * FROM product_gen WHERE price <= (SELECT AVG(price) FROM product_gen) ORDER BY price DESC'
                }

                if tipo in comandos:
                    comando = comandos[tipo]
                    cursor.execute(comando)
                    resultado = cursor.fetchall()

                    if resultado:
                        header = ["ID", "Nome do Produto", "Categoria", "Preço", "Unidades em Estoque", "Data de Entrada"]
                        resultado_formatado = tabulate(resultado, headers=header, tablefmt="pretty")
                        print(resultado_formatado)
                    else:
                        avisos = {
                            1: "Não há produtos com baixa quantidade em estoque.",
                            2: "Não há produtos adicionados recentemente.",
                            3: "Não há produtos fora de estoque."
                        }
                        print(avisos[tipo])
                else:
                    print("Opção inválida! Tente novamente.")

            except ValueError as err:
                print(f"Erro de Valor: {err}")
            except Exception as error:
                print(f"Erro de Valor: {error}")

    def main():
        while True:
            print("---------- MENU -----------")
            try:
                menu = int(input("Selecione a opção desejada: \n"
                                 "1. Criar novo produto \n"
                                 "2. Atualizar produto \n"
                                 "3. Deletar produto \n"
                                 "4. Exibir tabela \n"
                                 "5. Gerar relatório\n"
                                 "6. Encerrar Programa\n"
                                 "-> "))

                if menu == 1:
                    create()
                elif menu == 2:
                    update()
                elif menu == 3:
                    delete()
                elif menu == 4:
                    read()
                elif menu == 5:
                    relatorio()
                elif menu == 6:
                    print("Programa encerrado.")
                    break
                else:
                    print("Opção inválida! Tente novamente.")
            except ValueError as err:
                print(f"Erro de Valor: {err}")
            except Exception as error:
                print(f"Erro de Valor: {error}")
    main()

except mysql.connector.Error as erro:
    print(f"Erro ao conectar ou executar operações no banco de dados: {erro}")
except Exception as err:
    print(f"Erro: {err}")

finally:
    # Fechando o cursor e a conexão
    if cursor:
        cursor.close()
    if conexao:
        conexao.close()