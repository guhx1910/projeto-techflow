from decimal import Decimal

from PyQt6.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QIntValidator
)

from PyQt6.QtWidgets import (
    QMessageBox,
    QAbstractItemView
)

from utils.cnn import conectar


class GerenciadorVendas:

    def __init__(self, tela):

        self.tela = tela

        # ==========================================================
        # VALIDAÇÃO DO CAMPO QUANTIDADE
        # ==========================================================

        # Permite somente números inteiros entre 1 e 999999.
        self.tela.edit_quantidade.setValidator(
            QIntValidator(1, 999999)
        )

        # ==========================================================
        # CONFIGURAÇÃO DA TABELA DE VENDAS
        # ==========================================================

        self.modelo = QStandardItemModel()

        self.modelo.setHorizontalHeaderLabels([
            "Código",
            "Cliente",
            "Produto",
            "Quantidade",
            "Valor Total",
            "Data da Venda"
        ])

        self.tela.tableView_vendas.setModel(
            self.modelo
        )

        # Seleciona a linha inteira.
        self.tela.tableView_vendas.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # Permite selecionar somente uma linha.
        self.tela.tableView_vendas.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # ==========================================================
        # EVENTOS DOS BOTÕES
        # ==========================================================

        self.tela.btn_registrar_venda.clicked.connect(
            self.registrar_venda
        )

        self.tela.btn_limpar_venda.clicked.connect(
            self.limpar_campos
        )

        self.tela.btn_cancelar_venda.clicked.connect(
            self.cancelar
        )

        # ==========================================================
        # EVENTOS DOS CAMPOS
        # ==========================================================

        # Quando trocar o produto, recalcula o subtotal.
        self.tela.combo_produto.currentIndexChanged.connect(
            self.atualizar_subtotal
        )

        # Quando digitar a quantidade, recalcula o subtotal.
        self.tela.edit_quantidade.textChanged.connect(
            self.atualizar_subtotal
        )

        # ==========================================================
        # CARREGAMENTO INICIAL
        # ==========================================================

        self.carregar_clientes()

        self.carregar_produtos()

        self.carregar_vendas()

        self.atualizar_totais()

        self.atualizar_subtotal()

    # ==============================================================
    # CARREGAR CLIENTES
    # ==============================================================

    def carregar_clientes(self):

        self.tela.combo_cliente.clear()

        self.tela.combo_cliente.addItem(
            "Selecione o cliente",
            None
        )

        conexao = None
        cursor = None

        try:

            conexao = conectar()

            cursor = conexao.cursor()

            sql = """
                SELECT
                    id_clientes,
                    nome
                FROM clientes
                ORDER BY nome
            """

            cursor.execute(sql)

            clientes = cursor.fetchall()

            for cliente in clientes:

                id_cliente = cliente[0]

                nome = cliente[1]

                self.tela.combo_cliente.addItem(
                    nome,
                    id_cliente
                )

        except Exception as erro:

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Erro ao carregar clientes:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # ==============================================================
    # CARREGAR PRODUTOS
    # ==============================================================

    def carregar_produtos(self):

        self.tela.combo_produto.clear()

        self.tela.combo_produto.addItem(
            "Selecione o produto",
            None
        )

        conexao = None
        cursor = None

        try:

            conexao = conectar()

            cursor = conexao.cursor()

            sql = """
                SELECT
                    id_produtos,
                    nome,
                    preco,
                    estoque
                FROM produtos
                ORDER BY nome
            """

            cursor.execute(sql)

            produtos = cursor.fetchall()

            for produto in produtos:

                id_produto = produto[0]

                nome = produto[1]

                preco = Decimal(
                    str(produto[2])
                )

                estoque = int(
                    produto[3]
                )

                # Dados internos do produto.
                dados_produto = {
                    "id": id_produto,
                    "nome": nome,
                    "preco": preco,
                    "estoque": estoque
                }

                # Texto exibido no ComboBox.
                texto = (
                    f"{nome} - "
                    f"R$ {preco:.2f} - "
                    f"Estoque: {estoque}"
                )

                texto = texto.replace(
                    ".",
                    ","
                )

                self.tela.combo_produto.addItem(
                    texto,
                    dados_produto
                )

        except Exception as erro:

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Erro ao carregar produtos:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # ==============================================================
    # ATUALIZAR SUBTOTAL
    # ==============================================================

    def atualizar_subtotal(self):

        produto = (
            self.tela.combo_produto.currentData()
        )

        quantidade_texto = (
            self.tela.edit_quantidade.text().strip()
        )

        # ----------------------------------------------------------
        # PRODUTO NÃO SELECIONADO
        # ----------------------------------------------------------

        if produto is None:

            self.tela.subtotal_vendas.setText(
                "R$ 0,00"
            )

            return

        # ----------------------------------------------------------
        # QUANTIDADE VAZIA
        # ----------------------------------------------------------

        if not quantidade_texto:

            self.tela.subtotal_vendas.setText(
                "R$ 0,00"
            )

            return

        # ----------------------------------------------------------
        # CONVERTE QUANTIDADE
        # ----------------------------------------------------------

        try:

            quantidade = int(
                quantidade_texto
            )

        except ValueError:

            self.tela.subtotal_vendas.setText(
                "R$ 0,00"
            )

            return

        # ----------------------------------------------------------
        # QUANTIDADE PRECISA SER MAIOR QUE ZERO
        # ----------------------------------------------------------

        if quantidade <= 0:

            self.tela.subtotal_vendas.setText(
                "R$ 0,00"
            )

            return

        # ----------------------------------------------------------
        # BUSCA PREÇO
        # ----------------------------------------------------------

        preco = Decimal(
            str(produto["preco"])
        )

        # ----------------------------------------------------------
        # CALCULA VALOR TOTAL
        # ----------------------------------------------------------

        valor_total = (
            preco * quantidade
        )

        # ----------------------------------------------------------
        # FORMATA EM R$
        # ----------------------------------------------------------

        valor_formatado = (
            f"R$ {valor_total:.2f}"
        )

        valor_formatado = (
            valor_formatado.replace(
                ".",
                ","
            )
        )

        # ----------------------------------------------------------
        # MOSTRA NA TELA
        # ----------------------------------------------------------

        self.tela.subtotal_vendas.setText(
            valor_formatado
        )

    # ==============================================================
    # REGISTRAR VENDA
    # ==============================================================

    def registrar_venda(self):

        # ----------------------------------------------------------
        # CLIENTE
        # ----------------------------------------------------------

        id_cliente = (
            self.tela.combo_cliente.currentData()
        )

        if id_cliente is None:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Selecione um cliente."
            )

            return

        # ----------------------------------------------------------
        # PRODUTO
        # ----------------------------------------------------------

        produto = (
            self.tela.combo_produto.currentData()
        )

        if produto is None:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Selecione um produto."
            )

            return

        id_produto = produto["id"]

        preco = Decimal(
            str(produto["preco"])
        )

        # ==========================================================
        # QUANTIDADE
        # ==========================================================

        quantidade_texto = (
            self.tela.edit_quantidade.text().strip()
        )

        # Campo vazio.
        if not quantidade_texto:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Informe a quantidade."
            )

            self.tela.edit_quantidade.setFocus()

            return

        # Converte para inteiro.
        try:

            quantidade = int(
                quantidade_texto
            )

        except ValueError:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "A quantidade deve ser um número inteiro."
            )

            self.tela.edit_quantidade.setFocus()

            return

        # Não permite 0 ou negativo.
        if quantidade <= 0:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "A quantidade deve ser maior que zero."
            )

            self.tela.edit_quantidade.setFocus()

            return

        # ==========================================================
        # VERIFICA ESTOQUE MOSTRADO NA TELA
        # ==========================================================

        estoque = int(
            produto["estoque"]
        )

        if quantidade > estoque:

            QMessageBox.warning(
                self.tela,
                "Estoque insuficiente",
                (
                    f"Quantidade solicitada: {quantidade}\n"
                    f"Estoque disponível: {estoque}"
                )
            )

            self.tela.edit_quantidade.setFocus()

            return

        # ==========================================================
        # CALCULA VALOR DA VENDA
        # ==========================================================

        valor_total = (
            preco * quantidade
        )

        conexao = None
        cursor = None

        try:

            conexao = conectar()

            cursor = conexao.cursor()

            # ======================================================
            # ATUALIZA ESTOQUE
            # ======================================================
            #
            # O próprio banco verifica novamente se ainda existe
            # estoque suficiente.
            #
            # Isso é importante porque o estoque pode ter mudado
            # depois que o ComboBox foi carregado.
            # ======================================================

            sql_estoque = """
                UPDATE produtos

                SET estoque = estoque - %s

                WHERE id_produtos = %s

                AND estoque >= %s
            """

            cursor.execute(
                sql_estoque,
                (
                    quantidade,
                    id_produto,
                    quantidade
                )
            )

            # ------------------------------------------------------
            # ESTOQUE INSUFICIENTE
            # ------------------------------------------------------

            if cursor.rowcount == 0:

                conexao.rollback()

                QMessageBox.warning(
                    self.tela,
                    "Estoque insuficiente",
                    (
                        "Não existe estoque suficiente "
                        "para realizar esta venda."
                    )
                )

                # Atualiza os produtos.
                self.carregar_produtos()

                return

            # ======================================================
            # REGISTRAR VENDA
            # ======================================================

            sql_venda = """
                INSERT INTO vendas
                (
                    id_clientes,
                    id_produtos,
                    quantidade,
                    valor_total,
                    data_venda
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    NOW()
                )
            """

            cursor.execute(
                sql_venda,
                (
                    id_cliente,
                    id_produto,
                    quantidade,
                    valor_total
                )
            )

            # ======================================================
            # CONFIRMA VENDA + ESTOQUE
            # ======================================================

            conexao.commit()

            # ======================================================
            # MENSAGEM
            # ======================================================

            valor_formatado = (
                f"R$ {valor_total:.2f}"
                .replace(".", ",")
            )

            QMessageBox.information(
                self.tela,
                "Sucesso",
                (
                    "Venda registrada com sucesso!\n\n"
                    f"Quantidade: {quantidade}\n"
                    f"Valor total: {valor_formatado}"
                )
            )

            # ======================================================
            # ATUALIZA INTERFACE
            # ======================================================

            self.limpar_campos()

            # Atualiza estoque exibido no ComboBox.
            self.carregar_produtos()

            # Atualiza histórico.
            self.carregar_vendas()

            # Atualiza valores inferiores da tela.
            self.atualizar_totais()

        except Exception as erro:

            # Caso qualquer operação dê erro,
            # desfaz também a alteração do estoque.

            if conexao is not None:

                conexao.rollback()

            QMessageBox.critical(
                self.tela,
                "Erro",
                (
                    "Não foi possível registrar "
                    f"a venda:\n{erro}"
                )
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # ==============================================================
    # CARREGAR HISTÓRICO DE VENDAS
    # ==============================================================

    def carregar_vendas(self):

        # Limpa tabela.
        self.modelo.removeRows(
            0,
            self.modelo.rowCount()
        )

        conexao = None
        cursor = None

        try:

            conexao = conectar()

            cursor = conexao.cursor()

            sql = """
                SELECT
                    v.id_vendas,
                    c.nome,
                    p.nome,
                    v.quantidade,
                    v.valor_total,
                    v.data_venda

                FROM vendas v

                INNER JOIN clientes c
                    ON c.id_clientes = v.id_clientes

                INNER JOIN produtos p
                    ON p.id_produtos = v.id_produtos

                ORDER BY
                    v.id_vendas DESC
            """

            cursor.execute(sql)

            vendas = cursor.fetchall()

            # ======================================================
            # PREENCHE A TABELA
            # ======================================================

            for venda in vendas:

                id_venda = venda[0]

                nome_cliente = venda[1]

                nome_produto = venda[2]

                quantidade = venda[3]

                valor_total = Decimal(
                    str(venda[4])
                )

                data = venda[5]

                # --------------------------------------------------
                # FORMATA VALOR
                # --------------------------------------------------

                valor_formatado = (
                    f"R$ {valor_total:.2f}"
                )

                valor_formatado = (
                    valor_formatado.replace(
                        ".",
                        ","
                    )
                )

                # --------------------------------------------------
                # FORMATA DATA
                # --------------------------------------------------

                if hasattr(
                    data,
                    "strftime"
                ):

                    data_formatada = (
                        data.strftime(
                            "%d/%m/%Y %H:%M"
                        )
                    )

                else:

                    data_formatada = str(
                        data
                    )

                # --------------------------------------------------
                # CRIA LINHA
                # --------------------------------------------------

                linha = [

                    QStandardItem(
                        str(id_venda)
                    ),

                    QStandardItem(
                        str(nome_cliente)
                    ),

                    QStandardItem(
                        str(nome_produto)
                    ),

                    QStandardItem(
                        str(quantidade)
                    ),

                    QStandardItem(
                        valor_formatado
                    ),

                    QStandardItem(
                        data_formatada
                    )
                ]

                self.modelo.appendRow(
                    linha
                )

            # Ajusta largura das colunas.
            self.tela.tableView_vendas.resizeColumnsToContents()

        except Exception as erro:

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Erro ao carregar vendas:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # ==============================================================
    # ATUALIZAR TOTAIS
    # ==============================================================

    def atualizar_totais(self):

        conexao = None
        cursor = None

        try:

            conexao = conectar()

            cursor = conexao.cursor()

            sql = """
                SELECT

                    COALESCE(
                        SUM(valor_total),
                        0
                    ),

                    COALESCE(
                        SUM(quantidade),
                        0
                    )

                FROM vendas
            """

            cursor.execute(sql)

            resultado = cursor.fetchone()

            valor_total = resultado[0]

            total_itens = resultado[1]

            # ------------------------------------------------------
            # FORMATA TOTAL
            # ------------------------------------------------------

            valor_formatado = (
                f"R$ {Decimal(str(valor_total)):.2f}"
            )

            valor_formatado = (
                valor_formatado.replace(
                    ".",
                    ","
                )
            )

            # ------------------------------------------------------
            # TOTAL FINANCEIRO
            # ------------------------------------------------------

            self.tela.total_vendas.setText(
                valor_formatado
            )

            # ------------------------------------------------------
            # QUANTIDADE TOTAL VENDIDA
            # ------------------------------------------------------

            self.tela.qtd_itens.setText(
                str(int(total_itens))
            )

        except Exception as erro:

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Erro ao atualizar totais:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # ==============================================================
    # LIMPAR CAMPOS
    # ==============================================================

    def limpar_campos(self):

        # ----------------------------------------------------------
        # CLIENTE
        # ----------------------------------------------------------

        if self.tela.combo_cliente.count() > 0:

            self.tela.combo_cliente.setCurrentIndex(
                0
            )

        # ----------------------------------------------------------
        # PRODUTO
        # ----------------------------------------------------------

        if self.tela.combo_produto.count() > 0:

            self.tela.combo_produto.setCurrentIndex(
                0
            )

        # ----------------------------------------------------------
        # QUANTIDADE
        # ----------------------------------------------------------

        self.tela.edit_quantidade.clear()

        # ----------------------------------------------------------
        # LIMPA SELEÇÃO DA TABELA
        # ----------------------------------------------------------

        self.tela.tableView_vendas.clearSelection()

        # ----------------------------------------------------------
        # ZERA VALOR
        # ----------------------------------------------------------

        self.tela.subtotal_vendas.setText(
            "R$ 0,00"
        )

    # ==============================================================
    # CANCELAR
    # ==============================================================

    def cancelar(self):

        # Limpa todos os campos.
        self.limpar_campos()

        # Volta para a página inicial.
        self.tela.conteudo_principal.setCurrentIndex(
            0
        )