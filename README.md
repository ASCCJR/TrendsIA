# TrendsIA — P0: comparador de registros de reunião

Aplicação de terminal para quem precisa conferir suas anotações contra a
transcrição ou registro automático de uma reunião antes de usar as informações.
Compara **valores, quantidades e prazos** e mostra trechos das duas fontes para
conferência humana. Nenhuma fonte é considerada automaticamente correta.

Projeto individual da Capacitação em Agentes de IA — TrendsIA, do Núcleo Softex
Campinas. Estado: primeiro fluxo local em desenvolvimento; sem entrega final.

## Funcionamento e justificativa

O programa recebe dois textos e faz uma solicitação ao modelo
`openai/gpt-oss-120b`, hospedado na Groq. A resposta é uma tabela textual com
divergências, equivalências, informações presentes em apenas uma fonte e
situações inconclusivas.

O uso de LLM é investigado para associar assuntos escritos de maneiras diferentes
e distinguir propostas de decisões. Conferência manual e busca de números são
alternativas simples; a primeira execução não demonstra superioridade geral.

## Instalação

Ambiente usado nesta etapa: Linux/WSL, **Python 3.12.14** e `uv` 0.12.9.
Dependências diretas: `httpx` 0.28.1 (HTTP) e `python-dotenv` 1.2.4 (.env).
As versões resolvidas estão em [requirements.txt](requirements.txt).

Com Python 3.12 e uv já disponíveis, execute na raiz:

```bash
uv venv --python python3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Alternativa com Python 3.12, venv e pip instalados (ainda não validada nesta etapa):

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Configuração

Copie `.env.example` para `.env` se ainda não tiver o arquivo local:

```bash
cp -n .env.example .env
```

Preencha `GROQ_API_KEY` com sua chave e mantenha `GROQ_MODEL=openai/gpt-oss-120b`.
Variáveis já definidas no ambiente têm precedência sobre o arquivo. A chave
nunca deve ser publicada. O `.env` e a `.venv` são ignorados pelo Git.

Criação e uso da chave: [documentação da Groq](https://console.groq.com/docs/quickstart).
Plano, disponibilidade e [limites](https://console.groq.com/docs/rate-limits)
devem ser conferidos na conta usada por cada pessoa. O script não altera o plano.

## Execução

```bash
.venv/bin/python comparador.py
```

Cole suas anotações e escreva `FIM` numa linha separada. Depois faça o mesmo
com o registro automático. Cada execução válida envia ambos os textos à Groq.

Para executar o exemplo fictício já preparado:

```bash
.venv/bin/python comparador.py < exemplos/entrada.txt
```

Esse exemplo compara R$ 15 mil com R$ 50 mil, 20 participantes com vinte pessoas,
dois prazos diferentes e uma duração presente em apenas uma fonte. A resposta
observada está em [primeira execução](evidencias/primeira-execucao.md).

## Verificação atual

A chamada com o exemplo foi **real**, usando a API Groq; não foi uma resposta
simulada. Para repeti-la, use o comando acima (consome cota do serviço).

Também foi verificada a sintaxe localmente, sem chamada à API:

```bash
.venv/bin/python -m py_compile comparador.py
```

Ainda não há suíte de testes automatizados. Os casos simulados de falha,
a avaliação dos seis cenários planejados e a validação final em ambiente limpo
serão acrescentados durante a evolução do projeto. Criar a primeira `.venv`
de desenvolvimento não equivale à validação final de reprodução.

## Estrutura

- `comparador.py`: entrada, instruções de comparação e chamada HTTP.
- `requirements.in` / `requirements.txt`: dependências diretas e versões resolvidas.
- `.env.example`: nomes das variáveis, sem chave real.
- `exemplos/entrada.txt`: dois registros fictícios terminados por FIM.
- `evidencias/primeira-execucao.md`: resultado e limites do primeiro teste real.

## Limites conhecidos

- Até 6.000 caracteres somando as duas entradas; somente textos curtos.
- Nesta versão, limite de geração de 1.800 tokens e timeout HTTP de 45 segundos,
  definidos no código; parâmetros serão revisados nos próximos marcos.
- A aplicação usa recursos específicos do GPT-OSS (esforço de raciocínio baixo).
  Trocar apenas o nome do modelo pode exigir ajustes na chamada.
- A saída textual ainda não é validada automaticamente contra as fontes.
  O primeiro resultado incluiu negrito nos trechos e uma linha extra sem dados.
- O modelo pode inventar, omitir ou associar informações incorretamente; conferir
  as fontes antes de agir. Concordância não comprova a veracidade da reunião.
- Sem áudio, integração com reuniões, edição automática de fontes ou envio de ações.
- O script não grava textos/respostas em logs. Use material fictício ou autorizado
  para transmissão ao provedor; o exemplo publicado é inteiramente fictício.

Relatório final, vídeo e marcações dos três níveis ainda não estão disponíveis.
