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
