# converter.py – Full working version
# Supports: Unicode, AnmolLipi, Asees, Satluj, Joy, GurbaniLipi, DrChatrikWeb, Awaze

from typing import List, Dict, Any

# -----------------------------
# Helper functions
# -----------------------------
def get_char_from_unicode(*unicodes: int) -> str:
    return "".join(chr(c) for c in unicodes)

def get_composition_characters(composition_char_arrays: List[List[int]], codes: List[Any]) -> List[str]:
    characters = []
    for composition_char in composition_char_arrays:
        is_valid = True
        char_codes = []
        for code in composition_char:
            to_code = None
            if code < len(codes):
                to_code = codes[code]
            if to_code:
                char_codes.append(to_code)
            else:
                is_valid = False
                break
        if is_valid:
            characters.append(get_char_from_unicode(*char_codes))
    return characters

# -----------------------------
# Conversion engine (fixed)
# -----------------------------
def convert_string_using_mapper(mapper_config: Dict[str, Any], string_to_convert: str) -> str:
    mapper = mapper_config["mapper"]
    max_width = mapper_config["maxWidth"]
    move_right_chars = mapper_config["moveRightChars"]
    move_left_chars = mapper_config["moveLeftChars"]
    move_across_chars = mapper_config.get("moveAcrossCharacters", [])

    output: List[str] = []
    pending_right = None

    i = 0
    n = len(string_to_convert)
    while i < n:
        match_found = False
        char_to_add = None
        for j in range(max_width, 0, -1):
            if i + j <= n:
                sub = string_to_convert[i:i+j]
                if sub in mapper:
                    char_to_add = mapper[sub]
                    i += j
                    match_found = True
                    break
        if not match_found:
            char_to_add = string_to_convert[i]
            i += 1

        if pending_right is not None:
            if char_to_add in move_right_chars:
                output.append(char_to_add)
            else:
                # In Unicode, the consonant (char_to_add) must be placed BEFORE the Matra (pending_right)
                output.append(char_to_add)
                output.append(pending_right)
                pending_right = None
        elif char_to_add in move_right_chars:
            pending_right = char_to_add
        elif char_to_add in move_left_chars and len(output) > 0:
            insert_char_on_left(output, move_left_chars, move_across_chars, char_to_add)
        else:
            output.append(char_to_add)

    if pending_right is not None:
        output.append(pending_right)

    return "".join(output)

def insert_char_on_left(chars: List[str], move_left_chars: List[str], move_across_chars: List[str], character_to_add: str):
    if not chars:
        chars.append(character_to_add)
        return
    moved = []
    # 1. Pop any characters that are in move_left_chars or move_across_chars (like subjoined consonants)
    while chars and (chars[-1] in move_left_chars or chars[-1] in move_across_chars):
        moved.insert(0, chars.pop())
    # 2. Pop EXACTLY ONE more character (the main consonant)
    if chars:
        moved.insert(0, chars.pop())
    # 3. Append the sihari
    chars.append(character_to_add)
    # 4. Put back the popped characters
    chars.extend(moved)

