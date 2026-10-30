import sys
import bcrypt
from PyQt6 import QtWidgets, uic

from src.dashboard import TelaDashboard
from src.cadastro import TelaCadastro
from utils.cnn import conectar


class TelaLogin(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi("views/login.ui", self)

        self.btn_entrar.clicked.connect(
            self.verificar_login
        )

        self.btn_criarconta.clicked.connect(
            self.tela_cadastro
        )

    def tela_cadastro(self):
        self.nova_tela = TelaCadastro()
        self.nova_tela.show()
        self.close()

    def verificar_login(self):

        usuario_digitado = self.txt_usuario.text().strip()
        senha_digitada = self.txt_senha.text()
        
        try:

            conexao = conectar()
            cursor = conexao.cursor()

            sql = """
                SELECT senha
                FROM usuarios
                WHERE login = %s
            """

            cursor.execute(sql, (usuario_digitado,))

            resultado = cursor.fetchone()



            cursor.close()
            conexao.close()

            if resultado:

                senha_banco = resultado[0]

                if bcrypt.checkpw(senha_digitada.encode("utf-8"),senha_banco.encode("utf-8")):
                    self.nova_tela = TelaDashboard()
                    self.nova_tela.show()
                    self.close()

                else:

                    self.lbl_mensagem.setText(
                        "Usuário ou senha incorretos."
                    )

                    self.lbl_mensagem.setStyleSheet(
                        "color: red;"
                    )

            else:

                self.lbl_mensagem.setText(
                    "Usuário ou senha incorretos."
                )

                self.lbl_mensagem.setStyleSheet(
                    "color: red;"
                )

        except Exception as erro:

            self.lbl_mensagem.setText(
                f"Erro: {erro}"
            )

            self.lbl_mensagem.setStyleSheet(
                "color: orange;"
            )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    janela = TelaLogin()
    janela.show()

    sys.exit(app.exec())