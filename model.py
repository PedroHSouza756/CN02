
# Importa a biblioteca para ler arquivos CSV.
import csv

# Importa Path para manipular caminhos de arquivos e pastas.
from pathlib import Path

# Importa as ferramentas de programação linear e inteira do OR-Tools.
from ortools.linear_solver import pywraplp


# Define a classe que representa os dados e as regras da dieta.
class DietaModel:

    # Inicializa os caminhos dos arquivos e as listas de dados.
    def __init__(self):

        # Obtém o caminho absoluto da pasta onde este arquivo está.
        self.pasta = Path(__file__).resolve().parent

        # Define a pasta que contém os arquivos CSV.
        self.pasta_dados = self.pasta / "data"

        # Define o caminho do arquivo com os nutrientes mínimos.
        self.arquivo_nutrientes = self.pasta_dados / "nutrientes.csv"

        # Define o caminho do arquivo com os alimentos e seus valores.
        self.arquivo_alimentos = self.pasta_dados / "data.csv"

        # Inicializa a lista que armazenará os nutrientes.
        self.nutrientes = []

        # Inicializa a lista que armazenará os alimentos.
        self.alimentos = []

        # Armazena os nomes das colunas do arquivo de nutrientes.
        self.colunas_nutrientes = []

        # Armazena os nomes das colunas do arquivo de alimentos.
        self.colunas_alimentos = []

    # Lê um arquivo CSV e retorna seus cabeçalhos e suas linhas.
    def _ler_csv(self, caminho):

        # Verifica se o arquivo existe no caminho informado.
        if not caminho.exists():

            # Interrompe a execução com uma mensagem explicativa.
            raise FileNotFoundError(
                f"Ficheiro não encontrado: {caminho}\n"
                "Verifique se 'nutrientes.csv' e 'data.csv' "
                "estão dentro da pasta 'data'."
            )

        # Abre o arquivo em modo de leitura.
        # utf-8-sig também trata arquivos que possuem BOM.
        # newline="" evita problemas com quebras de linha no CSV.
        with caminho.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as ficheiro:

            # Cria um leitor que associa os valores aos nomes das colunas.
            leitor = csv.DictReader(ficheiro)

            # Verifica se o arquivo possui cabeçalhos.
            if not leitor.fieldnames:
                raise ValueError(
                    f"O ficheiro {caminho.name} "
                    "está vazio ou sem cabeçalho."
                )

            # Retorna os cabeçalhos e todas as linhas do arquivo.
            return leitor.fieldnames, list(leitor)

    # Converte um valor para número decimal.
    # O contexto identifica o campo caso ocorra um erro.
    def _numero(self, valor, contexto):

        try:

            # Converte o valor para texto, remove espaços
            # e substitui vírgula decimal por ponto.
            return float(str(valor).strip().replace(",", "."))

        # Captura valores que não podem ser convertidos para float.
        except (TypeError, ValueError):

            # Informa qual campo contém o valor inválido.
            raise ValueError(
                f"Valor numérico inválido em {contexto}: {valor!r}"
            )

    # Carrega e valida os dados dos dois arquivos CSV.
    def carregar_dados(self):

        # Lê os cabeçalhos e os registros de nutrientes.
        self.colunas_nutrientes, self.nutrientes = (
            self._ler_csv(self.arquivo_nutrientes)
        )

        # Lê os cabeçalhos e os registros de alimentos.
        self.colunas_alimentos, self.alimentos = (
            self._ler_csv(self.arquivo_alimentos)
        )

        # Impede a execução caso não existam nutrientes cadastrados.
        if not self.nutrientes:
            raise ValueError(
                "O ficheiro nutrientes.csv não contém nutrientes."
            )

        # Impede a execução caso não existam alimentos cadastrados.
        if not self.alimentos:
            raise ValueError(
                "O ficheiro data.csv não contém alimentos."
            )

        # Confere se o CSV de nutrientes possui as colunas necessárias.
        if (
            "nome" not in self.colunas_nutrientes
            or "minimo" not in self.colunas_nutrientes
        ):
            raise ValueError(
                "nutrientes.csv precisa de ter as colunas "
                "'nome' e 'minimo'."
            )

        # Confere se o CSV de alimentos possui as colunas básicas.
        if not {
            "ingrediente", "quantidade", "preco"
        }.issubset(self.colunas_alimentos):

            raise ValueError(
                "data.csv precisa de ter as colunas "
                "'ingrediente', 'quantidade' e 'preco'."
            )

        # Extrai os nomes dos nutrientes e remove espaços externos.
        nomes_nutrientes = [
            linha["nome"].strip()
            for linha in self.nutrientes
        ]

        # Identifica nutrientes que não possuem coluna correspondente
        # no arquivo de alimentos.
        faltantes = [
            nome
            for nome in nomes_nutrientes
            if nome not in self.colunas_alimentos
        ]

        # Se algum nutriente estiver ausente, interrompe a execução.
        if faltantes:
            raise ValueError(
                "Estas colunas de nutrientes estão em "
                "nutrientes.csv, mas não em data.csv: "
                f"{', '.join(faltantes)}"
            )

    # Resolve o problema de otimização da dieta.
    # modo_inteiro=True utiliza quantidades inteiras.
    # modo_inteiro=False permite quantidades fracionárias.
    def resolver(self, modo_inteiro=False):

        # Carrega e valida os dados antes de criar o modelo matemático.
        self.carregar_dados()

        # Escolhe o solver de acordo com o modo selecionado.
        # CBC trabalha com programação inteira.
        # GLOP resolve problemas de programação linear contínua.
        solver_nome = "CBC" if modo_inteiro else "GLOP"

        # Cria o solver solicitado.
        solver = pywraplp.Solver.CreateSolver(solver_nome)

        # Verifica se o solver foi criado corretamente.
        if solver is None:
            raise RuntimeError(
                f"Não foi possível iniciar o solver "
                f"{solver_nome} do OR-Tools."
            )

        # Lista que armazenará a variável de decisão de cada alimento.
        variaveis = []

        # Cria uma variável de decisão para cada alimento disponível.
        for i, alimento in enumerate(self.alimentos):

            # Converte o preço do alimento para número.
            preco = self._numero(
                alimento["preco"],
                f"preço de {alimento['ingrediente']}"
            )

            # Impede a utilização de preços negativos.
            if preco < 0:
                raise ValueError(
                    f"O preço de {alimento['ingrediente']} "
                    "não pode ser negativo."
                )

            # Se o usuário escolheu quantidades inteiras...
            if modo_inteiro:

                # Cria uma variável inteira não negativa.
                # x representa a quantidade do alimento.
                x = solver.IntVar(
                    0,
                    solver.infinity(),
                    f"x_{i}"
                )

                # Cria uma variável binária:
                # y = 0 significa que o alimento não foi selecionado.
                # y = 1 significa que o alimento foi selecionado.
                y = solver.BoolVar(f"selecionado_{i}")

                # Se y for zero, x também deverá ser zero.
                # O limite superior de 1.000.000 é uma constante grande
                # usada para relacionar a quantidade à seleção.
                solver.Add(x <= 1000000 * y)

                # Se y for um, x deverá ser pelo menos uma unidade.
                # Isso impede selecionar um alimento com quantidade zero.
                solver.Add(x >= y)

                # Armazena a variável de quantidade.
                variaveis.append(x)

            else:

                # Cria uma variável contínua não negativa.
                # Permite quantidades como 0.5, 1.25 ou 2.75.
                x = solver.NumVar(
                    0.0,
                    solver.infinity(),
                    f"x_{i}"
                )

                # Armazena a variável de quantidade fracionária.
                variaveis.append(x)

        # Cria uma restrição para cada nutriente obrigatório.
        for j, nutriente in enumerate(self.nutrientes):

            # Obtém o nome do nutriente.
            nome = nutriente["nome"].strip()

            # Converte a quantidade mínima exigida para número.
            minimo = self._numero(
                nutriente["minimo"],
                f"mínimo de {nome}"
            )

            # Cria a restrição:
            # quantidade total do nutriente >= mínimo exigido.
            restricao = solver.Constraint(
                minimo,
                solver.infinity(),
                f"nutriente_{j}"
            )

            # Percorre todos os alimentos para adicionar
            # a contribuição de cada um para esse nutriente.
            for i, alimento in enumerate(self.alimentos):

                # Obtém a quantidade do nutriente presente
                # em uma unidade de referência do alimento.
                quantidade_nutriente = self._numero(
                    alimento[nome],
                    f"{nome} do ingrediente "
                    f"{alimento['ingrediente']}"
                )

                # Define o coeficiente da variável na restrição.
                # Exemplo: se um alimento fornece 10 unidades
                # do nutriente, seu coeficiente será 10.
                restricao.SetCoefficient(
                    variaveis[i],
                    quantidade_nutriente
                )

        # Cria a função objetivo que calculará o custo da dieta.
        objetivo = solver.Objective()

        # Adiciona o preço de cada alimento à função objetivo.
        for i, alimento in enumerate(self.alimentos):

            # O coeficiente representa o custo de cada unidade
            # da variável de decisão correspondente.
            objetivo.SetCoefficient(
                variaveis[i],
                self._numero(
                    alimento["preco"],
                    f"preço de {alimento['ingrediente']}"
                )
            )

        # Define que o objetivo é minimizar o custo total.
        objetivo.SetMinimization()

        # Executa o solver para encontrar a solução.
        status = solver.Solve()

        # Prepara a estrutura que armazenará os resultados.
        resultado = {
            # Custo total inicial.
            "custo_total": 0.0,

            # Lista de alimentos utilizados na solução.
            "selecionados": [],

            # Lista para conferência dos nutrientes.
            "conferencia": []
        }

        # Processa os valores quando a solução é ótima.
        if status == pywraplp.Solver.OPTIMAL:

            # Obtém o valor mínimo encontrado pela função objetivo.
            resultado["custo_total"] = objetivo.Value()

            # Percorre os alimentos e recupera suas quantidades.
            for i, alimento in enumerate(self.alimentos):

                # Obtém a quantidade calculada pelo solver.
                val = variaveis[i].solution_value()

                # Trata a quantidade conforme o modo escolhido.
                if modo_inteiro:

                    # Arredonda o resultado para um número inteiro.
                    quantidade = int(round(val))

                    # Considera selecionado quando há pelo menos uma unidade.
                    condicao = quantidade >= 1

                else:

                    # Mantém o valor decimal calculado pelo solver.
                    quantidade = val

                    # Ignora valores praticamente iguais a zero,
                    # evitando exibir quantidades residuais muito pequenas.
                    condicao = quantidade > 1e-7

                # Adiciona à lista somente os alimentos selecionados.
                if condicao:

                    # Calcula o custo individual do alimento.
                    custo = (
                        quantidade
                        * self._numero(alimento["preco"], "preço")
                    )

                    # Armazena os dados necessários para a View.
                    resultado["selecionados"].append({
                        # Nome do alimento.
                        "ingrediente": alimento["ingrediente"],

                        # Quantidade utilizada na dieta.
                        "quantidade": quantidade,

                        # Unidade ou quantidade de referência do CSV.
                        "unidade_base": alimento["quantidade"],

                        # Custo correspondente à quantidade utilizada.
                        "custo": custo,

                        # Informa se foi utilizado o modo inteiro.
                        "modo_inteiro": modo_inteiro
                    })

            # Calcula o total de cada nutriente na solução encontrada.
            for nutriente in self.nutrientes:

                # Obtém o nome do nutriente.
                nome = nutriente["nome"].strip()

                # Soma a contribuição de todos os alimentos.
                # Cada contribuição é a quantidade utilizada
                # multiplicada pelo teor do nutriente no alimento.
                total = sum(
                    variaveis[i].solution_value()
                    * self._numero(
                        alimento[nome],
                        f"{nome} do ingrediente "
                        f"{alimento['ingrediente']}"
                    )
                    for i, alimento in enumerate(self.alimentos)
                )

                # Recupera o mínimo exigido para esse nutriente.
                minimo = self._numero(
                    nutriente["minimo"],
                    f"mínimo de {nome}"
                )

                # Guarda o total calculado e o mínimo exigido.
                resultado["conferencia"].append({
                    "nome": nome,
                    "total": total,
                    "minimo": minimo
                })

        # Retorna o status da execução e os resultados calculados.
        # A View utilizará esses dados para exibir a solução.
        return status, resultado