# -----------------------------
# Mapping tables (complete)
# -----------------------------
anmolMapping = {
    1: 0x3c, 2: 0x3e, 4: 0xc5, 5: 0xc6, 6: 0xa1,
    11: 0x61, 15: 0x45, 17: 0x41, 21: 0x65,
    25: 0x73, 26: 0x68, 27: 0x6b, 28: 0x4b, 29: 0x67, 30: 0x47,
    31: 0x7c, 32: 0x63, 33: 0x43, 34: 0x6a, 35: 0x4a,
    36: 0x5c, 37: 0x74, 38: 0x54, 39: 0x66, 40: 0x46,
    41: 0x78, 42: 0x71, 43: 0x51, 44: 0x64, 45: 0x44,
    46: 0x6e, 47: 0x70, 48: 0x50, 49: 0x62, 50: 0x42,
    51: 0x6d, 52: 0x58, 53: 0x72, 54: 0x6c, 55: 0x76,
    56: 0x56, 57: 0x53, 58: 0x5e, 59: 0x5a, 60: 0x7a,
    61: 0x26, 62: 0x4c, 63: 0xe6, 65: 0x2e, 66: 0x48,
    68: 0xa7, 69: 0x52, 71: 0xae, 72: 0xe7, 73: 0x2020,
    74: 0xcd, 76: 0xcf, 77: 0x153, 78: 0x2dc, 79: 0xce,
    82: 0x4d, 85: 0x4e, 86: 0x2c6, 89: 0x60, 90: 0x7e,
    91: 0xa4, 92: 0x0A01, 94: 0x77, 96: 0x57, 97: 0x69,
    99: 0x49, 103: 0x75, 104: 0xfc, 106: 0x55, 107: 0xa8,
    109: 0x79, 111: 0x59, 113: 0x6f, 115: 0x4f, 118: 0x40,
    120: 0x5b, 124: 0x5d, 125: 0xd2, 126: 0xfa, 127: 0xf1,
    129: 0xf2, 130: 0xf3, 131: 0xf4, 132: 0xf5, 133: 0xf6,
    134: 0xf7, 135: 0xf8, 136: 0xf9, 137: 0x30, 138: 0x31,
    139: 0x32, 140: 0x33, 141: 0x34, 142: 0x35, 143: 0x36,
    144: 0x37, 145: 0x38, 146: 0x39, 147: 0x192, 150: 0x2039,
    151: 0xbf, 152: 0xc7, 154: 0x152, 155: 0x201a, 156: 0x2030,
    157: 0xd3, 158: 0xd4, 159: 0x2022, 160: 0xff, 161: 0x3a,
    162: 0xda, 163: 0x3b, 166: 0xb4, 167: 0xd8, 168: 0x2018,
    170: 0x2019, 172: 0x201c, 173: 0x201d
}

unicodeMapping = {
    0: 0x0A74, 11: 0x0A73, 12: 0x0A09, 14: 0x0A0A, 15: 0x0A13,
    17: 0x0A05, 18: 0x0A06, 19: 0x0A10, 20: 0x0A14, 21: 0x0A72,
    22: 0x0A07, 23: 0x0A08, 24: 0x0A0F, 25: 0x0A38, 26: 0x0A39,
    27: 0x0A15, 28: 0x0A16, 29: 0x0A17, 30: 0x0A18, 31: 0x0A19,
    32: 0x0A1A, 33: 0x0A1B, 34: 0x0A1C, 35: 0x0A1D, 36: 0x0A1E,
    37: 0x0A1F, 38: 0x0A20, 39: 0x0A21, 40: 0x0A22, 41: 0x0A23,
    42: 0x0A24, 43: 0x0A25, 44: 0x0A26, 45: 0x0A27, 46: 0x0A28,
    47: 0x0A2A, 48: 0x0A2B, 49: 0x0A2C, 50: 0x0A2D, 51: 0x0A2E,
    52: 0x0A2F, 53: 0x0A30, 54: 0x0A32, 55: 0x0A35, 56: 0x0A5C,
    57: 0x0A36, 58: 0x0A59, 59: 0x0A5A, 60: 0x0A5B, 61: 0x0A5E,
    62: 0x0A33, 63: 0x0A3C, 82: 0x0A70, 85: 0x0A02, 87: 0x0A03,
    90: 0x0A71, 93: 0x0A75, 94: 0x0A3E, 97: 0x0A3F, 99: 0x0A40,
    103: 0x0A41, 106: 0x0A42, 109: 0x0A47, 111: 0x0A48, 113: 0x0A4B,
    115: 0x0A4C, 118: 0x0A4D, 119: 0x0A51, 120: 0x0964, 124: 0x0965,
    126: 0x0A66, 127: 0x0A67, 129: 0x0A68, 130: 0x0A69, 131: 0x0A6A,
    132: 0x0A6B, 133: 0x0A6C, 134: 0x0A6D, 135: 0x0A6E, 136: 0x0A6F,
    137: 0x30, 138: 0x31, 139: 0x32, 140: 0x33, 141: 0x34,
    142: 0x35, 143: 0x36, 144: 0x37, 145: 0x38, 146: 0x39,
    150: 0xf7, 151: 0xd7, 160: 0xff, 161: 0x3a, 163: 0x3b,
    168: 0x2018, 170: 0x2019, 172: 0x201c, 173: 0x201d
}

