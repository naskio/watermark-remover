from typing import Dict, List, Union, Callable
from PIL import Image
from pathlib import Path
import zlib
import numpy
from pikepdf import Pdf, PdfImage, Name, parse_content_stream, unparse_content_stream, ContentStreamInstruction
from decimal import Decimal
import cv2
import zipfile
import io
import numpy as np
# from quality import improve_text_in_image
import fire
from enum import Enum
from logging import getLogger
from sentry_sdk import capture_message

logger = getLogger(__name__)


def w_sentry(fn: Callable, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
        return True
    except Exception as e:
        logger.info("Sentry setup issue", exc_info=e)
        return False


class MethodChoice(Enum):
    geos = "GEOS"
    colors_replacement = "Replace colors"
    openCV2 = "OpenCV2"

    @staticmethod
    def from_str(label):
        if label in ('geos',):
            return MethodChoice.geos
        elif label in ('colors_replacement',):
            return MethodChoice.colors_replacement
        elif label in ('openCV2',):
            return MethodChoice.openCV2
        else:
            raise NotImplementedError


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


def remove_watermark_from_pil_image(image: Image, method_choice: MethodChoice,
                                    replacements: Dict[str, str] = None) -> Image:
    """
    Remove watermark from pil image
    :param image:
    :param method_choice:
    :param replacements:
    :return:
    """
    if method_choice == MethodChoice.openCV2:
        # noinspection PyTypeChecker
        opencv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        opencv_image = remove_watermark_from_cv_image(opencv_image)
        image = Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
        return image
    else:
        return replace_colors_in_image(image, replacements or {
            '#f0f0f0': '#FFFFFF',
            '#c0c0c0': '#FFFFFF',
            '#b4b4fe': '#FFFFFF',
        })


def generate_output_path(input_path: Path) -> Path:
    """
    Generate output_path from input_path
    :param input_path:
    :return:
    """
    return input_path.parent / (input_path.stem + f"_generated{input_path.suffix}")


def remove_tj_maj(instructions: List[ContentStreamInstruction], tj_start_with: Union[List[bytes], str]) -> \
        List[ContentStreamInstruction]:
    """Remove all "TJ" operators if it contains tj_start_with from PDF."""
    dest = tj_start_with
    if isinstance(tj_start_with, str):
        dest = list(map(lambda c: bytes(c, 'utf-8'), tj_start_with))
    for i in range(len(instructions)):
        instruction = instructions[i]
        op = instruction.operator.__str__()
        if op == 'TJ':
            source1 = []
            source2 = []
            for j in range(len(instruction.operands[0])):
                if type(instruction.operands[0][j]) not in [int, float, Decimal]:
                    operand_str = instruction.operands[0][j].__str__()
                    source2.append(bytes(operand_str, 'utf-8'))
                    for k in range(len(operand_str)):
                        source1.append(bytes(operand_str[k], 'utf-8'))
            for j in range(len(dest)):
                if dest[j] != source1[j]:
                    break
                if j == len(dest) - 1:
                    instructions[i] = None
            for j in range(len(dest)):
                if dest[j] != source2[j]:
                    break
                if j == len(dest) - 1:
                    instructions[i] = None
    return [x for x in instructions if x is not None]


def remove_tjs_min(instructions: List[ContentStreamInstruction], text: Union[List[bytes], str]) -> \
        List[ContentStreamInstruction]:
    """Remove all successive "Tj" if it combined equals to text from PDF."""
    indexes = []
    found = ""
    for i in range(len(instructions)):
        instruction = instructions[i]
        op = instruction.operator.__str__()
        if op == 'Tj':
            indexes.append(i)
            found += instruction.operands[0].__str__()
        else:
            if found:
                if not text.startswith(found):
                    indexes = []
                    found = ""
                elif text == found:
                    for index in indexes:
                        instructions[index] = None
                    indexes = []
                    found = ""
            else:
                indexes = []
                found = ""
    return [x for x in instructions if x is not None]


def remove_by_reversed_orders(instructions: List[ContentStreamInstruction], orders: Dict[str, List[int]]) -> \
        List[ContentStreamInstruction]:
    """Remove all instructions by reversed orders of operators from PDF."""
    indexes = {}
    for i in reversed(range(len(instructions))):
        instruction = instructions[i]
        op = instruction.operator.__str__()
        if indexes.get(op, 0) in orders.get(op, []):
            instructions[i] = None
        indexes[op] = indexes.get(op, 0) + 1
    return [x for x in instructions if x is not None]


def remove_watermark_from_geos_pdf(input_file: Path, output_file: Path) -> str:
    """
    Remove watermark from pdf (exported from any GEOS app) and save to output_file.
    :param input_file:
    :param output_file:
    :return:
    """
    pdf = Pdf.open(input_file)
    for page_number, page in enumerate(pdf.pages):
        page_instructions = parse_content_stream(page)
        previous_len = len(page_instructions)
        # VERSION EVALUATION
        page_instructions = remove_tjs_min(page_instructions, "VERSION EVALUATION")
        # alt: VERSION EVALUATION
        new_len = len(page_instructions)
        if new_len == previous_len:
            page_instructions = remove_by_reversed_orders(page_instructions, {
                'f': [0, ],
            })
            message = f"{input_file} at page {page_number + 1} => we used 'f' operator to remove watermark."
            logger.warning(message)
            w_sentry(capture_message, message)

        # Trial - XXX
        page_instructions = remove_tj_maj(page_instructions, "Trial - ")
        page_instructions = remove_tj_maj(page_instructions,
                                          [b'\x007', b'\x00U', b'\x00L', b'\x00D', b'\x00O', b'\x00\x03', b'\x00\x10',
                                           b'\x00\x03'])

        # UnRegistered
        page_instructions = remove_tj_maj(page_instructions, "UnRegistered")

        # save page
        new_content_stream = unparse_content_stream(page_instructions)
        page.Contents = pdf.make_stream(new_content_stream)  # override page contents
    pdf.save(output_file)
    return str(output_file)


def remove_watermark_from_pdf(input_file: Path, output_file: Path, method_choice: MethodChoice = None) -> str:
    """
    Remove watermark from pdf and save to output_file
    :param input_file:
    :param output_file:
    :param method_choice:
    :return:
    """
    if method_choice == MethodChoice.geos:
        return remove_watermark_from_geos_pdf(input_file, output_file)
    pdf = Pdf.open(input_file)
    for page in pdf.pages:
        for image_key in page.images.keys():
            raw_image = page.images[image_key]
            pdf_image = PdfImage(raw_image)
            pil_image = pdf_image.as_pil_image()
            pil_image = remove_watermark_from_pil_image(pil_image, method_choice)
            raw_image.write(zlib.compress(pil_image.tobytes()), filter=Name("/FlateDecode"))
    pdf.save(output_file)
    return str(output_file)


def remove_watermark_from_docx(input_file: Path, output_file: Path, method_choice: MethodChoice = None) -> str:
    """
    Remove watermark from docx and save to output_file
    :param input_file:
    :param output_file:
    :param method_choice:
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
            pil_image = remove_watermark_from_pil_image(pil_image, method_choice)
            image_file_tmp = io.BytesIO()
            pil_image.save(image_file_tmp, format="PNG")
            replacements[image] = image_file_tmp
    z.close()
    return str(replace_images_in_zip(input_file, output_file, replacements))


def remove_watermark_from_image(input_file: Path, output_file: Path, method_choice: MethodChoice) -> str:
    """
    Remove watermark from image
    :param input_file:
    :param output_file:
    :param method_choice:
    :return:
    """
    pil_image = Image.open(input_file)
    pil_image = remove_watermark_from_pil_image(pil_image, method_choice)
    pil_image.save(output_file)
    return str(output_file)


def main(input_file: Union[str, Path], output_file: Union[str, Path] = None, method_choice: MethodChoice = None) -> str:
    """
    Entry point
    :param input_file:
    :param output_file:
    :param method_choice:
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
        return remove_watermark_from_pdf(input_path, output_path, method_choice)
    elif str(input_path.suffix).lower() == ".docx":
        return remove_watermark_from_docx(input_path, output_path, method_choice)
    elif str(input_path.suffix).lower() in [".png", ".jpg", ".jpeg"]:
        return remove_watermark_from_image(input_path, output_path, method_choice)
    else:
        raise Exception(f"Unsupported file type: {input_path.suffix}")


def mmain(input_files: List[Union[str, Path]], output_dir: Union[str, Path] = None,
          method_choice: MethodChoice = None) -> List[str]:
    """
    Entry point
    :param input_files:
    :param output_dir:
    :param method_choice:
    :return:
    """
    output_files = []
    for input_file in input_files:
        input_path = Path(input_file)
        if not output_dir:
            output_dir = input_path.parent
        output_file = output_dir / (input_path.stem + f"_generated{input_path.suffix}")
        output_file = main(input_file, output_file, method_choice)
        output_files.append(output_file)
    return output_files


if __name__ == "__main__":
    fire.Fire(main)
