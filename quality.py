from PIL import Image


def improve_text_in_image(image: Image) -> Image:
    """
    Improve the quality of the text in the image.
    :param image:
    :return:
    """
    black = (0, 0, 0)
    white = (255, 255, 255)
    threshold = (160, 160, 160)
    image = image.convert("LA")
    pixels = image.getdata()
    new_pixels = []

    for pixel in pixels:
        if pixel < threshold:
            new_pixels.append(black)
            # new_pixels.append(pixel)
        else:
            new_pixels.append(white)
    # return Image.new(image.mode, image.size)
    image = Image.new("RGB", image.size)
    image.putdata(new_pixels)
    return image


"""
A4 size
3508 x 2480 px
297 x 210 mm
px: 595 x 842	794 x 1123	1240 x 1754	2480 x 3508
px: 72 PPI	96 PPI	150 PPI	300 PPI
8.3 x 11.7 inches (8.27 x 11.69)
"""
if __name__ == '__main__':
    image_low_quality = Image.open("low_quality.png")
    s1 = image_low_quality.size
    print(image_low_quality.size, s1[0] / s1[1])
    image_full_size = Image.open("full_size.png")
    s2 = image_full_size.size
    print(image_full_size.size, s2[0] / s2[1])
    # resize the image to a new size
    new_width = 1240
    w_percent = (new_width / float(s1[0]))
    new_height = int((float(s1[1]) * float(w_percent)))
    new_sized_img = image_low_quality.resize((new_width, new_height), Image.ANTIALIAS)
    new_sized_img.show()
    new_sized_img = improve_text_in_image(new_sized_img)
    new_sized_img.show()