drChatrikMappings = {
    1: 0xc3, 2: 0xc4, 11: 0x41, 17: 0x61, 21: 0x65,
    25: 0x73, 26: 0x68, 27: 0x6b, 28: 0x4b, 29: 0x67, 30: 0x47,
    31: 0xd5, 32: 0x63, 33: 0x43, 34: 0x6a, 35: 0x4a,
    36: 0xd6, 37: 0x74, 38: 0x54, 39: 0x7a, 40: 0x5a,
    41: 0x78, 42: 0x71, 43: 0x51, 44: 0x64, 45: 0x44,
    46: 0x6e, 47: 0x70, 48: 0x50, 49: 0x62, 50: 0x42,
    51: 0x6d, 52: 0x58, 53: 0x72, 54: 0x6c, 55: 0x76,
    56: 0x56, 57: 0xc8, 58: 0xc9, 59: 0xca, 60: 0xcb,
    61: 0xcc, 62: 0xdc, 63: 0xe6, 64: 0x4c, 65: 0x5b,
    66: 0x48, 69: 0x52, 82: 0x4d, 83: 0x53, 85: 0x4e,
    90: 0x77, 91: 0x57, 92: 0x0A01, 94: 0x66, 96: 0x46,
    97: 0x69, 99: 0x49, 103: 0x75, 106: 0x55, 109: 0x79,
    111: 0x59, 113: 0x6f, 115: 0x4f, 118: 0xd9, 120: 0x2e,
    122: 0x7c, 123: 0xbb, 124: 0x5d, 125: 0xab, 126: 0xfa,
    127: 0xf1, 129: 0xf2, 130: 0xf3, 131: 0xf4, 132: 0xf5,
    133: 0xf6, 134: 0xf7, 135: 0xf8, 136: 0xf9, 137: 0x30,
    138: 0x31, 139: 0x32, 140: 0x33, 141: 0x34, 142: 0x35,
    143: 0x36, 144: 0x37, 145: 0x38, 146: 0x39, 161: 0x3a,
    162: 0xda, 163: 0x3b, 168: 0x2018, 170: 0x2019, 172: 0x201c,
    173: 0x201d
}

awazeMappings = {
    6: 0xf7, 9: 0xd8, 10: 0xa3, 11: 0x75, 15: 0x6f,
    17: 0x61, 21: 0x65, 24: 0xb4, 25: 0x73, 26: 0x68,
    27: 0x63, 28: 0x6b, 29: 0x67, 30: 0x47, 31: 0x4c,
    32: 0x43, 33: 0x78, 34: 0x6a, 35: 0x4a, 36: 0x4d,
    37: 0x74, 38: 0x54, 39: 0x44, 40: 0x51, 41: 0x4e,
    42: 0x56, 43: 0x57, 44: 0x64, 45: 0x59, 46: 0x6e,
    47: 0x70, 48: 0x66, 49: 0x62, 50: 0x42, 51: 0x6d,
    52: 0x79, 53: 0x72, 54: 0x6c, 55: 0x76, 56: 0x52,
    57: 0x53, 58: 0x4b, 59: 0x5a, 60: 0x7a, 61: 0x46,
    63: 0xe6, 65: 0x50, 66: 0x48, 69: 0x71, 72: 0xe7,
    73: 0x2020, 74: 0x58, 76: 0xcf, 77: 0x153, 78: 0x2dc,
    80: 0x77, 82: 0x2a, 84: 0x5e, 89: 0x26, 90: 0x25,
    92: 0x0A01, 85: 0x3a, 86: 0x2c6, 94: 0x41, 96: 0x3b,
    97: 0x69, 99: 0x49, 101: 0x192, 103: 0x55, 104: 0xfc,
    106: 0x3c, 109: 0x45, 111: 0x3e, 113: 0x7e, 115: 0x4f,
    116: 0xf8, 118: 0x40, 120: 0x2e, 121: 0xa2, 124: 0x7c,
    126: 0x201a, 127: 0x2044, 129: 0xa4, 130: 0x2039,
    131: 0x203a, 132: 0xf001, 133: 0xf002, 134: 0x2021,
    135: 0xb0, 137: 0x30, 138: 0x31, 139: 0x32, 140: 0x33,
    141: 0x34, 142: 0x35, 143: 0x36, 144: 0x37, 145: 0x38,
    146: 0x39, 147: 0x2dc, 148: 0xb6, 151: 0xbf, 152: 0x2da,
    154: 0x152, 156: 0x2030, 157: 0xd3, 158: 0xd4, 159: 0x2022,
    160: 0xff, 161: 0x5c, 163: 0xdf, 164: 0xab, 165: 0x2026,
    166: 0xb4, 167: 0xd8, 168: 0x60, 169: 0xa7, 170: 0x24,
    171: 0xa1, 172: 0x2122, 173: 0x23, 175: 0x5b, 176: 0x7b,
    177: 0x5d, 178: 0x7d, 179: 0xb4, 13: 0xaa, 180: 0xac,
    181: 0xab, 182: 0xa6, 183: 0x00, 184: 0x00
}

