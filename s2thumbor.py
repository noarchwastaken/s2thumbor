#!/usr/bin/python3

"""
Site-to-Thumbor - Convert all images into Thumbor CDN Links,
    in a static, HTML-based website.

This Code is released under the public domain with WTFPL.
You just DO WHAT THE FUCK YOU WANT TO.
http://www.wtfpl.net/about/
"""

# Built-in imports
import argparse
import urllib
from pathlib import Path

# External imports
import cv2
from bs4 import BeautifulSoup
from libthumbor import CryptoURL


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Site-to-Thumbor - \
            Convert all images into Thumbor CDN Links,\
            in a static, HTML-based website.')

    parser.add_argument('key', type=str,
                        help='Your Thumbor Secure key')
    parser.add_argument('thumbor_site', type=str,
                        help='Thumbor CDN URL without trailing slash')
    parser.add_argument('root', type=Path,
                        help='Website root')
    parser.add_argument('--width', type=int, default=0,
                        help='Width of Thumbor-processed images')
    parser.add_argument('--height', type=int, default=0,
                        help='Height of Thumbor-processed images')
    parser.add_argument('--smart', type=float, default=None,
                        help='Instead of using a fixed size, \
                            divide target images by it')

    return parser.parse_args()


def process_url(crypto, thumbor_site, root, url, width, height, smart):
    """
    Convert url into full, secure Thumbor URL

    crypto: CryptoURL, libthumbor object for generating encrypted URL
    thumbor_site: str, Thumbor CDN URL without trailing slash
    root: Path, Website root
    url: str, Absolute (relative to website root) path of target image
    width: int, Width of target image
    height: int, Height of target image
    smart: float, Instead of using a fixed size, divide target images by it
    """

    if smart:
        # Unquote encoded URLs before passing to pathlib
        unquoted_url = urllib.parse.unquote(url)
        absolute_path = Path(root, unquoted_url)
        actual_image = cv2.imread(str(absolute_path))

        h, w, _ = actual_image.shape
        width = int(w / smart)
        height = int(h / smart)

    encrypted_url = crypto.generate(
        width=width,
        height=height,
        image_url=url
    )
    return (thumbor_site + encrypted_url)


def main(key, root):
    """
    Execution

    key: str, Secret to encrypt the Thumbor URL
    root: Path, Website root
    """
    crypto = CryptoURL(key)
    for i in root.glob('**/*.html'):
        file = Path(i)
        html = BeautifulSoup(file.read_text(), 'html.parser')
        imgs = html.find_all('img')

        for img in imgs:
            src = img['src']
            # Do not process SVGs because doing it is useless
            if not src.endswith('.svg'):
                if src.startswith('/'):
                    # Some links are already absolute paths,
                    # so do not make them absolute again
                    src = src[1:]
                else:
                    # Get the path of the image relative to the website root
                    src = (str(file.parent.relative_to(root))
                           + '/'
                           + src)

                img['src'] = process_url(
                        crypto, args.thumbor_site, root, src,
                        args.width, args.height, args.smart)
                print(img['src'])

        i.write_text(str(html))


if __name__ == '__main__':
    args = parse_arguments()
    main(args.key,
         args.root)
