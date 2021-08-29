from typing import *
from PIL import Image
from bitarray import bitarray
from os import listdir, makedirs
from os.path import realpath, dirname, join, isfile, basename, splitext, exists


def get_letter_borders(img, marker_line):
    result = []
    inside_character = False
    for i in range(0, img.width):
        p = img.getpixel((i, marker_line))

        if p == (255, 0, 0) or p == (255, 0, 0, 255):
            if not inside_character:
                inside_character = True
                start = i
        elif p == (0, 255, 0) or p == (0, 255, 0, 255):
            if inside_character:
                result.append((start, i))
                inside_character = False
            else:
                result.append((i, i))

    return result


def old_build_tables(img, bounds, y_pos):
    jumps, widths, chars = [], [], []
    cursor = 0
    counter = 0
    for i in range(0, 256):
        table_index = get_char_mapping(i)
        if table_index != -1:
            (start, end) = bounds[table_index]
            width = end - start + 1
            jumps.append((f"\n/*{chr(i)}*/" if i % 8 == 0 and i else "") + str(cursor).rjust(5))
            widths.append((f"\n/*{chr(i)}*/" if i % 8 == 0 and i else "") + str(width).rjust(2))

            for x in range(start, end + 1):
                bits = bitarray(endian="little")
                for y in range(y_pos, y_pos + 8):
                    p = img.getpixel((x, y))
                    if p == (0, 0, 0):
                        bits.append(1)
                    else:
                        bits.append(0)
                byte = bits.tobytes()[0]

                if x == start:
                    b = bytearray([i])
                    comment = "/* " + b.decode("iso8859-15") + " */  "
                else:
                    comment = ""

                chars.append(("\n    " if x == start and counter else "") + comment + f"{byte:#04x}")

            cursor += width
            counter += 1
        else:
            jumps.append(("\n    " if i % 16 == 0 and i else "") + str(-1).rjust(5))
            widths.append(("\n    " if i % 16 == 0 and i else "") + str(-1).rjust(2))

    jumps_str = ", ".join(jumps)
    widths_str = ", ".join(widths)
    chars_str = ", ".join(chars)

    return jumps_str, widths_str, chars_str


def build_tables(img: Image.Image, bounds, y_pos, true_c: str, false_c: str):
    jumps, widths, chars = [], [], []
    # line zero is for guide
    height = img.height - 1
    cursor = 0
    counter = 0
    jump = 0
    for i in range(0, 256):
        table_index = get_char_mapping(i)
        if table_index != -1:
            (start, end) = bounds[table_index]
            width = end - start + 1
            jumps.append((f"\n/*{chr(i)}*/" if i % 8 == 0 and i else "") + str(jump).rjust(5))
            widths.append((f"\n/*{chr(i)}*/" if i % 8 == 0 and i else "") + str(width).rjust(2))
            jump += width * height

            letter = []
            comment = "/* " + chr(i) + " */\n"
            for y in range(y_pos, y_pos + height):
                row = []
                for x in range(start, end + 1):
                    p = img.getpixel((x, y))
                    if p == (0, 0, 0) or p == (0, 0, 0, 255):
                        entry = true_c
                    else:
                        entry = false_c
                    if y == y_pos and x == start:
                        row.append(comment + entry)
                    else:
                        row.append(entry)
                letter.append(f"{', '.join(row)}")
            chars.append(",\n".join(letter))
        else:
            jumps.append(("\n    " if i % 8 == 0 and i else "") + str(-1).rjust(5))
            widths.append(("\n    " if i % 8 == 0 and i else "") + str(-1).rjust(2))
    jumps_str = ", ".join(jumps)
    widths_str = ", ".join(widths)
    chars_str = ", \n".join(chars)
    return jumps_str, widths_str, chars_str, height


# ISO-8859-15
def get_char_mapping(v):
    # Special supported characters from upper block
    # if v == 0xc4: return 94  # Ä
    # if v == 0xd6: return 95  # Ö
    # if v == 0xdc: return 96  # Ü
    # if v == 0xe4: return 97  # ä
    # if v == 0xf6: return 98  # ö
    # if v == 0xdf: return 99  # ß
    # if v == 0xfc: return 100  # ü
    # if v == 0xa4: return 101  # €

    # ASCII block (non control chars up to 127)
    if 32 <= v <= 126:
        return v - 32

    # No mapping
    return -1


#
# def print_char(img, bounds, variant):
#     index = get_char_mapping(0xdf)
#
#     if index != -1:
#         (start, end) = bounds[index]
#
#         for y in range(variant["y_pos"], variant["y_pos"] + 8):
#             for x in range(start, end + 1):
#                 p = img.getpixel((x, y))
#                 if p == (0, 0, 0):
#                     print("x", end='')
#                 else:
#                     print(" ", end='')
#             print("")
#     else:
#         print("No character data.")


if __name__ == '__main__':
    here = dirname(realpath(__file__))
    input_dir = join(here, "input")
    input_files = [join(input_dir, f) for f in listdir(input_dir) if
                   isfile(join(input_dir, f)) and f.lower().endswith(".png")]

    define_true = "x"
    define_false = "o"
    if not exists('output'):
        makedirs('output')

    for input_file in input_files:
        img = Image.open(input_file)
        font_name = splitext(basename(input_file))[0].capitalize()

        bounds = get_letter_borders(img, 0)

        jumps, widths, chars, height = build_tables(img, bounds, 1, define_true, define_false)

        # print_char(img, bounds, v, 0xdf)

        h_file = f"""
#ifndef {font_name.upper()}_H_
#define {font_name.upper()}_H_

#include "pixelfont.h"

class {font_name}: public PixelFont {{

private:
    static const bool chars[];
    static const int jumps[];
    static const int widths[];
    static const int height = {height};

    const bool *get_chars() override {{
        return chars;
    }}

    const int* get_jumps() override {{
        return jumps;
    }}

    const int* get_widths() override {{
        return widths;
    }}
    
    int get_font_height() override {{
        return height;
    }}
}};

#define {define_true} true
#define {define_false} false
const bool {font_name}::chars[] = {{
{chars}
}};
#undef {define_true}
#undef {define_false}

const int {font_name}::jumps[] = {{
{jumps}
}};

const int {font_name}::widths[] = {{
{widths}
}};
#endif //{font_name.upper()}_H_
"""
        output_file = join(here, "output", font_name + ".h")
        print(basename(input_file) + " -> " + basename(output_file))

        f = open(output_file, "w")
        f.write(h_file)
        f.close()
