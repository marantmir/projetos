# Prompt Estruturado para Relatórios HTML Responsivos e Prontos para PDF

Use este prompt como base para gerar relatórios técnicos em HTML no mesmo padrão do projeto.

## Prompt

```text
Crie um relatório técnico em HTML, em português do Brasil, com estrutura profissional, visual limpa e foco em leitura no navegador e impressão em PDF.

Objetivo do relatório:
[descrever objetivo]

Dados de entrada:
[descrever arquivos, métricas, tabelas, gráficos e contexto]

O relatório deve seguir estas regras:

1. Formato geral
- Saída final em HTML completo (`<!DOCTYPE html> ... </html>`)
- Documento com `<head>`, `<meta charset="utf-8">` e `<meta name="viewport">`
- CSS embutido no próprio HTML
- Estrutura com cabeçalho principal e seções bem separadas

2. Qualidade visual
- Layout centralizado com largura máxima confortável para leitura
- Cards ou blocos para resumo executivo
- Tabelas bem formatadas, com cabeçalhos destacados
- Figuras com legenda
- Hierarquia clara de títulos (`h1`, `h2`, `h3`)

3. Responsividade
- O documento deve funcionar bem em desktop e mobile
- Em telas menores, reduzir paddings e ajustar títulos
- Tabelas devem poder rolar horizontalmente sem quebrar o layout
- Gráficos e imagens devem ocupar largura total disponível sem distorção

4. Impressão em PDF
- Incluir regras `@media print`
- Evitar quebra de página dentro de seções, tabelas, figuras e blocos de métricas
- Ajustar margens para impressão em A4
- Remover efeitos visuais desnecessários na impressão, como sombras fortes
- Garantir que tabelas e imagens não sejam cortadas

5. Conteúdo obrigatório
- Visão geral
- Tabelas com dados principais
- Gráficos incorporados com `<img>`
- Insights ou interpretação dos resultados
- Conclusão final

6. Estilo de escrita
- Texto objetivo
- Tom técnico, claro e direto
- Explicações curtas para cada seção
- Nada de conteúdo genérico ou filler

7. Entrega esperada
- HTML pronto para salvar em arquivo `.html`
- Estrutura compatível com abertura em navegador
- Adequado para exportar como PDF pelo navegador sem quebrar layout

Monte o relatório com base nestas informações:
[inserir conteúdo específico]
```

## Uso recomendado

- preencher o objetivo do relatório
- informar quais tabelas e gráficos precisam aparecer
- incluir os insights já calculados
- pedir que a saída final seja somente o HTML

## Observação

Se quiser manter consistência com este projeto, reaproveite o mesmo padrão de:

- cabeçalho com destaque
- seções em cards
- tabelas dentro de container com scroll horizontal
- `@media print` para exportação em PDF
