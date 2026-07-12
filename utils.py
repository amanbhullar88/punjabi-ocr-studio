import unicodedata

FONT_FAMILY_MAP = {
    "Gurmukhi (Unicode)": "Raavi",
    "Raavi (Unicode)": "Raavi",
    "Asees": "Asees",
    "Anmol Lipi": "AnmolLipi",
    "Joy": "Joy",
    "Gurbani": "GurbaniLipi",
    "AmritLipi": "AmritLipi",
    "Satluj": "Satluj",
    "Amar Lipi": "AmarLipi",
    "Gurumukhi Lys (CCTNS CAS)": "GurumukhiLys-020-Condensed",
}
DROPDOWN_TO_CONVERTER = {
    "Gurmukhi (Unicode)": "Unicode",
    "Raavi (Unicode)": "Unicode",
    "Asees": "Asees",
    "Anmol Lipi": "AnmolLipi",
    "Joy": "Joy",
    "Gurbani": "GurbaniLipi",
    "AmritLipi": "AmritLipi",
    "Satluj": "Satluj",
    "Amar Lipi": "AmarLipi",
    "Gurumukhi Lys (CCTNS CAS)": "GurumukhiLys",
}
CONV_SOURCE_UNICODE = "AnmolUni"

def sanitize_unicode(s):
    if not s:
        return s
    s = unicodedata.normalize('NFC', s)
    for ch in ('\u200d','\u200c','\u200b','\u2060','\u00A0','\ufeff','\u00ad'):
        s = s.replace(ch, ' ')
    
    # Split by line to preserve layout and newlines, clean spaces within each line
    lines = s.splitlines()
    cleaned_lines = []
    for line in lines:
        cleaned_line = " ".join(line.split())
        cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines)

def is_gurmukhi_unicode(text):
    if not text:
        return False
    # If there is even one character in the Gurmukhi range, it is Unicode
    return any('\u0A00' <= c <= '\u0A7F' for c in text)

def detect_legacy_font(text):
    # Common words in Anmol Lipi layout
    anmol_words = [
        "syvw", "iProzpUr", "lyb", "pulIs", "mJy", "Awp", 
        "sRImwn", "bynqI", "AMdr", "hY", "ik", "ijlw", "iemwrq"
    ]
    if any(x in text for x in anmol_words):
        return "AnmolLipi"
    return "Asees"

WORD_FONT_MAP = {
    "Unicode": "Raavi",
    "AnmolLipi": "Anmol Lipi",
    "Asees": "Asees",
    "Joy": "Joy",
    "GurbaniLipi": "GurbaniLipi",
    "AmritLipi": "AmritLipi",
    "Satluj": "Satluj",
    "AmarLipi": "AmarLipi",
    "GurumukhiLys": "Gurumukhi Lys (CCTNS CAS)"
}

LEGACY_FONTS = {
    "Asees", "AnmolLipi", "Anmol Lipi", "Joy", "GurbaniLipi", 
    "Satluj", "AmritLipi", "AmarLipi", "GurumukhiLys", 
    "GurumukhiLys-020-Condensed", "Gurumukhi Lys", "Gurumukhi Lys (CCTNS CAS)"
}

def split_gurmukhi_segments(text):
    """
    Split text into segments of Gurmukhi Unicode characters and other characters (English/spaces/numbers).
    Returns a list of tuples: (is_gurmukhi, segment_text)
    """
    if not text:
        return []
    
    segments = []
    current_segment = []
    
    # Find the first character that is clearly Gurmukhi or English to set the initial state
    is_gur = True
    for char in text:
        if '\u0A00' <= char <= '\u0A7F':
            is_gur = True
            break
        elif char.isalpha():
            is_gur = False
            break
            
    for char in text:
        # Check if character is Gurmukhi
        char_is_gur = ('\u0A00' <= char <= '\u0A7F') or char in ('\u0964', '\u0965')
        # Check if character is English letter
        char_is_eng = char.isalpha() and not char_is_gur
        
        # Space, numbers, and punctuation are "neutral" and don't change the active segment type
        if not char_is_gur and not char_is_eng:
            current_segment.append(char)
        else:
            if char_is_gur == is_gur:
                current_segment.append(char)
            else:
                if current_segment:
                    segments.append((is_gur, "".join(current_segment)))
                is_gur = char_is_gur
                current_segment = [char]
                
    if current_segment:
        segments.append((is_gur, "".join(current_segment)))
        
    return segments