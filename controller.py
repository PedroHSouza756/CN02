
# Define a classe responsável por coordenar o Model e a View.
class DietaController:

    # Recebe os objetos do Model e da View.
    def __init__(self, model, view):

        # Guarda a referência ao Model.
        # Será utilizado para carregar dados e resolver a otimização.
        self.model = model

        # Guarda a referência à View.
        # Será utilizada para interagir com o usuário.
        self.view = view

    # Executa o fluxo principal do programa.
    def executar(self):

        # Mantém o programa em execução até que o usuário saia.
        while True:

            # Trata erros que possam ocorrer durante a execução.
            try:

                # Solicita ao usuário a opção desejada no menu.
                escolha = self.view.solicitar_modo()

                # Se a opção for 3, encerra o programa.
                if escolha == "3":

                    # Exibe uma mensagem de encerramento.
                    print("\nEncerrando o programa. Até logo!")

                    # Interrompe o laço principal.
                    break

                # Ativa o modo inteiro se a opção escolhida for 2.
                # Para a opção 1, utiliza o modo fracionário.
                modo_inteiro = (escolha == "2")

                # Solicita ao Model que resolva o problema da dieta.
                # Recebe o status e os dados da solução.
                status, resultado = self.model.resolver(
                    modo_inteiro=modo_inteiro
                )

                # Envia o status e o resultado para a View exibir.
                self.view.exibir_resultado(status, resultado)

            # Captura erros conhecidos relacionados aos arquivos,
            # aos valores informados e à inicialização do solver.
            except (
                FileNotFoundError,
                ValueError,
                RuntimeError
            ) as erro:

                # Encaminha a mensagem de erro para a View.
                self.view.exibir_erro(str(erro))