satluj = {
    0: 0xfd, 11: 0xc0, 15: 0xfa, 17: 0xc1, 21: 0xc2,
    25: 0xc3, 26: 0xd4, 27: 0xd5, 28: 0xd6, 29: 0xd7,
    30: 0xd8, 31: 0xd9, 32: 0xda, 33: 0xdb, 34: 0xdc,
    35: 0xde, 36: 0xdf, 37: 0xe0, 38: 0xe1, 39: 0xe2,
    40: 0xe3, 41: 0xe4, 42: 0xe5, 43: 0xe6, 44: 0xe7,
    45: 0xe8, 46: 0xe9, 47: 0xea, 48: 0xeb, 49: 0xec,
    50: 0xed, 51: 0xee, 52: 0xef, 53: 0xf0, 54: 0xf1,
    55: 0xf2, 56: 0xf3, 57: 0xf4, 58: 0xf5, 59: 0xf6,
    60: 0xf7, 61: 0xf8, 62: 0xff, 69: 0xcc, 70: 0x7a,
    72: 0x7b, 73: 0x7c, 74: 0xc9, 77: 0x7d, 78: 0xa5,
    81: 0xa7, 82: 0xbf, 85: 0xba, 94: 0xc5, 96: 0xbb,
    97: 0xc7, 99: 0xc6, 101: 0xc4, 106: 0xb1, 107: 0xc8,
    109: 0xb6, 111: 0xcb, 115: 0xcf, 120: 0xa2, 122: 0xcd,
    124: 0xa3, 125: 0xa8, 126: 0x30, 127: 0x31, 129: 0x32,
    130: 0x33, 131: 0x34, 132: 0x35, 133: 0x36, 134: 0x37,
    135: 0x38, 136: 0x39, 137: 0x30, 138: 0x31, 139: 0x32,
    140: 0x33, 141: 0x34, 142: 0x35, 143: 0x36, 144: 0x37,
    145: 0x38, 146: 0x39, 147: 0xf9, 149: 0x57, 151: 0x2039,
    152: 0xc7, 154: 0x152, 156: 0x2030, 157: 0xd3, 158: 0xd4,
    160: 0xff, 161: 0x3a, 167: 0xce, 168: 0xd2, 170: 0xd3,
    172: 0x2122, 173: 0x23, 179: 0xb4, 180: 0x00, 181: 0x00,
    182: 0x00
}

