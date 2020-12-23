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
from pathlib import Path

# Bxternal imports
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

    return parser.parse_args()


def process_url(crypto, thumbor_site, url, width, height):
    """
    Convert url into full, secure Thumbor URL

    crypto: CryptoURL, libthumbor object for generating encrypted URL
    thumbor_site: str, Thumbor CDN URL without trailing slash
    url: str, Absolute (relative to website root) path of target image
    width: int, Width of target image
    height: int, Height of target image
    """

    encrypted_url = crypto.generate(
        width=width,
        height=height,
        image_url=url
    )
    return (thumbor_site + encrypted_url)


def main(key, thumbor_site, root, width, height):
    """
    Execution

    key: str, Secret to encrypt the Thumbor URL
    thumbor_site: str, Thumbor CDN URL without trailing slash
    root: Path, Website root
    width: int, Width of target image
    height: int, Height of target image
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
                # Some links are already absolute paths,
                # so do not make them absolute again
                if src.startswith('/'):
                    # Omit the heading slash
                    img['src'] = process_url(
                        crypto, thumbor_site, src[1:], width, height)
                    print(img['src'])
                else:
                    # Get the absolute path of the image
                    abs_src = (str(file.parent.relative_to(root))
                               + '/'
                               + src)
                    img['src'] = process_url(
                        crypto, thumbor_site, abs_src, width, height)
                    print(img['src'])

        i.write_text(html.prettify())


if __name__ == '__main__':
    args = parse_arguments()
    main(args.key, args.thumbor_site,
         args.root, args.width, args.height)
