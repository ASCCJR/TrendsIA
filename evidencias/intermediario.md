# Evidências do Intermediário

## Entrada vazia bloqueada

**21/11/2026** · Python 3.12.16 · código de `p0-basico` (`0aeda90`).

O resultado esperado em cada caso era a mensagem **“Preencha os dois textos
antes de enviar.”**, encerramento com código `1` e zero chamadas HTTP.

| Caso induzido | Anotações | Registro automático | Resultado observado |
| --- | --- | --- | --- |
| Anotações vazias | `FIM` na primeira linha | Texto fictício seguido de `FIM` | Mensagem esperada, saída `1`, zero chamadas |
| Registro automático vazio | Texto fictício seguido de `FIM` | `FIM` na primeira linha | Mensagem esperada, saída `1`, zero chamadas |
| Anotações com espaços | Linha com três espaços, seguida de `FIM` | Texto fictício seguido de `FIM` | Mensagem esperada, saída `1`, zero chamadas |

Foi executado o ponto de entrada do `comparador.py` com dados fornecidos pelo
teste em `stdin`. A configuração veio de variáveis temporárias com chave
fictícia. O teste substituiu `httpx.post` por uma função que falharia em caso de
chamada e registrou quantas vezes ela foi acionada. Nos três casos, a contagem
foi zero. Este é um teste local da validação de entrada. A execução com o serviço
está documentada na [primeira chamada real](primeira-execucao.md).

Para repetir a verificação a partir da raiz, com as dependências instaladas em
`.venv`, execute:

```bash
.venv/bin/python - <<'PY'
import io
import os
from contextlib import redirect_stderr, redirect_stdout
from runpy import run_path
from unittest.mock import patch

cases = {
    "anotações vazias": "FIM\nVinte pessoas participaram do piloto.\nFIM\n",
    "registro automático vazio": "O piloto teve 20 participantes.\nFIM\nFIM\n",
    "anotações com espaços": "   \nFIM\nVinte pessoas participaram do piloto.\nFIM\n",
}
expected_message = "Preencha os dois textos antes de enviar."
test_env = {"GROQ_API_KEY": "chave-ficticia", "GROQ_MODEL": "openai/gpt-oss-120b"}

for name, text in cases.items():
    stdout, stderr = io.StringIO(), io.StringIO()
    with (
        patch.dict(os.environ, test_env),
        patch("dotenv.load_dotenv"),
        patch("sys.stdin", io.StringIO(text)),
        patch("httpx.post", side_effect=AssertionError("Chamada HTTP indevida")) as post,
        redirect_stdout(stdout),
        redirect_stderr(stderr),
    ):
        try:
            run_path("comparador.py", run_name="__main__")
        except SystemExit as error:
            code = error.code
        else:
            raise AssertionError("O comando deveria encerrar com erro.")
    assert code == 1, (name, code)
    assert stderr.getvalue().strip() == expected_message, (name, stderr.getvalue())
    assert "Comparação sugerida pela IA" not in stdout.getvalue(), name
    post.assert_not_called()
    print(f"{name} | saída {code} | {post.call_count} chamadas HTTP | {stderr.getvalue().strip()}")
PY
```

## Chave de API ausente

**21/11/2026** · Python 3.12.16 · código de `p0-basico` (`0aeda90`).

O teste iniciou o programa com o modelo configurado e a variável
`GROQ_API_KEY` ausente. A leitura do `.env` foi desativada só no processo
do teste para impedir que o arquivo local restaurasse a chave.

| Esperado | Observado |
| --- | --- |
| Mensagem de configuração e saída `1` | `Preencha GROQ_API_KEY e GROQ_MODEL no .env.`, em `stderr`, com saída `1` |
| Interrupção antes de pedir os textos e chamar a API | Saída padrão vazia. Uma execução instrumentada contou zero leituras de `input()` e zero chamadas de `httpx.post` |

Para repetir a execução do terminal a partir da raiz:

```bash
env -u GROQ_API_KEY PYTHON_DOTENV_DISABLED=1 GROQ_MODEL=openai/gpt-oss-120b \
  .venv/bin/python comparador.py </dev/null
echo "$?"
```

## Chave de API inválida

**21/11/2026** · Python 3.12.16 · código de `p0-basico` (`0aeda90`).

O teste enviou o [exemplo fictício](../exemplos/entrada.txt) pela integração
real com a Groq, usando uma chave propositalmente inválida. O processo recebeu
a chave fictícia por variável de ambiente, com a leitura do `.env` desativada.

| Esperado | Observado |
| --- | --- |
| Rejeição da autenticação pela Groq | HTTP `401` |
| Encerramento controlado, com mensagem de erro e sem revelar a chave | Saída `1` e mensagem `A Groq recusou a solicitação (HTTP 401). Confira chave, modelo e limites no painel do serviço.` |

O título “Comparação sugerida pela IA” chegou a aparecer porque a versão
testada o imprime antes da chamada. O terminal exibiu a mensagem de erro
em seguida. Esse detalhe pode ser corrigido na organização da apresentação.

Para repetir a partir da raiz:

```bash
env PYTHON_DOTENV_DISABLED=1 GROQ_API_KEY=chave-ficticia-invalida \
  GROQ_MODEL=openai/gpt-oss-120b .venv/bin/python comparador.py < exemplos/entrada.txt
echo "$?"
```

## Modelo em branco ou inexistente

**21/11/2026** · Python 3.12.16 · código de `p0-basico` (`0aeda90`).

