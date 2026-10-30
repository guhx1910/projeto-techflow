from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox
import bcrypt

from utils.cnn import conectar


class TelaCadastro(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi("views/cadastro.ui", self)

        self.txt_senha.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Password
        )

        self.txt_confirmar.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Password
        )

        self.btn_cadastrar.clicked.connect(
            self.cadastrar_usuario
        )

    def cadastrar_usuario(self):

        nome = self.txt_nome.text().strip()
        login = self.txt_login.text().strip()
        senha = self.txt_senha.text()
        confirmar = self.txt_confirmar.text()

        if not nome or not login or not senha or not confirmar:
            QMessageBox.warning(
                self,
                "Aviso",
                "Preencha todos os campos."
            )
            return

        if senha != confirmar:
            QMessageBox.warning(
                self,
                "Aviso",
                "As senhas não coincidem."
            )
            return

        try:

            conexao = conectar()
            cursor = conexao.cursor()

            sql = """
                SELECT id_usuarios
                FROM usuarios
                WHERE login = %s
            """

            cursor.execute(sql, (login,))

            if cursor.fetchone():

                QMessageBox.warning(
                    self,
                    "Aviso",
                    "Login já cadastrado."
                )

                cursor.close()
                conexao.close()

                return

            senha_hash = bcrypt.hashpw(
                senha.encode("utf-8"),
                bcrypt.gensalt()
            )

            sql = """
                INSERT INTO usuarios
                (
                    nome,
                    login,
                    senha
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
            """

            cursor.execute(
                sql,
                (
                    nome,
                    login,
                    senha_hash.decode("utf-8")
                )
            )

            conexao.commit()

            cursor.close()
            conexao.close()

            QMessageBox.information(
                self,
                "Sucesso",
                "Usuário cadastrado com sucesso!"
            )

            # Abre a tela de login
            self.login = QtWidgets.QWidget()
            uic.loadUi("views/login.ui", self.login)

            self.login.show()
            self.close()

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro)
            )