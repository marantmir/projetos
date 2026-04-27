from __future__ import annotations
"""Funções utilitárias para geração de relatórios HTML do projeto."""

import html
from typing import Any

import pandas as pd


def build_structured_report(
    title: str,
    sections: list[dict[str, Any]],
    subtitle: str | None = None,
) -> str:
    """Monta um relatório HTML completo a partir de seções e blocos declarativos."""
    body = "".join(render_section(section) for section in sections)
    return _build_html_document(title=title, body=body, subtitle=subtitle)


def render_section(section: dict[str, Any]) -> str:
    """Renderiza uma seção completa do relatório."""
    title = html.escape(str(section["title"]))
    description = section.get("description")
    blocks = section.get("blocks", [])
    description_html = (
        f'<p class="muted section-description">{_render_inline_text(str(description))}</p>'
        if description
        else ""
    )
    blocks_html = "".join(render_block(block) for block in blocks)
    return (
        f"<section>"
        f"<h2>{title}</h2>"
        f"{description_html}"
        f"{blocks_html}"
        f"</section>"
    )


def render_block(block: dict[str, Any]) -> str:
    """Despacha a renderização de um bloco pelo seu tipo."""
    block_type = str(block["type"])
    header_html = _render_block_header(block)

    if block_type == "text":
        content_html = render_text_block(block)
    elif block_type == "table":
        content_html = render_table_block(block)
    elif block_type == "figure":
        content_html = render_figure_block(block)
    elif block_type == "metrics_grid":
        content_html = render_metrics_grid_block(block)
    elif block_type == "html":
        content_html = str(block.get("content", ""))
    else:
        raise ValueError(f"Tipo de bloco não suportado: {block_type}")

    return f'<div class="report-block">{header_html}{content_html}</div>'


def render_text_block(block: dict[str, Any]) -> str:
    """Renderiza bloco textual em formato parágrafo, lista ou preformatado."""
    text_format = str(block.get("format", "paragraph"))

    if text_format == "paragraph":
        paragraphs = block.get("content", [])
        if isinstance(paragraphs, str):
            paragraphs = [paragraphs]
        return "".join(f"<p>{_render_inline_text(str(paragraph))}</p>" for paragraph in paragraphs)

    if text_format == "list":
        items = block.get("items", [])
        tag = "ol" if block.get("ordered", False) else "ul"
        items_html = "".join(f"<li>{_render_inline_text(str(item))}</li>" for item in items)
        return f"<{tag}>{items_html}</{tag}>"

    if text_format == "pre":
        return f"<pre>{html.escape(str(block.get('content', '')))}</pre>"

    raise ValueError(f"Formato de texto não suportado: {text_format}")


def render_table_block(block: dict[str, Any]) -> str:
    """Renderiza uma tabela HTML estilizada a partir de um DataFrame."""
    dataframe = block.get("data")
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Bloco do tipo 'table' precisa receber um DataFrame em 'data'.")
    return _dataframe_to_html_table(dataframe)


def render_figure_block(block: dict[str, Any]) -> str:
    """Renderiza uma figura com imagem e legenda opcional."""
    src = str(block["src"])
    alt = str(block.get("alt", "Figura do relatório"))
    caption = block.get("caption")
    caption_html = f"<figcaption>{_render_inline_text(str(caption))}</figcaption>" if caption else ""
    return (
        f'<figure class="report-figure">'
        f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" />'
        f"{caption_html}"
        f"</figure>"
    )


def render_metrics_grid_block(block: dict[str, Any]) -> str:
    """Renderiza uma grade de métricas em cards."""
    items = block.get("items", [])
    cards_html = "".join(
        (
            '<div class="metric-card">'
            f"<strong>{html.escape(str(item['label']))}</strong>"
            f"<span>{_render_inline_text(str(item['value']))}</span>"
            "</div>"
        )
        for item in items
    )
    return f'<div class="metrics-grid">{cards_html}</div>'


def _render_block_header(block: dict[str, Any]) -> str:
    """Renderiza cabeçalho opcional de um bloco."""
    title = block.get("title")
    description = block.get("description")
    parts: list[str] = []

    if title:
        parts.append(f"<h3>{html.escape(str(title))}</h3>")
    if description:
        parts.append(f'<p class="muted block-description">{_render_inline_text(str(description))}</p>')

    return "".join(parts)


def _dataframe_to_html_table(df: pd.DataFrame) -> str:
    """Converte um DataFrame em uma tabela HTML estilizada."""
    table_html = df.to_html(index=False, classes="report-table", border=0)
    return f'<div class="table-wrap">{table_html}</div>'


def _render_inline_text(text: str) -> str:
    """Aplica escape HTML e suporte simples a texto entre crases como código inline."""
    parts = text.split("`")
    rendered: list[str] = []
    for index, part in enumerate(parts):
        escaped = html.escape(part)
        if index % 2 == 1:
            rendered.append(f"<code>{escaped}</code>")
        else:
            rendered.append(escaped)
    return "".join(rendered)


