
# Importa a biblioteca de expressões regulares para manipular textos.
import re

# Importa as constantes de status dos solvers do OR-Tools.
from ortools.linear_solver import pywraplp


# Define a classe responsável pela interface do programa.
class DietaView:

    # Exibe o menu e solicita ao usuário o modo de otimização.
    def solicitar_modo(self):

        # Repete o menu até que o usuário informe uma opção válida.
        while True:

            # Exibe o título e as opções do menu.
            print("\n" + "=" * 55)
            print("             OTIMIZADOR DE DIETA - MENU             ")
            print("=" * 55)
            print(" [1] Quantidades Fracionadas (ex: 1.5) [Solver: GLOP]")
            print(" [2] Quantidades Inteiras   (ex: 1, 2)  [Solver: CBC]")
            print(" [3] Sair")
            print("-" * 55)

            # Lê a opção digitada e remove espaços desnecessários.
            escolha = input(
                " Digite o número da opção desejada (1, 2 ou 3): "
            ).strip()

            # Verifica se a opção digitada é válida.
            if escolha in ("1", "2", "3"):

                # Retorna a opção para o Controller.
                return escolha

            # Informa que a opção digitada não é válida.
            print("\n[Erro] Opção inválida! Por favor, digite 1, 2 ou 3.")

    # Exibe os resultados da otimização recebidos do Model.
    # O parâmetro status informa o resultado do solver.
    # O parâmetro resultado contém os dados calculados.
    def exibir_resultado(self, status, resultado):

        # Imprime uma linha para organizar a apresentação.
        print("\n" + "=" * 55)

        # Verifica se o solver encontrou a solução ótima.
        if status == pywraplp.Solver.OPTIMAL:

            # Exibe o título e o custo mínimo da dieta.
            print("                 RESULTADO DA DIETA                  ")
            print("=" * 55)
            print(f" Custo Mínimo Total: R$ {resultado['custo_total']:.2f}")
            print("-" * 55)
            print(" ALIMENTOS SELECIONADOS:")

            # Verifica se a lista de alimentos selecionados está vazia.
            if not resultado["selecionados"]:

                # Informa que nenhum alimento foi selecionado.
                print("   (Nenhum alimento selecionado)")

            else:

                # Percorre todos os alimentos utilizados na solução.
                for item in resultado["selecionados"]:

                    # No modo inteiro, exibe a quantidade sem casas decimais.
                    # No modo fracionado, exibe quatro casas decimais.
                    qtd_str = (
                        f"{item['quantidade']}"
                        if item["modo_inteiro"]
                        else f"{item['quantidade']:.4f}"
                    )

                    # Remove caracteres iniciais indesejados da unidade.
                    # Exemplo: transforma "1 lb." em "lb.".
                    unidade_limpa = re.sub(
                        r"^[\d\.\/\s]+",
                        "",
                        item["unidade_base"]
                    ).strip()

                    # Se a limpeza remover todo o texto,
                    # utiliza a unidade original como alternativa.
                    if not unidade_limpa:
                        unidade_limpa = item["unidade_base"]

                    # Exibe o nome, a quantidade, a unidade e o custo.
                    print(
                        f" • {item['ingrediente']:<22} | "
                        f"{qtd_str:>6} {unidade_limpa:<8} | "
                        f"R$ {item['custo']:.2f}"
                    )

            # Inicia a seção de conferência dos nutrientes.
            print("-" * 55)
            print(" CONFERÊNCIA DE NUTRIENTES:")

            # Percorre os nutrientes calculados pelo Model.
            for conf in resultado["conferencia"]:

                # Compara o total encontrado com o mínimo exigido.
                # Exibe OK se atingir o mínimo ou BAIXO caso contrário.
                status_nutri = (
                    "OK"
                    if conf["total"] >= conf["minimo"]
                    else "BAIXO"
                )

                # Mostra o nome, o total, o mínimo e o status.
                print(
                    f" • {conf['nome']:<18} | "
                    f"Total: {conf['total']:>8.4f} | "
                    f"Mín: {conf['minimo']:>8.4f} [{status_nutri}]"
                )

            # Finaliza a apresentação da solução ótima.
            print("=" * 55)

        # Verifica se existe uma solução viável,
        # mas sem garantia de que seja a melhor solução.
        elif status == pywraplp.Solver.FEASIBLE:
            print(
                " Solução viável encontrada "
                "(sem garantia de otimização máxima)."
            )

        # Informa que as restrições não podem ser satisfeitas.
        elif status == pywraplp.Solver.INFEASIBLE:
            print(
                " [Erro] Não existe solução que satisfaça "
                "todas as restrições."
            )

        # Informa que o problema possui uma solução ilimitada.
        elif status == pywraplp.Solver.UNBOUNDED:
            print(
                " [Erro] O problema está ilimitado; "
                "verifique os dados."
            )

        # Trata outros status que não foram reconhecidos.
        else:
            print(
                " [Erro] O solver não conseguiu "
                "encontrar uma solução."
            )

        # Fecha o quadro de resultados.
        print("=" * 55)

    # Exibe mensagens de erro recebidas do Controller.
    def exibir_erro(self, mensagem):

        # Imprime uma linha de destaque antes da mensagem.
        print("\n" + "!" * 55)

        # Exibe a descrição do erro.
        print(f" ERRO: {mensagem}")

        # Imprime uma linha de destaque após a mensagem.
        print("!" * 55)
