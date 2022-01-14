from typing import Dict
from PIL import Image
from pathlib import Path
import zlib
import numpy
from pikepdf import Pdf, PdfImage, Name
import cv2
import zipfile
import io
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


def remove_watermark_from_image(img: numpy.ndarray) -> numpy.ndarray:
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


def generate_output_path(input_path: Path) -> Path:
    """
    Generate output_path from input_path
    :param input_path:
    :return:
    """
    return input_path.parent / (input_path.stem + f"_generated{input_path.suffix}")


def remove_watermark_from_pdf(input_file: Path, output_file: Path) -> str:
    """
    Remove watermark from pdf and save to output_file
    :param input_file:
    :param output_file:
    :return:
    """
    pdf = Pdf.open(input_file)
    for page in pdf.pages:
        for image_key in page.images.keys():
            raw_image = page.images[image_key]
            pdf_image = PdfImage(raw_image)
            pil_image = pdf_image.as_pil_image()
            # noinspection PyTypeChecker
            opencv_image = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
            opencv_image = remove_watermark_from_image(opencv_image)
            pil_image = Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
            raw_image.write(zlib.compress(pil_image.tobytes()), filter=Name("/FlateDecode"))
    pdf.save(output_file)
    return str(output_file)


def remove_watermark_from_docx(input_file: Path, output_file: Path) -> str:
    """
    Remove watermark from docx and save to output_file
    :param input_file:
    :param output_file:
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
            # noinspection PyTypeChecker
            opencv_image = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
            opencv_image = remove_watermark_from_image(opencv_image)
            pil_image = Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
            image_file_tmp = io.BytesIO()
            pil_image.save(image_file_tmp, format="PNG")
            replacements[image] = image_file_tmp
    z.close()
    return str(replace_images_in_zip(input_file, output_file, replacements))


def main(input_file: str, output_file: str = None) -> str:
    """
    Entry point
    :param input_file:
    :param output_file:
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
        return remove_watermark_from_pdf(input_path, output_path)
    elif str(input_path.suffix).lower() == ".docx":
        return remove_watermark_from_docx(input_path, output_path)
    else:
        raise Exception(f"Unsupported file type: {input_path.suffix}")


if __name__ == "__main__":
    fire.Fire(main)