asees = {
    0: 0xc5, 1: 0x2039, 3: 0xc6, 6: 0xa1, 7: 0xe5, 8: 0x3e,
    11: 0x54, 15: 0x55, 17: 0x6e, 21: 0x4a, 25: 0x3b,
    26: 0x6a, 27: 0x65, 28: 0x79, 29: 0x72, 30: 0x78,
    31: 0x43, 32: 0x75, 33: 0x53, 34: 0x69, 35: 0x4d,
    36: 0x52, 37: 0x4e, 38: 0x6d, 39: 0x76, 40: 0x59,
    41: 0x44, 42: 0x73, 43: 0x45, 44: 0x64, 45: 0x58,
    46: 0x42, 47: 0x67, 48: 0x63, 49: 0x70, 50: 0x47,
    51: 0x77, 52: 0x3a, 53: 0x6f, 54: 0x62, 55: 0x74,
    56: 0x56, 57: 0x50, 58: 0x5c, 59: 0x7d, 60: 0x49,
    61: 0x7c, 62: 0x2b, 63: 0x61, 65: 0x48, 66: 0x51,
    68: 0xa7, 69: 0x71, 70: 0xae, 72: 0xe7, 73: 0x2020,
    74: 0x5f, 76: 0xcf, 77: 0x153, 78: 0x2dc, 79: 0xce,
    82: 0x7a, 85: 0x41, 86: 0x2c6, 89: 0x5a, 90: 0x7e,
    91: 0xa4, 94: 0x6b, 96: 0x4b, 97: 0x66, 99: 0x68,
    103: 0x5b, 106: 0x7b, 107: 0xa8, 109: 0x2f, 111: 0x3f,
    113: 0x27, 115: 0x22, 120: 0x2e, 124: 0x5d, 125: 0xd2,
    126: 0xfa, 127: 0xf1, 129: 0xf2, 130: 0xf3, 131: 0xf4,
    132: 0xf5, 133: 0xf6, 134: 0xf7, 135: 0xf8, 136: 0xf9,
    137: 0x30, 138: 0x31, 139: 0x32, 140: 0x33, 141: 0x34,
    142: 0x35, 143: 0x36, 144: 0x37, 145: 0x38, 146: 0x39,
    147: 0x192, 149: 0x57, 151: 0x2039, 152: 0xc7, 154: 0x152,
    155: 0x201a, 156: 0x2030, 157: 0xd3, 158: 0xd4, 160: 0xff,
    161: 0x4c, 162: 0xda, 163: 0x6c, 167: 0x46, 168: 0x2018,
    170: 0x2019, 172: 0x201c, 173: 0x201d, 174: 0x40
}

joy = {
    0: 0x2dd, 11: 0x54, 15: 0x55, 16: 0x2d9, 17: 0x6e,
    21: 0x4a, 25: 0x3b, 26: 0x6a, 27: 0x65, 28: 0x79,
    29: 0x72, 30: 0x78, 31: 0x43, 32: 0x75, 33: 0x53,
    34: 0x69, 35: 0x4d, 36: 0x52, 37: 0x4e, 38: 0x6d,
    39: 0x76, 40: 0x59, 41: 0x44, 42: 0x73, 43: 0x45,
    44: 0x64, 45: 0x58, 46: 0x42, 47: 0x67, 48: 0x63,
    49: 0x70, 50: 0x47, 51: 0x77, 52: 0x3a, 53: 0x6f,
    54: 0x62, 55: 0x74, 56: 0x56, 57: 0xd9, 58: 0x131,
    59: 0x2c6, 60: 0x2dc, 61: 0xaf, 62: 0x2c7, 66: 0x51,
    67: 0x2211, 69: 0xc3, 70: 0x71, 74: 0x60, 75: 0x2026,
    79: 0x203a, 82: 0x7a, 83: 0xf8, 84: 0x2265, 88: 0xe6,
    89: 0xba, 94: 0x6b, 95: 0x2248, 96: 0xaa, 97: 0x66,
    98: 0xab, 99: 0x68, 100: 0x2206, 101: 0x5d, 102: 0x192,
    103: 0x5b, 104: 0x221e, 105: 0x3c0, 106: 0x7b, 107: 0xb1,
    108: 0xbb, 109: 0x2f, 110: 0x2202, 111: 0x3f, 112: 0x2b,
    113: 0xd8, 114: 0x27, 115: 0x22, 116: 0x2126, 117: 0x153,
    120: 0xd5, 122: 0x2e, 126: 0xa0, 127: 0xa1, 128: 0x49,
    129: 0xa2, 130: 0xa3, 131: 0xa4, 133: 0xa6, 134: 0xa7,
    136: 0xa9, 137: 0x30, 138: 0x31, 139: 0x32, 140: 0x33,
    141: 0x34, 142: 0x35, 143: 0x36, 144: 0x37, 145: 0x38,
    146: 0x39, 147: 0x2d8, 167: 0x152, 168: 0x201c, 170: 0x201d,
    172: 0x161, 173: 0x40, 179: 0xa5, 13: 0x2122, 180: 0xa8,
    181: 0xb4, 185: 0x57, 186: 0x2db, 183: 0x2da, 184: 0xb8
}

