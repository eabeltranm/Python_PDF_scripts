REFERENCE_PATTERNS = {
    'ott_pattern': {'pattern': r"OTT[\w\s,-]*?CM", 'enabled': True},
    'otf_pattern': {'pattern': r"OTF[\w\s,-]*?CM", 'enabled': True},
    'ots_pattern': {'pattern': r"OTS[\w\s,-]*?CM", 'enabled': True},
    'otl_pattern': {'pattern': r"OTL[\w\s,-]*?APLICADOR", 'enabled': True},
    'otp_pattern': {'pattern': r"OTP-?\s*[\w\s,-]*?GR", 'enabled': True},
    'ot_pattern': {'pattern': r"OT-[\w\s,(\w\s)-]*?CM", 'enabled': True},
    'alphanumeric': {'pattern': r"[\w/]+", 'enabled': True},
    'ts_mm_paren': {'pattern': r"TS[\w\s,(\w\s)\s-]*?MM\)", 'enabled': True},
    'ts_mm': {'pattern': r"TS[\w\s,-]*?MM", 'enabled': True},
    'tsf_pattern': {'pattern': r"TSF[\w\s,(\w\s)\s-]*?MM\)", 'enabled': True},
    'tsp_pattern': {'pattern': r"TSP[\w\s,(\w\s)\s-]*?GR\)", 'enabled': True},
    'wm_mm': {'pattern': r"WM[\w\s-]*?\d*MM", 'enabled': True},
    'wm_complex_1': {'pattern': r"(WM[\w]*-\d{3}[\w\s]*[\w\s\d-]+?)(?=\s*WM[\w]*-\d{3}|$)", 'enabled': True},
    'wm_complex_2': {'pattern': r"(WM\w*-*\d*\s*[\w\s\d-]+?)(?=\s*WM\w*-*\d*|$)", 'enabled': True},
    'fq_pattern': {'pattern': r"F[A-Z]\d+[A-Z]+", 'enabled': True}
}

def enable_pattern(pattern_name):
    """Enable a specific pattern by name."""
    if pattern_name in REFERENCE_PATTERNS:
        REFERENCE_PATTERNS[pattern_name]['enabled'] = True

def disable_pattern(pattern_name):
    """Disable a specific pattern by name."""
    if pattern_name in REFERENCE_PATTERNS:
        REFERENCE_PATTERNS[pattern_name]['enabled'] = False

def get_active_patterns():
    """Return only the enabled patterns."""
    return {name: data['pattern'] for name, data in REFERENCE_PATTERNS.items() 
            if data['enabled']}

def disable_all_patterns():
    """Disable all patterns."""
    for pattern in REFERENCE_PATTERNS:
        REFERENCE_PATTERNS[pattern]['enabled'] = False

def enable_all_patterns():
    """Enable all patterns."""
    for pattern in REFERENCE_PATTERNS:
        REFERENCE_PATTERNS[pattern]['enabled'] = True

def get_pattern_status():
    """Print the status of all patterns."""
    for name, data in REFERENCE_PATTERNS.items():
        print(f"{name}: {'Enabled' if data['enabled'] else 'Disabled'}")
