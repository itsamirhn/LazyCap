import pathlib
from time import sleep

import click
import mss
from PIL import Image, ImageChops, ImageGrab


def difference_percentage(img1, img2):
    diff = ImageChops.difference(img1, img2)
    bbox = diff.getbbox()
    if not bbox:
        return 0
    pixels = diff.height * diff.width
    return sum(diff.crop(bbox).point(lambda x: 255 if x else 0).convert("L").point(bool).getdata()) * 100 / pixels


def take_screenshot():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img


@click.command('LazyCap')
@click.argument('output_folder', type=click.Path(file_okay=False))
@click.option('-s', '--similarity', 'similarity_percentage', default=90, show_default=True,
              help='Minimum Similarity percentage of the consecutive Screenshots to skip the Screenshot')
@click.option('-d', '--delay', 'delay', default=1, show_default=True, help='Delay seconds between each Screenshot')
def main(similarity_percentage, delay, output_folder):
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    last_saved_img = None
    index = 1
    while True:
        sleep(delay)
        img = take_screenshot()
        diff = difference_percentage(last_saved_img, img) if last_saved_img else 100.0
        if diff + similarity_percentage > 100:
            click.echo("Saving Screenshot {} with difference: {}".format(index, diff))
            img.save(f'{output_folder}/{index}.png')
            index += 1
        last_saved_img = img


if __name__ == '__main__':
    main()
