# Dossiê Didático de Auditoria - Gerdau S.A. - 2025

**Nome:** GUILHERME VITOR ESPINDOLA ALVES PEREIRA  
**Matrícula:** 190108169  
Entrega acadêmica

Trabalho da disciplina Auditoria 1, CCA0024, Turma 02, Universidade de Brasília. Este repositório contém a entrega final completa e autossuficiente.

## Conteúdo

* `01\_dossie`: dossiê único em DOCX e PDF, com os 27 PTs, seis programas, fontes e conclusão integrada.
* `02\_base\_sintetica`: base de 500.000 bens, amostra PPS e registro das exceções.
* `03\_codigo`: geração e análise reproduzíveis.
* `04\_planilhas`: cálculos de materialidade, riscos, analíticos, amostragem, estimativas e controles finais.
* `05\_fontes`: cadastro consolidado das fontes.
* `06\_evidencias\_publicas`: demonstrações financeiras anuais de 2025, comparativos, notas e relatório do auditor.
* `07\_resultados`: resultados dos testes automatizados.

## Reprodução

```bash
python -m pip install -r 03\_codigo/requirements.txt
cd 02\_base\_sintetica
python ../03\_codigo/gerar\_base\_imobilizado.py
```

Semente: `20251025`. A saída principal possui 500.000 linhas e concilia a R$ 30.640.833.000.

## Avisos

Todos os dados analíticos são sintéticos. Não foram realizadas entrevistas, inspeções, confirmações ou acessos internos. Modelos de cartas não devem ser enviados. O dossiê não constitui auditoria profissional independente e não emite opinião.

