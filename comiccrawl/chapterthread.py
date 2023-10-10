import json
import os
import zipfile

import requests
from PIL import Image
from bs4 import BeautifulSoup
from requests import RequestException

from comiccrawl.compress import compress_folder
from comiccrawl.utils import make_new_folder, save_image_from_url, delete_folder


class ChapterIterator:
    """
        Iterates through the chapters
        We start in chapter one, until we arrive to the latest
    """

    def __init__(self, start_url):
        self.__start = start_url
        self.__current_url = ''

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__current_url:
            self.__current_url = self.__start
            return self.__current_url
        page = requests.get(self.__current_url)
        if page.status_code == requests.codes.ok:
            soup = BeautifulSoup(page.text, "html.parser")
            next_chapter = soup.select_one('.navi-next-chap')
            if next_chapter:
                print(f'Current chapter: {self.__current_url} - Next chapter: {next_chapter["href"]}')
                self.__current_url = next_chapter['href']
                return self.__current_url
        print('No more chapters')
        raise StopIteration


class PagesIterator:
    """
        Iterates through the pages of a chapter
        We start in chapter one, until we arrive to the latest

        This iterator returns the soup
    """

    def __init__(self, start_url):
        self.__start = start_url
        self.__current_url = start_url
        self.__end_url = ''

    def __iter__(self):
        return self

    def __next__(self):
        if self.__current_url != self.__end_url:
            page = requests.get(self.__current_url)
            if page.status_code == requests.codes.ok:
                soup = BeautifulSoup(page.text, "html.parser")
                if not self.__end_url:
                    next_chapter = soup.select_one('.navi-next-chap')
                    self.__end_url = next_chapter.get('href', None) if next_chapter else None
                next_page = soup.select_one('.navi-next')
                if next_page and next_page.get('href', None):
                    print(f'\tCurrent page: {self.__current_url} - Next page: {next_page["href"]}')
                    self.__current_url = next_page['href']
                    return soup
        print('\tNo more pages')
        raise StopIteration


def iterate_webcomic(start_url, destination_folder):
    for chapter_num, chapter in enumerate(ChapterIterator(start_url)):
        new_folder = make_new_folder(destination_folder, chapter_num)
        for idx, page in enumerate(PagesIterator(chapter)):
            save_image(page, idx, new_folder)
            save_text_as_images(page, idx, new_folder)
        compress_folder(new_folder)
        delete_folder(new_folder)


def save_image(soup, image_index, new_folder):
    img_link = soup.find('div', {'class': 'comic-table'}).findNext('div', {'id': 'comic'}).find('img')['src']
    save_image_from_url(img_link, image_index, new_folder)


def save_text_as_images(soup, image_index, new_folder):
    image_text = soup.find('div', {'class': 'entry'}).get_text()

    image_text = image_text.strip()
    if image_text != '':
        #   I want the text printed in the same image size as the last downloaded image
        #   so I extract the size from it.
        image_with_index = ''
        for image_name in sorted(os.listdir(new_folder), reverse=True):
            if image_name.startswith(f'{image_index:03d}_'):
                image_with_index = image_name

        img_path = os.path.join(new_folder, image_with_index)
        im = Image.open(img_path)
        image_size = im.size  # (width,height) tuple
        # get the image from the flask utility
        try:
            get_image_from_text2pic(image_text, image_size, image_index, new_folder)
        except RequestException as ex:
            print(f"Exception connecting to text2pic - {ex}")


def get_image_from_text2pic(text, size, image_index, new_folder):
    """

    Sends some text to the text2pic service that embeds the text in a series
    of images of the given size

    The images are named using the image_index so they will appear after
    the original image

    :param text:    the text to put into images
    :param size:    the image size
    :param image_index: current image index
    :param new_folder:  destination folder to store images
    :return:
    """
    # text2pic_host = 'http://172.17.0.2:5000/'
    text2pic_host = 'http://127.0.0.1:5000/'
    margin_ratio = 0.15
    json_data = json.dumps({'text': text, 'width': size[0], 'height': size[1],
                            'margin-width': size[0] * margin_ratio, 'margin-height': size[1] * margin_ratio,
                            'font': 'NotoMono-Regular.ttf', 'font-size': 32})
    headers = {'Content-type': 'application/json'}
    img_request = requests.post(text2pic_host + 'text2piczip', headers=headers, data=json_data, stream=True)
    if img_request.status_code == 200:
        zip_folder = os.path.join(new_folder, 'temp-zip')
        zip_file = os.path.join(new_folder, 'temp.zip')
        os.makedirs(zip_folder, exist_ok=True)
        with open(zip_file, 'wb') as f:
            f.write(img_request.content)
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(zip_folder)
        os.remove(zip_file)
        all_images = os.listdir(zip_folder)
        for image in all_images:
            os.rename(os.path.join(zip_folder, image), os.path.join(new_folder, f'{image_index:03d}Z{image}'))
        os.rmdir(zip_folder)
    else:
        print(f'Error in text from {image_index} image in chapter {new_folder}')
        print(img_request.text)


def get_end_of_chapter(start_url, next_chapter):
    page = requests.get(start_url)
    if page.status_code != requests.codes.ok:
        return ''

    soup = BeautifulSoup(page.text, "html.parser")
    # get the url for the "Next page" link
    next_link = soup.find('a', href=True, string=next_chapter)
    if next_link:
        next_link = next_link['href']
    else:
        next_link = ''
    return next_link
