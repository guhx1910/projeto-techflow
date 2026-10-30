from decimal import Decimal, InvalidOperation

from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMessageBox, QAbstractItemView

from utils.cnn import conectar


class GerenciadorProdutos:
    def __init__(self, tela):
        self.tela = tela

        # ============================================================
        # CONFIGURAÇÃO DA TABELA
        # ============================================================

        self.modelo = QStandardItemModel()

        self.modelo.setHorizontalHeaderLabels(
            [
                "Código",
                "Nome",
                "Descrição",
                "Categoria",
                "Preço",
                "Estoque"
            ]
        )

        self.tela.tableView_2.setModel(self.modelo)

        # Seleciona a linha inteira
        self.tela.tableView_2.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # Permite selecionar apenas uma linha
        self.tela.tableView_2.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # ============================================================
        # CONEXÃO DOS BOTÕES
        # ============================================================

        self.tela.btn_salvar_produto.clicked.connect(
            self.salvar_produto
        )

        self.tela.btn_limpar_produto.clicked.connect(
            self.limpar_campos
        )

        self.tela.btn_excluir_produto.clicked.connect(
            self.excluir_produto
        )

        # Duplo clique na tabela para editar um produto
        self.tela.tableView_2.doubleClicked.connect(
            self.carregar_campos_ao_duplo_clique
        )

        # Carrega os produtos ao iniciar
        self.carregar_dados_na_tabela()

    # ================================================================
    # CARREGAR PRODUTOS
    # ================================================================

    def carregar_dados_na_tabela(self):
        """
        Busca os produtos no banco de dados
        e mostra no tableView_2.
        """

        # Limpa os registros existentes no modelo
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
                    id_produtos,
                    nome,
                    descricao,
                    categoria,
                    preco,
                    estoque
                FROM produtos
                ORDER BY id_produtos
            """

            cursor.execute(sql)

            produtos = cursor.fetchall()

            # Adiciona cada produto na tabela
            for produto in produtos:

                # Formata o preço com duas casas decimais
                if produto[4] is None:
                    preco = ""
                else:
                    preco = f"{Decimal(str(produto[4])):.2f}"

                linha = [
                    QStandardItem(
                        str(produto[0] or "")
                    ),

                    QStandardItem(
                        str(produto[1] or "")
                    ),

                    QStandardItem(
                        str(produto[2] or "")
                    ),

                    QStandardItem(
                        str(produto[3] or "")
                    ),

                    QStandardItem(
                        preco
                    ),

                    QStandardItem(
                        str(
                            produto[5]
                            if produto[5] is not None
                            else ""
                        )
                    ),
                ]

                self.modelo.appendRow(linha)

            # Ajusta automaticamente o tamanho das colunas
            self.tela.tableView_2.resizeColumnsToContents()

        except Exception as erro:

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Erro ao carregar produtos do banco:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # ================================================================
    # SALVAR / ALTERAR PRODUTO
    # ================================================================

    def salvar_produto(self):
        """
        Se o campo código estiver vazio:
            cadastra um novo produto.

        Se o código possuir valor:
            atualiza o produto existente.
        """

        # ------------------------------------------------------------
        # PEGA OS VALORES DOS CAMPOS
        # ------------------------------------------------------------

        codigo_texto = (
            self.tela.edit_codigo_produto
            .text()
            .strip()
        )

        nome = (
            self.tela.edit_nome_produto
            .text()
            .strip()
        )

        descricao = (
            self.tela.edit_descricao_produto
            .text()
            .strip()
        )

        categoria = (
            self.tela.comboBox
            .currentText()
            .strip()
        )

        preco_texto = (
            self.tela.edit_preco_produto
            .text()
            .strip()
        )

        estoque_texto = (
            self.tela.edit_estoque_produto
            .text()
            .strip()
        )

        # ------------------------------------------------------------
        # VALIDAÇÃO DO NOME
        # ------------------------------------------------------------

        if not nome:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha o nome do produto."
            )

            return

        # ------------------------------------------------------------
        # VALIDAÇÃO DA DESCRIÇÃO
        # ------------------------------------------------------------

        if not descricao:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha a descrição do produto."
            )

            return

        # ------------------------------------------------------------
        # VALIDAÇÃO DA CATEGORIA
        # ------------------------------------------------------------

        if not categoria:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Selecione a categoria do produto."
            )

            return

        # ------------------------------------------------------------
        # VALIDAÇÃO DO PREÇO
        # ------------------------------------------------------------

        if not preco_texto:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha o preço do produto."
            )

            return

        # ------------------------------------------------------------
        # VALIDAÇÃO DO ESTOQUE
        # ------------------------------------------------------------

        if not estoque_texto:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha o estoque do produto."
            )

            return

        # ------------------------------------------------------------
        # CONVERSÃO DO PREÇO
        # ------------------------------------------------------------

        try:

            # Aceita:
            #
            # 59.90
            # 59,90
            # R$ 59,90

            preco_formatado = (
                preco_texto
                .replace("R$", "")
                .replace(" ", "")
                .replace(",", ".")
            )

            preco = Decimal(preco_formatado)

            if preco < 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preço inválido.\n\n"
                "Digite, por exemplo:\n"
                "59,90\n"
                "ou\n"
                "59.90"
            )

            return

        # DECIMAL(10,2)
        #
        # máximo:
        # 99.999.999,99

        if preco > Decimal("99999999.99"):

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "O preço excede o limite "
                "do campo DECIMAL(10,2)."
            )

            return

        # ------------------------------------------------------------
        # CONVERSÃO DO ESTOQUE
        # ------------------------------------------------------------

        try:

            estoque = int(estoque_texto)

            if estoque < 0:
                raise ValueError

        except ValueError:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Estoque inválido.\n\n"
                "Digite um número inteiro "
                "maior ou igual a zero."
            )

            return

        # ------------------------------------------------------------
        # ABRE CONEXÃO
        # ------------------------------------------------------------

        conexao = None
        cursor = None

        try:

            conexao = conectar()

            cursor = conexao.cursor()

            # ========================================================
            # UPDATE
            # ========================================================

            if codigo_texto:

                sql = """
                    UPDATE produtos
                    SET
                        nome = %s,
                        descricao = %s,
                        categoria = %s,
                        preco = %s,
                        estoque = %s
                    WHERE id_produtos = %s
                """

                cursor.execute(
                    sql,
                    (
                        nome,
                        descricao,
                        categoria,
                        preco,
                        estoque,
                        int(codigo_texto)
                    )
                )

                if cursor.rowcount == 0:

                    mensagem = (
                        "Nenhuma alteração foi realizada."
                    )

                else:

                    mensagem = (
                        "Produto atualizado com sucesso!"
                    )

            # ========================================================
            # INSERT
            # ========================================================

            else:

                sql = """
                    INSERT INTO produtos
                    (
                        nome,
                        descricao,
                        categoria,
                        preco,
                        estoque
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """

                cursor.execute(
                    sql,
                    (
                        nome,
                        descricao,
                        categoria,
                        preco,
                        estoque
                    )
                )

                mensagem = (
                    "Produto cadastrado com sucesso!"
                )

            # Confirma a alteração no banco
            conexao.commit()

            QMessageBox.information(
                self.tela,
                "Sucesso",
                mensagem
            )

            # Limpa formulário
            self.limpar_campos()

            # Atualiza tabela
            self.carregar_dados_na_tabela()

        except Exception as erro:

            # Desfaz a operação se ocorrer algum problema
            if conexao is not None:
                conexao.rollback()

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Não foi possível salvar o produto:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # ================================================================
    # CARREGAR PRODUTO PARA EDIÇÃO
    # ================================================================

    def carregar_campos_ao_duplo_clique(self, index):
        """
        Ao dar dois cliques em uma linha da tabela,
        carrega os dados nos campos para edição.
        """

        linha = index.row()

        # Função auxiliar para buscar
        # texto de determinada coluna
        def texto(coluna):

            item = self.modelo.item(
                linha,
                coluna
            )

            if item:
                return item.text()

            return ""

        # ------------------------------------------------------------
        # CÓDIGO
        # ------------------------------------------------------------

        self.tela.edit_codigo_produto.setText(
            texto(0)
        )

        # ------------------------------------------------------------
        # NOME
        # ------------------------------------------------------------

        self.tela.edit_nome_produto.setText(
            texto(1)
        )

        # ------------------------------------------------------------
        # DESCRIÇÃO
        # ------------------------------------------------------------

        self.tela.edit_descricao_produto.setText(
            texto(2)
        )

        # ------------------------------------------------------------
        # CATEGORIA
        # ------------------------------------------------------------

        categoria = texto(3)

        indice_categoria = (
            self.tela.comboBox.findText(
                categoria
            )
        )

        # Se a categoria está no ComboBox
        if indice_categoria >= 0:

            self.tela.comboBox.setCurrentIndex(
                indice_categoria
            )

        # Caso exista no banco,
        # mas não exista mais no ComboBox
        elif categoria:

            self.tela.comboBox.addItem(
                categoria
            )

            self.tela.comboBox.setCurrentIndex(
                self.tela.comboBox.count() - 1
            )

        # ------------------------------------------------------------
        # PREÇO
        # ------------------------------------------------------------

        # Converte 59.90 para 59,90
        # apenas para exibição no formulário

        self.tela.edit_preco_produto.setText(
            texto(4).replace(".", ",")
        )

        # ------------------------------------------------------------
        # ESTOQUE
        # ------------------------------------------------------------

        self.tela.edit_estoque_produto.setText(
            texto(5)
        )

    # ================================================================
    # EXCLUIR PRODUTO
    # ================================================================

    def excluir_produto(self):
        """
        Exclui um produto da tabela produtos.
        """

        codigo_texto = (
            self.tela.edit_codigo_produto
            .text()
            .strip()
        )

        # ------------------------------------------------------------
        # SE O PRODUTO NÃO FOI CARREGADO PELO DUPLO CLIQUE
        # TENTA PEGAR A LINHA SELECIONADA
        # ------------------------------------------------------------

        if not codigo_texto:

            linhas_selecionadas = (
                self.tela
                .tableView_2
                .selectionModel()
                .selectedRows()
            )

            if not linhas_selecionadas:

                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "Selecione um produto na tabela."
                )

                return

            linha = linhas_selecionadas[0].row()

            item_id = self.modelo.item(
                linha,
                0
            )

            if item_id is None:

                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "Não foi possível identificar "
                    "o produto."
                )

                return

            codigo_texto = item_id.text()

        # ------------------------------------------------------------
        # CONVERTE O ID
        # ------------------------------------------------------------

        try:

            id_produto = int(
                codigo_texto
            )

        except ValueError:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "O código do produto é inválido."
            )

            return

        # ------------------------------------------------------------
        # CONFIRMAÇÃO
        # ------------------------------------------------------------

        resposta = QMessageBox.question(
            self.tela,
            "Confirmar exclusão",
            (
                "Deseja realmente excluir "
                f"o produto de código {id_produto}?"
            ),
            (
                QMessageBox.StandardButton.Yes
                |
                QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No
        )

        if (
            resposta
            != QMessageBox.StandardButton.Yes
        ):
            return

        # ------------------------------------------------------------
        # DELETE NO BANCO
        # ------------------------------------------------------------

        conexao = None
        cursor = None

        try:

            conexao = conectar()

            cursor = conexao.cursor()

            sql = """
                DELETE FROM produtos
                WHERE id_produtos = %s
            """

            cursor.execute(
                sql,
                (id_produto,)
            )

            conexao.commit()

            # --------------------------------------------------------
            # VERIFICA SE ALGUM REGISTRO FOI EXCLUÍDO
            # --------------------------------------------------------

            if cursor.rowcount == 0:

                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "Produto não encontrado no banco."
                )

            else:

                QMessageBox.information(
                    self.tela,
                    "Sucesso",
                    "Produto excluído com sucesso!"
                )

            # Limpa os campos
            self.limpar_campos()

            # Atualiza tabela
            self.carregar_dados_na_tabela()

        except Exception as erro:

            if conexao is not None:
                conexao.rollback()

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Não foi possível excluir o produto:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # ================================================================
    # LIMPAR CAMPOS
    # ================================================================

    def limpar_campos(self):
        """
        Limpa todos os campos do cadastro de produtos.
        """

        self.tela.edit_codigo_produto.clear()

        self.tela.edit_nome_produto.clear()

        self.tela.edit_descricao_produto.clear()

        self.tela.edit_preco_produto.clear()

        self.tela.edit_estoque_produto.clear()

        # Volta o ComboBox para a primeira opção
        if self.tela.comboBox.count() > 0:

            self.tela.comboBox.setCurrentIndex(0)

        # Remove seleção da tabela
        self.tela.tableView_2.clearSelection()