| Caso induzido | Esperado | Observado |
| --- | --- | --- |
| `GROQ_MODEL` só com um espaço, com chave fictícia | Aviso de configuração e saída `1` antes da leitura dos textos | `Preencha GROQ_API_KEY e GROQ_MODEL no .env.`, saída `1`, zero leituras de `input()` e zero chamadas HTTP |
| `GROQ_MODEL` com identificador inexistente, com a chave local válida | Uma solicitação real à Groq, rejeição do modelo e saída `1` | Uma solicitação, HTTP `404` com código `model_not_found` na resposta da Groq e saída `1`. O comparador exibiu a mensagem com o status HTTP e orientou conferir a configuração |

O teste local interceptou `input()` e `httpx.post` para detectar qualquer
tentativa de leitura ou chamada. Na verificação com a API real, a instrumentação
observou o código devolvido pela Groq. A credencial foi lida localmente e ficou
fora da saída dos testes. A configuração de modelo foi alterada só no processo.

Para repetir os cenários a partir da raiz, use uma chave válida no `.env`
para o segundo comando:

```bash
env PYTHON_DOTENV_DISABLED=1 GROQ_API_KEY=chave-ficticia GROQ_MODEL=' ' \
  .venv/bin/python comparador.py </dev/null
echo "$?"

env -u GROQ_API_KEY -u PYTHON_DOTENV_DISABLED GROQ_MODEL=p0-modelo-inexistente-teste-21 \
  .venv/bin/python comparador.py < exemplos/entrada.txt
echo "$?"
```

## Serviço indisponível, falha de conexão e timeout

**21/11/2026** · Python 3.12.16 · versão local do Intermediário.

No código de `p0-basico`, as três falhas já encerravam com saída `1`. O
HTTP `503` orientava a conferir chave, modelo e limites. A falha de conexão
recebia o mesmo aviso do timeout. O título da comparação aparecia nos três
casos. As mensagens foram ajustadas e o título passou a aparecer após a
obtenção do resultado.

| Caso simulado | Esperado | Observado após o ajuste |
| --- | --- | --- |
| Resposta HTTP `503` | Informar a falha do serviço, sugerir tentar mais tarde e sair com `1` | Mensagem com HTTP `503` e orientação de tentar mais tarde, saída `1` |
| Erro de conexão | Orientar a conferir a conexão e sair com `1` | Mensagem de comunicação com orientação de conferir a conexão, saída `1` |
| Timeout de leitura | Informar que o tempo limite foi excedido e sair com `1` | Mensagem de tempo limite, saída `1` |

Nos três casos, o título da comparação ficou ausente. Os testes também
conferiram as mensagens de HTTP `401` e `404` e a exibição do título com
uma resposta de sucesso. Foi usado o exemplo fictício com `httpx.post`
substituído por respostas ou exceções simuladas. A suíte passou nos cinco
testes. [Código dos testes](../tests/test_falhas_servico.py)

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## Resposta vazia ou formato inesperado

**21/11/2026** · Python 3.12.16 · versão local do Intermediário.

As respostas abaixo foram simuladas com HTTP `200`. O resultado esperado em
cada caso era uma mensagem de erro adequada, saída `1` e ausência do título da
comparação. O código HTTP de sucesso permite que o programa chegue à leitura do
corpo e valide seu conteúdo.

| Caso simulado | Resultado observado após o ajuste |
| --- | --- |
| Conteúdo vazio, só com espaços ou `null` | `O serviço não retornou uma comparação textual.` e saída `1` |
| Campo `choices` ausente ou vazio, primeira opção `null` ou campo `content` ausente | `O serviço retornou uma estrutura inesperada.` e saída `1` |
| Corpo HTTP vazio ou com HTML no lugar de JSON | `Resposta inválida do serviço.` e saída `1` |

Antes do ajuste, `choices: [null]` causava `AttributeError` ao ler
`finish_reason`. A função passou a verificar se a primeira opção é um
objeto JSON antes de acessar seus campos. Com o mesmo comando acima, a suíte
passou nos oito testes, incluindo as variações de resposta e as falhas
demonstradas anteriormente. [Código dos testes](../tests/test_falhas_servico.py)

## Organização do fluxo

**21/11/2026** · Python 3.12.16 · versão local do Intermediário.

O código foi dividido por responsabilidade no mesmo arquivo. `main()`
coordena as funções e exibe o resultado ou a mensagem de erro. A configuração,
a leitura e validação dos textos, a montagem da solicitação e a interpretação
da resposta têm funções próprias. `comparar()` realiza a chamada HTTP e passa
a resposta para interpretação. [Código do comparador](../comparador.py)

Com a chamada HTTP simulada, passaram novamente os oito testes da suíte e os
três casos de entrada vazia. Uma verificação adicional confirmou o bloqueio de
configuração incompleta e de textos acima do limite, além do envio esperado
do modelo, das instruções, dos textos e da autenticação no caminho de sucesso.

## Execução real após os ajustes

**21/11/2026** · Python 3.12.16 · `openai/gpt-oss-120b` na API da Groq.

Foi repetido o [exemplo fictício](../exemplos/entrada.txt) com o código
reorganizado. A saída foi `0`. A comparação sinalizou divergência no
orçamento e na data de entrega, equivalência entre 20 e vinte participantes
e duração do treinamento presente apenas nas anotações. A saída trouxe as
quatro linhas esperadas. O modelo continuou incluindo marcação de negrito
nas citações, apesar do pedido de cópia literal.

```bash
.venv/bin/python comparador.py < exemplos/entrada.txt
```
