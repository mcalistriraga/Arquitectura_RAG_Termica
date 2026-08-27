# =============================================================
# Archivo: parsers/csharp_parser.py (v2.1.5)
#
# Descripción:
# Extractor heurístico de símbolos C# (.cs) para Knowledge Source (KS2).
#
# Correcciones v2.1.5:
# - Detección explícita de constructores. RE_METHOD exige un token de
#   tipo de retorno, por lo que un constructor ("public NombreClase(...)")
#   era mal interpretado: el modificador de acceso se leía como si fuera
#   el tipo de retorno. Se agrega constructor_pattern (usa el nombre real
#   de la entidad) que detecta constructores correctamente y los marca
#   con "is_constructor": true, access y parámetros reales. Los métodos
#   regulares ahora incluyen "is_constructor": false para mantener un
#   esquema consistente. Hallazgo detectado validando symbols_raw.jsonl
#   contra el proyecto MAUI real (no cubierto por test_parser_v214.py).
#
# Correcciones v2.1.4:
# - Mantenimiento estricto del enmascaramiento depth >= 2 para clases anidadas y métodos.
# - Discriminación de bloques de propiedades (get/set/init) en _extract_body_clean
#   para evitar el borrado de sus llaves y permitir la correcta extracción por RE_PROPERTY.
# =============================================================

import re

CSHARP_KEYWORDS_AND_RESERVED = {
    "from", "select", "where", "group", "by", "into", "orderby", "join", "let",
    "in", "on", "equals", "ascending", "descending", "yield", "return", "var",
    "new", "get", "set", "add", "remove", "value", "global", "alias", "await",
    "if", "else", "while", "for", "foreach", "do", "switch", "case", "default",
    "try", "catch", "finally", "throw", "using", "lock", "goto", "break", "continue"
}

RE_NAMESPACE = re.compile(r'\bnamespace\s+([\w\.]+)')

# Detección de entidades
RE_ENTITY = re.compile(
    r'(?:\b(public|internal|protected\s+internal|private\s+protected|protected|private)\s+)?'
    r'((?:\b(?:abstract|sealed|static|readonly|partial|unsafe|ref|new)\s+)*)'
    r'\b(class|interface|struct|record\s+class|record\s+struct|record|enum)\s+'
    r'([A-Za-z_]\w*)'
    r'(?:\s*<[^>]+>)?'
    r'(?:\s*\([^)]*\))?'
    r'(?:\s*:\s*([\w\s,<>.]+?))?'
    r'(?:\s+where\b[^{;]+)?'
    r'\s*([\{;])'
)

# Modificador de acceso opcional para capturar métodos implícitos como "static void Main"
RE_METHOD = re.compile(
    r'(?:\b(public|protected\s+internal|private\s+protected|protected|private|internal)\s+)?'
    r'((?:\b(?:static|async|virtual|override|sealed|unsafe|new)\s+)*)'
    r'([\w<>,?\[\]]+)\s+'
    r'([A-Za-z_]\w*)\s*'
    r'\(([^)]*)\)'
)

RE_PROPERTY = re.compile(
    r'\b(public|protected\s+internal|private\s+protected|protected|private|internal)\s+'
    r'([\w<>,?\[\]]+)\s+'
    r'([A-Za-z_]\w*)\s*'
    r'\{\s*(?:(?:public|protected|private|internal)\s+)*(?:get|set|init)\b'
)


def _strip_comments_and_strings(code: str) -> str:
    def replacer(match):
        s = match.group(0)
        return '\n' * s.count('\n') if s.startswith('/') else ' ' + ('\n' * s.count('\n'))

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|'
        r'[\$@]*("{3,})[\s\S]*?\1|'
        r'[@\$]*"(?:""|[^"])*"|'
        r'\'(?:\\.|[^\'\\])\'',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, code)


def _is_property_block(content: str, open_idx: int) -> bool:
    """
    Inspecciona si el bloque iniciado en open_idx corresponde a los accesores
    de una propiedad (ej. { get; set; }) en lugar de un cuerpo de método o clase anidada.
    """
    close_idx = content.find('}', open_idx)
    if close_idx == -1:
        return False
    inner = content[open_idx + 1:close_idx]
    # Si contiene otras llaves anidadas, es un bloque complejo/método
    if '{' in inner or '}' in inner:
        return False
    # Verifica presencia de palabras clave de accesores
    return bool(re.search(r'\b(get|set|init)\b', inner))


def _extract_body_clean(content: str, start_index: int) -> str:
    open_brace_idx = content.find('{', start_index)
    if open_brace_idx == -1:
        return ""

    chars = list(content)
    i = open_brace_idx
    depth = 0
    block_start = -1
    is_prop = False

    while i < len(chars):
        char = chars[i]
        if char == '{':
            depth += 1
            if depth == 2:
                block_start = i
                is_prop = _is_property_block(content, i)
        elif char == '}':
            if depth == 2 and block_start != -1:
                if not is_prop:
                    for j in range(block_start, i + 1):
                        if chars[j] != '\n':
                            chars[j] = ' '
                block_start = -1
                is_prop = False
            depth -= 1
            if depth == 0:
                break
        i += 1

    return "".join(chars[open_brace_idx + 1:i])


