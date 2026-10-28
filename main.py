
# Importa a classe responsável pelos dados e pela otimização.
from model import DietaModel

# Importa a classe responsável pela interface com o usuário.
from view import DietaView

# Importa a classe responsável por controlar o funcionamento.
from controller import DietaController


# Verifica se este arquivo está sendo executado diretamente.
# Isso evita iniciar o programa automaticamente caso ele
# seja importado por outro módulo.
if __name__ == "__main__":

    # Cria o objeto que carregará os dados e resolverá a dieta.
    modelo = DietaModel()

    # Cria o objeto que exibirá o menu e os resultados.
    visao = DietaView()

    # Cria o Controller e entrega a ele o Model e a View.
    # Assim, o Controller pode coordenar as duas classes.
    controlador = DietaController(modelo, visao)

    # Inicia o fluxo principal do programa.
    controlador.executar()
