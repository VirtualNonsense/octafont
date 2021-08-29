from PIL import Image, ImageDraw, ImageFont
from os import listdir, makedirs
from os.path import realpath, dirname, join, isfile, basename, splitext, exists


def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    # if text_string == " ":
    return font.getsize(text_string)

    # text_width = font.getmask(text_string).getbbox()[2]
    # text_height = font.getmask(text_string).getbbox()[3] + descent
    #
    # return text_width, text_height


def binarize(image_to_transform, threshold):
    # now, lets convert that image to a single greyscale image using convert()
    output_image = image_to_transform.convert("L")
    # the threshold value is usually provided as a number between 0 and 255, which
    # is the number of bits in a byte.
    # the algorithm for the binarization is pretty simple, go through every pixel in the
    # image and, if it's greater than the threshold, turn it all the way up (255), and
    # if it's lower than the threshold, turn it all the way down (0).
    # so lets write this in code. First, we need to iterate over all of the pixels in the
    # image we want to work with
    for x in range(output_image.width):
        for y in range(output_image.height):
            # for the given pixel at w,h, lets check its value against the threshold
            if output_image.getpixel((x, y)) < threshold:  # note that the first parameter is actually a tuple object
                # lets set this to zero
                output_image.putpixel((x, y), 0)
            else:
                # otherwise lets set this to 255
                output_image.putpixel((x, y), 255)
    # now we just return the new image
    return output_image


if __name__ == '__main__':
    here = dirname(realpath(__file__))
    input_dir = join(here, "input")
    output_dir = "output"
    if not exists(output_dir):
        makedirs(output_dir)

    font_name = "/usr/share/fonts/opentype/fira/FiraMono-Regular.otf"
    font_size = 20

    # define letters to draw
    letters = r" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvxyz"

    # script
    font = ImageFont.truetype(font_name, font_size)
    height = 0
    width = 0
    for char in letters:
        dim = get_text_dimensions(char, font)
        width += dim[0]
        if height < dim[1]:
            height = dim[1]
    img = Image.new("RGB", (width, height), color="white")
    drawn_image = ImageDraw.Draw(img)
    drawn_image.fontmode = "1"
    former_letters_width = 0
    for char in letters:
        drawn_image.text(xy=(former_letters_width, 0), text=char, font=font, fill="black")
        drawn_image.point((former_letters_width, 0), (0, 255, 0,))
        former_letters_width += get_text_dimensions(char, font)[0]
        drawn_image.point((former_letters_width - 1, 0), (255, 0, 0,))
    img.save(join(here, output_dir, f"{splitext(font_name)[0].split('/')[-1]}{font_size}.png"))
