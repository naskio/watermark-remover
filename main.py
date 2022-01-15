from typing import Dict, List
from PIL import Image
from pathlib import Path
import zlib
import numpy
from pikepdf import Pdf, PdfImage, Name
import cv2
import zipfile
import io
import numpy as np
# from quality import improve_text_in_image
import fire


def replace_images_in_zip(in_zip: Path, out_zip: Path, replacements: Dict[str, io.BytesIO]) -> Path:
    """
    Replace images in zip
    :param in_zip:
    :param out_zip:
    :param replacements:
    :return:
    """

    with zipfile.ZipFile(in_zip, 'r') as zin:
        with zipfile.ZipFile(out_zip, 'w') as zout:
            zout.comment = zin.comment  # preserve the comment
            for item in zin.infolist():
                # copy all files except the images to replace
                if item.filename not in replacements.keys():
                    with zout.open(item.filename, 'w') as f:
                        f.write(zin.read(item.filename))
                else:  # replace the image
                    with zout.open(item.filename, 'w') as f:
                        f.write(replacements[item.filename].getvalue())
    return out_zip


def remove_watermark_from_cv_image(img: numpy.ndarray) -> numpy.ndarray:
    """
    Remove watermark from open cv image
    :param img:
    :return: image without watermark
    """
    # convert image to hsv colorspace
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    # threshold saturation image
    thresh1 = cv2.threshold(s, 92, 255, cv2.THRESH_BINARY)[1]
    # threshold value image and invert
    thresh2 = cv2.threshold(v, 128, 255, cv2.THRESH_BINARY)[1]
    thresh2 = 255 - thresh2
    # combine the two threshold images as a mask
    mask = cv2.add(thresh1, thresh2)
    # use mask to remove lines in background of input
    result = img.copy()
    result[mask == 0] = (255, 255, 255)
    return result


def hex_to_rbg(hex_color: str) -> tuple:
    """
    Convert hex color to rgb
    example: #FFFFFF to (255, 255, 255)
    :param hex_color:
    :return:
    """
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return r, g, b


def rgb_to_hex(rgb_color: tuple) -> str:
    """
    Convert rgb color to hex
    example: (255, 255, 255) to #FFFFFF
    :param rgb_color:
    :return:
    """
    r, g, b = rgb_color
    return '#%02x%02x%02x' % (r, g, b)


def hex_to_rgba(hex_color: str, alpha: int = 255):
    """
    Convert hex color to rgba
    example: #FFFFFF to (255, 255, 255, 255)
    :param hex_color:
    :param alpha:
    :return:
    """
    r, g, b = hex_to_rbg(hex_color)
    return r, g, b, alpha


def rgba_to_hex(rgba_color: tuple):
    """
    Convert rgba color to hex
    example: (255, 255, 255, 128) to #FFFFFF
    :param rgba_color:
    :return:
    """
    r, g, b, a = rgba_color
    return '#%02x%02x%02x' % (r, g, b)


def replace_colors_in_image(image: Image, replacements: Dict[str, str]) -> Image:
    """
    Replace colors in image with new colors from replacements {to_replace_hex: new_hex}
    example = {
        '#f0f0f0': '#FFFFFF',
        '#c0c0c0': '#FFFFFF',
    }
    :param image:
    :param replacements:
    :return:
    """
    image = image.convert('RGBA')
    data = np.array(image)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability
    for old_c, new_c in replacements.items():
        old_color = hex_to_rbg(old_c)
        new_color = hex_to_rbg(new_c)
        white_areas = (red == old_color[0]) & (blue == old_color[1]) & (green == old_color[2])
        data[..., :-1][white_areas.T] = new_color
    return Image.fromarray(data)


def generate_output_path(input_path: Path) -> Path:
    """
    Generate output_path from input_path
    :param input_path:
    :return:
    """
    return input_path.parent / (input_path.stem + f"_generated{input_path.suffix}")


