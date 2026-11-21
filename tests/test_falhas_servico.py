import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import httpx

from comparador import API_URL, main


class TestFalhasServico(unittest.TestCase):
    def setUp(self):
        self.entrada = (Path(__file__).parents[1] / "exemplos" / "entrada.txt").read_text(encoding="utf-8")
        self.requisicao = httpx.Request("POST", API_URL)

    def executar(self, resposta=None, erro=None):
        saida, erros = StringIO(), StringIO()
        with (
            patch.dict("os.environ", {"GROQ_API_KEY": "chave-ficticia", "GROQ_MODEL": "modelo-ficticio"}, clear=True),
            patch("comparador.load_dotenv"),
            patch("sys.stdin", StringIO(self.entrada)),
            patch("comparador.httpx.post", return_value=resposta, side_effect=erro) as post,
            redirect_stdout(saida),
            redirect_stderr(erros),
        ):
            codigo = main()
        post.assert_called_once()
        return codigo, saida.getvalue(), erros.getvalue()

    def conferir_falha(self, resultado, mensagem):
        codigo, saida, erros = resultado
        self.assertEqual(codigo, 1)
        self.assertIn(mensagem, erros)
        self.assertNotIn("Comparação sugerida pela IA", saida)
        self.assertNotIn("chave-ficticia", saida + erros)

    def test_servico_indisponivel_orienta_tentar_mais_tarde(self):
        resposta = httpx.Response(503, request=self.requisicao)
        self.conferir_falha(self.executar(resposta=resposta), "HTTP 503). Tente novamente mais tarde.")

    def test_falha_de_conexao_orienta_conferir_a_conexao(self):
        erro = httpx.ConnectError("falha induzida", request=self.requisicao)
        self.conferir_falha(self.executar(erro=erro), "Confira a conexão e tente novamente.")

    def test_timeout_identifica_tempo_limite(self):
        erro = httpx.ReadTimeout("tempo esgotado induzido", request=self.requisicao)
        self.conferir_falha(self.executar(erro=erro), "excedeu o tempo limite")

    def test_credencial_e_modelo_invalidos_preservam_status(self):
        for status in (401, 404):
            with self.subTest(status=status):
                resposta = httpx.Response(status, request=self.requisicao)
                self.conferir_falha(self.executar(resposta=resposta), f"A Groq recusou a solicitação (HTTP {status}).")

    def test_resposta_sem_texto_exibe_aviso(self):
        for conteudo in ("", "   ", None):
            with self.subTest(conteudo=conteudo):
                resposta = httpx.Response(
                    200,
                    request=self.requisicao,
                    json={"choices": [{"message": {"content": conteudo}}]},
                )
                self.conferir_falha(
                    self.executar(resposta=resposta), "O serviço não retornou uma comparação textual."
                )

    def test_resposta_com_estrutura_inesperada_exibe_aviso(self):
        for dados in ({}, {"choices": []}, {"choices": [None]}, {"choices": [{"message": {}}]}):
            with self.subTest(dados=dados):
                resposta = httpx.Response(200, request=self.requisicao, json=dados)
                self.conferir_falha(
                    self.executar(resposta=resposta), "O serviço retornou uma estrutura inesperada."
                )

    def test_corpo_vazio_ou_sem_json_exibe_aviso(self):
        for corpo in (b"", b"<html>Resposta inesperada</html>"):
            with self.subTest(corpo=corpo):
                resposta = httpx.Response(200, request=self.requisicao, content=corpo)
                self.conferir_falha(self.executar(resposta=resposta), "Resposta inválida do serviço.")

    def test_sucesso_exibe_a_comparacao(self):
        resposta = httpx.Response(
            200,
            request=self.requisicao,
            json={"choices": [{"message": {"content": "Comparação fictícia."}}]},
        )
        codigo, saida, erros = self.executar(resposta=resposta)
        self.assertEqual(codigo, 0)
        self.assertIn("Comparação sugerida pela IA", saida)
        self.assertIn("Comparação fictícia.", saida)
        self.assertEqual(erros, "")
