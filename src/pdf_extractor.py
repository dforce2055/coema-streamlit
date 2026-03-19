"""
OCEBA PDF Tariff Extractor
Extracts tariff data from OCEBA resolution PDFs (Anexo 6, 14, 104)
for Area Atlantica (EDEA - includes COEMA General Madariaga)
"""

import re
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def parse_number(s: str) -> float:
    """Convert Argentine number format to float.
    '3.441,98' -> 3441.98 | '160,2894' -> 160.2894
    Also handles pdfplumber artifacts like '3 .441,98' or '1 60,2894'
    """
    s = s.replace(' ', '')  # Remove internal spaces from PDF extraction
    return float(s.replace('.', '').replace(',', '.'))


def detect_anexo(text: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """Detect Anexo type from PDF text. Returns (anexo_num, nivel, descripcion)."""
    t = text.upper()
    if 'ANEXO 104' in t or 'TARIFA SOCIAL' in t:
        return 104, 'N3', 'Tarifa Social'
    elif 'ANEXO 14' in t:
        return 14, 'N2', 'Subsidio hasta 350 kWh/mes'
    elif 'ANEXO 6' in t:
        return 6, 'N1', 'Precio completo (sin subsidio)'
    return None, None, None


# Known ranges per tariff type (stable across resolutions, only values change)
RANGOS_T1R = {
    1: (0, 100), 2: (100, 200), 3: (200, 400),
    4: (400, 500), 5: (500, 700), 6: (700, 1400), 7: (1400, 99999),
}
RANGOS_T1RE = {
    1: (0, 500), 2: (500, 700), 3: (700, 1400), 4: (1400, 99999),
}


def _section_between(text: str, start_re: str, end_re: str) -> str:
    """Extract text between two regex patterns."""
    start = re.search(start_re, text, re.IGNORECASE)
    if not start:
        return ''
    rest = text[start.start():]
    end = re.search(end_re, rest[len(start.group()):], re.IGNORECASE)
    if end:
        return rest[:len(start.group()) + end.start()]
    return rest


def _extract_cargos(section: str, prefix: str, ranges: dict) -> List[Dict]:
    """Extract cargo fijo and cargo variable per escalon from a tariff section.

    Handles pdfplumber artifacts where numbers have internal spaces,
    e.g. '3 .441,98' instead of '3.441,98' or '1 60,2894' instead of '160,2894'.
    """
    # Pattern captures numbers that may contain internal spaces from PDF extraction
    # e.g. "3 .441,98" or "1 60,2894" or "3.441,98" (no spaces)
    num_pattern = r'(\d[\d .,]*\d)\s+\$'

    fijos = re.findall(
        rf'CARGO\s+FIJO\s+{prefix}(\d+)\b.*?{num_pattern}(?:/mes|factura)',
        section, re.IGNORECASE
    )
    variables = re.findall(
        rf'CARGO\s+VARIABLE\s+{prefix}(\d+)\b.*?{num_pattern}/kWh',
        section, re.IGNORECASE
    )

    fijo_map = {int(n): parse_number(v) for n, v in fijos}
    var_map = {int(n): parse_number(v) for n, v in variables}
    all_nums = sorted(set(list(fijo_map.keys()) + list(var_map.keys())))

    escalones = []
    for num in all_nums:
        desde, hasta = ranges.get(num, (0, 99999))
        escalones.append({
            'num': num,
            'nombre': f'{prefix}{num}',
            'desde': desde,
            'hasta': hasta,
            'cargo_fijo': fijo_map.get(num, 0.0),
            'cargo_variable': var_map.get(num, 0.0),
        })
    return escalones


def extract_tariffs(text: str) -> Dict:
    """
    Main extraction function.
    Parses PDF text into structured tariff data for T1R and T1RE.

    Returns:
        dict with keys: anexo, nivel, descripcion, tarifas
        tarifas is a dict keyed by tariff code (T1R, T1RE) with escalones list
    """
    anexo, nivel, descripcion = detect_anexo(text)

    result = {
        'anexo': anexo,
        'nivel': nivel,
        'descripcion': descripcion,
        'tarifas': {},
    }

    # --- T1R - Residencial ---
    t1r_section = _section_between(
        text,
        r'T1R\s*[-–]?\s*RESIDENCIAL\b(?!\s*ESTACIONAL)',
        r'T1RE\s*[-–]?\s*RESIDENCIAL\s+ESTACIONAL',
    )
    if t1r_section:
        esc = _extract_cargos(t1r_section, 'R', RANGOS_T1R)
        if esc:
            result['tarifas']['T1R'] = {
                'nombre': 'Tarifa 1 Residencial',
                'codigo': 'T1R',
                'escalones': esc,
            }

    # --- T1RE - Residencial Estacional ---
    t1re_section = _section_between(
        text,
        r'T1RE\s*[-–]?\s*RESIDENCIAL\s+ESTACIONAL',
        r'T1G\s*[-–]|T2\s*[-–]|T3\s*[-–]|GRANDES\s+DEMANDAS',
    )
    if t1re_section:
        esc = _extract_cargos(t1re_section, 'RE', RANGOS_T1RE)
        if esc:
            result['tarifas']['T1RE'] = {
                'nombre': 'Tarifa 1 Residencial Estacional',
                'codigo': 'T1RE',
                'escalones': esc,
            }

    # --- N3 Bonificaciones (Anexo 104 only) ---
    if anexo == 104:
        bonif = {}
        matches = re.findall(
            r'Bonificaci[oó]n\s+R(\d+)\s+.*?(\d[\d .,]*\d)\s+\$/mes',
            text, re.IGNORECASE,
        )
        for num, val in matches:
            bonif[int(num)] = parse_number(val)
        if bonif:
            result['bonificaciones_t1r'] = bonif

    return result


def extract_tariffs_from_pdf(pdf_path: str) -> Dict:
    """Extract tariffs from a PDF file on disk."""
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        pages_text = [p.extract_text() or '' for p in pdf.pages]

    result = extract_tariffs('\n'.join(pages_text))
    result['archivo'] = Path(pdf_path).name
    result['paginas'] = len(pages_text)
    return result


def extract_tariffs_from_bytes(pdf_bytes: bytes) -> Dict:
    """Extract tariffs from raw PDF bytes (for Streamlit file_uploader)."""
    import pdfplumber

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages_text = [p.extract_text() or '' for p in pdf.pages]

    return extract_tariffs('\n'.join(pages_text))


def extract_tariffs_from_url(url: str) -> Dict:
    """Download a PDF from a URL and extract tariffs."""
    import requests

    response = requests.get(url, timeout=30, headers={
        'User-Agent': 'COEMA-Facturacion/1.0',
    })
    response.raise_for_status()

    content_type = response.headers.get('Content-Type', '')
    if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
        raise ValueError(
            f"La URL no parece ser un PDF (Content-Type: {content_type})"
        )

    result = extract_tariffs_from_bytes(response.content)
    result['url'] = url
    return result