def remove_watermark_from_pdf(input_file: Path, output_file: Path, use_colors_replacement: bool = False) -> str:
    """
    Remove watermark from pdf and save to output_file
    :param input_file:
    :param output_file:
    :param use_colors_replacement:
    :return:
    """
    pdf = Pdf.open(input_file)
    for page in pdf.pages:
        for image_key in page.images.keys():
            raw_image = page.images[image_key]
            pdf_image = PdfImage(raw_image)
            pil_image = pdf_image.as_pil_image()
            pil_image = remove_watermark_from_pil_image(pil_image, use_colors_replacement)
            raw_image.write(zlib.compress(pil_image.tobytes()), filter=Name("/FlateDecode"))
    pdf.save(output_file)
    return str(output_file)


def remove_watermark_from_docx(input_file: Path, output_file: Path, use_colors_replacement: bool = False) -> str:
    """
    Remove watermark from docx and save to output_file
    :param input_file:
    :param output_file:
    :param use_colors_replacement:
    :return:
    """
    z = zipfile.ZipFile(input_file)
    all_files = z.namelist()
    # get all files in word/media/ directory
    images = list(filter(lambda x: x.startswith('word/media/'), all_files))
    replacements = {}
    for image in images:
        with z.open(image) as f:
            pil_image = Image.open(f)
            # pil_image = improve_text_in_image(pil_image)
            pil_image = remove_watermark_from_pil_image(pil_image, use_colors_replacement)
            image_file_tmp = io.BytesIO()
            pil_image.save(image_file_tmp, format="PNG")
            replacements[image] = image_file_tmp
    z.close()
    return str(replace_images_in_zip(input_file, output_file, replacements))


def remove_watermark_from_pil_image(image: Image, use_colors_replacement: bool = False) -> Image:
    """
    Remove watermark from pil image
    :param image:
    :param use_colors_replacement:
    :return:
    """
    if use_colors_replacement:
        return replace_colors_in_image(image, {
            '#f0f0f0': '#FFFFFF',
            '#c0c0c0': '#FFFFFF',
        })
    else:
        # noinspection PyTypeChecker
        opencv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        opencv_image = remove_watermark_from_cv_image(opencv_image)
        image = Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
        return image


def remove_watermark_from_image(input_file: Path, output_file: Path, use_colors_replacement: bool = False) -> str:
    """
    Remove watermark from image
    :param input_file:
    :param output_file:
    :param use_colors_replacement:
    :return:
    """
    pil_image = Image.open(input_file)
    pil_image = remove_watermark_from_pil_image(pil_image, use_colors_replacement)
    pil_image.save(output_file)
    return str(output_file)


def main(input_file: str, output_file: str = None, use_colors_replacement: bool = False) -> str:
    """
    Entry point
    :param input_file:
    :param output_file:
    :param use_colors_replacement:
    :return:
    """
    input_path = Path(input_file)
    if not input_path or not input_path.exists():
        raise FileNotFoundError(f"File {input_path} does not exist")
    # generate output path
    if not output_file:
        output_path = generate_output_path(input_path)
    else:
        output_path = Path(output_file)
    # remove output file if it exists
    if output_path.exists():
        output_path.unlink()
    # remove watermark
    if str(input_path.suffix).lower() == ".pdf":
        return remove_watermark_from_pdf(input_path, output_path, use_colors_replacement)
    elif str(input_path.suffix).lower() == ".docx":
        return remove_watermark_from_docx(input_path, output_path, use_colors_replacement)
    elif str(input_path.suffix).lower() in [".png", ".jpg", ".jpeg"]:
        return remove_watermark_from_image(input_path, output_path, use_colors_replacement)
    else:
        raise Exception(f"Unsupported file type: {input_path.suffix}")


def mmain(input_files: List[str], output_dir: str = None, use_colors_replacement: bool = False) -> List[str]:
    """
    Entry point
    :param input_files:
    :param output_dir:
    :param use_colors_replacement:
    :return:
    """
    output_files = []
    for input_file in input_files:
        input_path = Path(input_file)
        if not output_dir:
            output_dir = input_path.parent
        output_file = output_dir / (input_path.stem + f"_generated{input_path.suffix}")
        output_file = main(input_file, output_file, use_colors_replacement)
        output_files.append(output_file)
    return output_files


if __name__ == "__main__":
    fire.Fire(main)
