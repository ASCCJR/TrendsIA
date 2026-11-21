# Primeira execução real — 05/11/2026

Entrada: [exemplo fictício](../exemplos/entrada.txt). Provedor: Groq.
Modelo solicitado: `openai/gpt-oss-120b`. Python 3.12.14, Linux/WSL.
Comando: `.venv/bin/python comparador.py < exemplos/entrada.txt`.
Processo finalizou com código 0; chamada real, sem simulação. Nenhuma credencial
foi incluída no conteúdo enviado ao modelo ou neste registro (autenticação no
cabeçalho HTTP). Este arquivo foi preparado após a execução, com assistência
do Codex; o programa não grava entradas/respostas automaticamente.

## Resultado esperado antes da execução

- Divergências de orçamento (15 mil / 50 mil) e data (12/11 / 20/11/2026).
- Equivalência de participantes (20 / vinte).
- Duração de duas horas presente somente nas anotações.
- Trechos fiéis às fontes; não declarar uma fonte correta.

## Resposta recebida

**Comparação de trechos (valores, quantidades e prazos)**

| Assunto | Trecho das anotações | Trecho do registro automático | Classificação | Ponto para conferir |
|---|---|---|---|---|
| Orçamento do piloto | “Orçamento aprovado do piloto: **R$ 15 mil**.” | “O orçamento aprovado do piloto é de **R$ 50 mil**.” | **Divergente** | Valor monetário aprovado |
| Número de participantes | “O piloto terá **20 participantes**.” | “Vinte pessoas participarão do piloto.” | **Compatível** | Quantidade de participantes |
| Data de entrega | “Entrega em **12/11/2026**.” | “Entrega em **20/11/2026**.” | **Divergente** | Data prevista de entrega |
| Duração do treinamento | “Treinamento com duração de **2 horas**.” | – (não mencionado) | **Só nas anotações** | Informação presente apenas nas anotações |
| (Informação extra) | – | – | – | Não há outros trechos comparáveis. |

*Observação:* A concordância entre os registros não comprova a veracidade dos valores, quantidades ou prazos; apenas indica se as informações são consistentes ou não entre as duas fontes.

## Análise inicial com assistência de IA

As quatro relações esperadas apareceram e os valores foram preservados. A
resposta não escolheu qual orçamento ou data era verdadeiro.

Limitações reais: os trechos ganharam marcações de negrito, portanto não são
cópias literais exatas como solicitado. Houve também uma linha extra sem
informação, fora das classificações pedidas. Ainda não existe validador da saída.

Uma execução não mede acurácia, confiabilidade geral ou vantagem sobre regras
simples. Não foram testados aqui assuntos diferentes com o mesmo número,
proposta versus decisão, prazos relativos ou falhas de autenticação/comunicação.
Não houve medição de consumo/custo nem inspeção do plano/cotas no painel.
Revisão do aluno sobre código, decisões e resultado ainda pendente.