def _build_html_document(title: str, body: str, subtitle: str | None = None) -> str:
    """Monta o documento HTML final com o CSS compartilhado do projeto."""
    safe_title = html.escape(title)
    subtitle_html = f'<p class="hero-subtitle">{_render_inline_text(subtitle)}</p>' if subtitle else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_title}</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --card: #ffffff;
      --text: #1f2933;
      --muted: #52606d;
      --accent: #0b7285;
      --border: #d9e2ec;
      --table-head: #e6f4f1;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      line-height: 1.6;
    }}

    .page {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}

    .hero {{
      background: linear-gradient(135deg, #0b7285, #1f4e79);
      color: #ffffff;
      border-radius: 20px;
      padding: 28px 32px;
      margin-bottom: 24px;
      box-shadow: 0 16px 32px rgba(15, 23, 42, 0.12);
    }}

    .hero h1 {{
      margin: 0;
      font-size: 2rem;
    }}

    .hero-subtitle {{
      margin: 10px 0 0;
      color: rgba(255, 255, 255, 0.92);
      font-size: 1rem;
    }}

    .content {{
      display: grid;
      gap: 20px;
    }}

    section {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    h2, h3 {{
      margin-top: 0;
      color: #102a43;
    }}

    p, li {{
      color: var(--text);
    }}

    .muted {{
      color: var(--muted);
    }}

    .section-description,
    .block-description {{
      margin-top: -4px;
    }}

    .report-block + .report-block {{
      margin-top: 18px;
    }}

    .report-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 0.95rem;
      min-width: 680px;
    }}

    .report-table th,
    .report-table td {{
      border: 1px solid var(--border);
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
      word-break: break-word;
    }}

    .report-table thead th {{
      background: var(--table-head);
      color: #102a43;
    }}

    .report-figure {{
      margin: 18px 0 0;
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .report-figure img {{
      width: 100%;
      max-width: 100%;
      border-radius: 16px;
      border: 1px solid var(--border);
      background: #ffffff;
      display: block;
      height: auto;
    }}

    .report-figure figcaption {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.92rem;
    }}

    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-top: 12px;
    }}

    .metric-card {{
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      background: #f8fbfd;
    }}

    .metric-card strong {{
      display: block;
      margin-bottom: 6px;
      color: #102a43;
    }}

    code, pre {{
      font-family: Consolas, "Courier New", monospace;
    }}

    pre {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 16px;
      border-radius: 14px;
      overflow-x: auto;
      white-space: pre-wrap;
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    ul, ol {{
      margin-bottom: 0;
      padding-left: 24px;
    }}

    .table-wrap {{
      width: 100%;
      overflow-x: auto;
      margin-top: 12px;
    }}

    @media (max-width: 720px) {{
      .page {{
        padding: 20px 12px 32px;
      }}

      .hero {{
        padding: 22px 20px;
        border-radius: 16px;
      }}

      .hero h1 {{
        font-size: 1.6rem;
      }}

      section {{
        padding: 18px;
        border-radius: 16px;
      }}

      .metrics-grid {{
        grid-template-columns: 1fr;
      }}

      .report-table {{
        font-size: 0.9rem;
        min-width: 560px;
      }}

      .report-figure img {{
        border-radius: 12px;
      }}
    }}

    @media print {{
      @page {{
        size: A4 portrait;
        margin: 12mm;
      }}

      body {{
        background: #ffffff;
        color: #000000;
        font-size: 11pt;
      }}

      .page {{
        max-width: none;
        margin: 0;
        padding: 0;
      }}

      .hero {{
        background: #ffffff;
        color: #000000;
        border: 2px solid var(--border);
        box-shadow: none;
        margin-bottom: 16px;
        break-after: avoid;
        page-break-after: avoid;
      }}

      .hero-subtitle {{
        color: #374151;
      }}

      section {{
        box-shadow: none;
        border-radius: 10px;
        margin-bottom: 14px;
      }}

      .table-wrap {{
        overflow: visible;
      }}

      .report-table {{
        min-width: 0;
        width: 100%;
        font-size: 9.5pt;
      }}

      .report-table thead {{
        display: table-header-group;
      }}

      .report-table tr,
      .metric-card,
      .report-figure,
      pre {{
        break-inside: avoid;
        page-break-inside: avoid;
      }}

      .report-figure img {{
        max-height: 235mm;
        object-fit: contain;
      }}

      a {{
        color: inherit;
        text-decoration: none;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header class="hero">
      <h1>{safe_title}</h1>
      {subtitle_html}
    </header>
    <div class="content">
      {body}
    </div>
  </main>
</body>
</html>
"""