gurbaniLipi = {
    126: 0x30, 127: 0x31, 129: 0x32, 130: 0x33, 131: 0x34,
    132: 0x35, 133: 0x36, 134: 0x37, 135: 0x38, 136: 0x39,
    137: 0x30, 138: 0x31, 139: 0x32, 140: 0x33, 141: 0x34,
    142: 0x35, 143: 0x36, 144: 0x37, 145: 0x38, 146: 0x39
}

# -----------------------------
# Compositions (unchanged)
# -----------------------------
moveAcrossChaSet = [
    [[66], [67], [118, 26]],
    [[69], [70], [118, 53]],
    [[72], [118, 32]],
    [[73], [118, 37]],
    [[74], [75], [118, 55]],
    [[76], [118, 52, 118, 52]],
    [[77], [118, 42]],
    [[78], [118, 46]],
    [[71], [69, 63], [69, 64], [63, 118, 53], [64, 118, 53]],
]

ikOnkarVersion1 = [[0], [1,2], [1], [127,9]]
ikOnkarVersion2 = [[3], [4,5], [4], [127,10]]
ikOnkarVersion3 = [[6]]

compositions = (moveAcrossChaSet + [
    ikOnkarVersion1,
    ikOnkarVersion2,
    ikOnkarVersion3,
    ikOnkarVersion1 + ikOnkarVersion2 + ikOnkarVersion3 + [[7],[8]],
    [[127],[128]],
    [[85],[86]],
    [[99],[100]],
    [[97],[98]],
    [[109],[110]],
    [[111],[112]],
    [[94],[95]],
    [[79],[118,52]],
    [[92],[90,85]],
    [[18],[17,94]],
    [[18,85],[17,96]],
    [[22],[97,21],[98,21]],
    [[23],[21,99]],
    [[12],[11,103]],
    [[14],[11,106]],
    [[15],[16]],
    [[15],[16],[9],[10]],
    [[24],[21,109],[21,110]],
    [[19],[17,111],[17,112]],
    [[20],[17,117],[17,115]],
    [[62],[54,63]],
    [[57],[25,63]],
    [[58],[28,63]],
    [[59],[29,63]],
    [[60],[34,63]],
    [[61],[48,63]],
    [[124],[120,120],[125]],
    [[106],[107],[108]],
    [[103],[104],[105]],
    [[120],[122],[123],[121]],
    [[96],[94,85]],
    [[90],[91]],
    [[89],[90],[91],[88]],
    [[0],[1,2],[1]],
    [[63],[64]],
    [[82],[83],[84],[81]],
    [[147],[46,106,82],[46,82,106],[148,82]],
    [[148],[46,106]],
    [[154],[155],[156],[157],[158]],
    [[68],[118,26,106]],
    [[101],[102],[99,85],[100,85]],
    [[113],[114]],
    [[115],[116],[117]],
    [[168],[169]],
    [[170],[171]],
    [[173],[174]],
    [[152],[153]],
    [[161],[162]],
    [[163],[164],[165]],
    [[149],[53,103],[53,104]],
    [[179],[27,69],[27,118,53]],
    [[12],[11,103]],
    [[180],[54,106],[54,107]],
    [[181],[54,103],[54,104]],
    [[182],[54,82],[83]],
    [[183],[43,103],[43,104]],
    [[184],[32,103],[32,104]],
    [[185],[186],[26,111]],
    [[13],[12,85],[11,103,85]],
])

