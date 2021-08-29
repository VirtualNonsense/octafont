//
// Created by anachtmann on 8/23/21.
//
#ifndef FLIPDOT_PIXELFONT_H
#define FLIPDOT_PIXELFONT_H

#include <cstdint>
#include <cstdlib>

struct letter {
    int height;
    int width;
    int start_index;
    const bool *letter;
};


class PixelFont {

public:
    virtual ~PixelFont() = default;

    bool has_char(char c) {
        return get_jumps()[(int) c] != -1;
    }

    int get_width(char c) {
        return get_widths()[(int) c];
    };

    int get_height() {
        return get_font_height();
    };

    int get_letter(char c, letter *letter) {
        Serial.print("input: ");
        Serial.println((int) c);
        if (!has_char(c)) {
            return -1;
        }
        letter->start_index = get_jumps()[(int) c];
        letter->letter = get_chars();
        letter->height = get_height();
        letter->width = get_width(c);
        return 0;
    }

    static uint8_t get_undercut(PixelFont &font1, char c1, PixelFont &font2, char c2) {
//        if (!font1.has_char(c1) || !(font2.has_char(c2))) {
//            return 0;
//        }
//
//        uint8_t c1_width = font1.get_width(c1);
//        uint8_t octet1 = font1.get_letter(c1, c1_width - 1);
//        uint8_t octet2 = font2.get_letter(c2, 0);
//
//        if (octet1 & octet2) {
//            return 0;
//        }
//        if (octet1 & (octet2 >> 1)) {
//            return 0;
//        }
//        if (octet1 & (octet2 << 1)) {
//            return 0;
//        }
//
//        return 1;
        return 0;
    }

private:
    virtual const bool *get_chars() = 0;

    virtual const int *get_widths() = 0;

    virtual const int *get_jumps() = 0;

    virtual int get_font_height() = 0;

};

#endif //FLIPDOT_PIXELFONT_H