def _parse_parameters_raw(params_raw: str) -> list:
    if not params_raw.strip():
        return []

    raw_list = []
    current = []
    angle_depth = 0

    for char in params_raw:
        if char == '<':
            angle_depth += 1
            current.append(char)
        elif char == '>':
            angle_depth -= 1
            current.append(char)
        elif char == ',' and angle_depth == 0:
            raw_list.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        raw_list.append("".join(current).strip())

    parsed_params = []
    for param in raw_list:
        if not param:
            continue
        param_decl = param.split('=')[0].strip()
        tokens = param_decl.split()
        tokens = [t for t in tokens if t not in ("ref", "out", "in", "params", "this")]

        if len(tokens) >= 2:
            param_name = tokens[-1]
            param_type = " ".join(tokens[:-1])
            parsed_params.append({
                "type": param_type,
                "name": param_name
            })

    return parsed_params


def parse_csharp_file(file_content, relative_path):
    symbols = []
    clean_content = _strip_comments_and_strings(file_content)

    namespace_match = RE_NAMESPACE.search(clean_content)
    namespace = namespace_match.group(1) if namespace_match else "Global"

    for match in RE_ENTITY.finditer(clean_content):
        access = match.group(1) or "internal"
        raw_modifiers_str = match.group(2) or ""
        modifiers = [m for m in raw_modifiers_str.split() if m.strip()]
        kind = match.group(3).strip()
        name = match.group(4)
        raw_heritage = match.group(5)
        terminator = match.group(6)

        if name in CSHARP_KEYWORDS_AND_RESERVED:
            continue

        inherits = None
        implements = []

        if raw_heritage:
            tokens = [t.strip() for t in raw_heritage.split(",") if t.strip()]
            if tokens:
                if kind in ("class", "record", "record class") and not tokens[0].startswith("I"):
                    inherits = tokens[0]
                    implements = tokens[1:]
                else:
                    implements = tokens

        body_content = _extract_body_clean(clean_content, match.end() - 1) if terminator == '{' else ""

        # ---------------------------------------------------------------
        # Constructores
        #
        # Un constructor tiene la forma "[acceso] NombreClase(params)"
        # sin tipo de retorno. RE_METHOD exige un token de tipo de
        # retorno además del nombre, por lo que ante un constructor
        # termina interpretando el modificador de acceso ("public",
        # "private", etc.) como si fuera el tipo de retorno, y el
        # nombre de la clase como si fuera el nombre de un método.
        # Se detectan aquí explícitamente, usando el nombre real de la
        # entidad, para evitar esa mala clasificación.
        # ---------------------------------------------------------------
        constructor_pattern = re.compile(
            r'(?:\b(public|protected\s+internal|private\s+protected|protected|private|internal)\s+)?'
            r'(?:\b(?:static|extern)\s+)*'
            r'\b' + re.escape(name) + r'\b'
            r'\s*\(([^)]*)\)'
            r'(?:\s*:\s*(?:base|this)\s*\([^)]*\))?'
        )

        methods = []

        for c_match in constructor_pattern.finditer(body_content):
            c_access = c_match.group(1) or "private"
            c_params_raw = c_match.group(2)

            methods.append({
                "name": name,
                "access": c_access,
                "is_async": False,
                "return_type": None,
                "parameters": _parse_parameters_raw(c_params_raw),
                "is_constructor": True
            })

        for m_match in RE_METHOD.finditer(body_content):
            m_access = m_match.group(1) or "private"
            m_mods = m_match.group(2) or ""
            m_ret = m_match.group(3)
            m_name = m_match.group(4)
            m_params_raw = m_match.group(5)

            if m_name in CSHARP_KEYWORDS_AND_RESERVED or m_name in ("if", "while", "for", "switch", "catch"):
                continue

            # En C# un método no puede tener el mismo nombre que su
            # clase contenedora (solo los constructores pueden). Si
            # aparece acá, es un constructor mal-matcheado por
            # RE_METHOD y ya fue capturado correctamente arriba.
            if m_name == name:
                continue

            methods.append({
                "name": m_name,
                "access": m_access,
                "is_async": "async" in m_mods,
                "return_type": m_ret,
                "parameters": _parse_parameters_raw(m_params_raw),
                "is_constructor": False
            })

        properties = []
        for p_match in RE_PROPERTY.finditer(body_content):
            p_name = p_match.group(3)
            if p_name in CSHARP_KEYWORDS_AND_RESERVED:
                continue

            properties.append({
                "name": p_name,
                "type": p_match.group(2),
                "access": p_match.group(1)
            })

        symbols.append({
            "entity_type": kind,
            "name": name,
            "namespace": namespace,
            "file": relative_path,
            "access": access,
            "modifiers": modifiers,
            "inherits": inherits,
            "implements": implements,
            "methods": methods,
            "properties": properties
        })

    return symbols