# -----------------------------
# Build font configurations
# -----------------------------
def make_codes(*configs: Dict[int,int]) -> List[Any]:
    max_index = 0
    for cfg in configs:
        if cfg:
            max_index = max(max_index, max(cfg.keys()))
    arr = [None] * (max_index + 1)
    for cfg in configs:
        for k, v in cfg.items():
            arr[int(k)] = v
    return arr

fontConvertorConfigs = {
    "Unicode": {
        "moveRightCharacters": [97],
        "characterCodes": make_codes(unicodeMapping)
    },
    "AnmolUni": {
        "moveRightCharacters": [97],
        "characterCodes": make_codes(unicodeMapping)
    },
    "AnmolLipi": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(anmolMapping)
    },
    "DrChatrikWeb": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(drChatrikMappings)
    },
    "Awaze": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(awazeMappings)
    },
    "Satluj": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(satluj)
    },
    "Asees": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(asees)
    },
    "Joy": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(joy)
    },
    "GurbaniLipi": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(anmolMapping, gurbaniLipi)
    },
    "AmritLipi": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(anmolMapping)
    },
    "AmarLipi": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(anmolMapping)
    },
    "GurumukhiLys": {
        "moveRightCharacters": [],
        "characterCodes": make_codes(asees)
    },
}

# -----------------------------
# Mapper builder
# -----------------------------
def get_mapper(to_cfg: Dict[str,Any], from_cfg: Dict[str,Any], compositions_list: List[Any], moveAcrossCharSet):
    to_codes = to_cfg["characterCodes"]
    from_codes = from_cfg["characterCodes"]
    mapping_length = max(len(to_codes), len(from_codes))
    mapper: Dict[str,str] = {}

    # single char mapping
    for i in range(mapping_length):
        from_char = from_codes[i] if i < len(from_codes) else None
        to_char = to_codes[i] if i < len(to_codes) else None
        if from_char and to_char:
            mapper[get_char_from_unicode(from_char)] = get_char_from_unicode(to_char)

    # composition mapping
    max_width = 1
    for comp in compositions_list:
        to_candidates = get_composition_characters(comp, to_codes)
        if to_candidates:
            to_char = to_candidates[0]
            from_candidates = get_composition_characters(comp, from_codes)
            for from_char in from_candidates:
                if from_char:
                    max_width = max(max_width, len(from_char))
                    if from_char not in mapper:
                        mapper[from_char] = to_char

    # moveRight/moveLeft
    from_move_right = from_cfg.get("moveRightCharacters", [])
    to_move_right = to_cfg.get("moveRightCharacters", [])
    move_left_char_indexes = [i for i in from_move_right if i not in to_move_right]
    move_right_char_indexes = [i for i in to_move_right if i not in from_move_right]

    move_left_chars = []
    for idx in move_left_char_indexes:
        if idx < len(to_codes) and to_codes[idx]:
            move_left_chars.append(get_char_from_unicode(to_codes[idx]))
    move_right_chars = []
    for idx in move_right_char_indexes:
        if idx < len(to_codes) and to_codes[idx]:
            move_right_chars.append(get_char_from_unicode(to_codes[idx]))

    move_across = []
    for comp in moveAcrossCharSet:
        chars = get_composition_characters(comp, to_codes)
        move_across.extend(chars)

    return {
        "mapper": mapper,
        "maxWidth": max_width,
        "moveLeftChars": move_left_chars,
        "moveRightChars": move_right_chars,
        "moveAcrossCharacters": move_across
    }

# -----------------------------
# Main convert function
# -----------------------------
def convert(str_input: str, to_font_name: str, from_font_name: str) -> str:
    to_cfg = fontConvertorConfigs.get(to_font_name)
    from_cfg = fontConvertorConfigs.get(from_font_name)
    if not to_cfg or not from_cfg:
        return str_input
    mapper_config = get_mapper(to_cfg, from_cfg, compositions, moveAcrossChaSet)
    return convert_string_using_mapper(mapper_config, str_input)

# -----------------------------
# Class wrapper
# -----------------------------
class PunjabiFontConverter:
    def convert_font(self, text: str, from_font: str, to_font: str) -> str:
        return convert(text, to_font, from_font)

# End of file