import json
import requests
from PIL import Image
from bs4 import BeautifulSoup
from requests import RequestException

from comiccrawl.compress import compress_folder
from comiccrawl.utils import make_new_folder, save_image_from_url, delete_folder


def crawl_chapter(start_url, end_url, next_text, base_folder, chapter_num):
    """
    Iterates over all the images of a chapter in the webcomic and download
    each of it pages.

    This function will create a new folder using the chapter_num parameter and
    all the images will be downloaded there.

    If there is some text in a page it will call the text2pic service
    TODO: take the text2pic host from config file. now is on localhost:5000

    After downloading the whole chapter into a folder it will make a CBZ
    file from it,

    :param start_url:   first page of this chapter
    :param end_url:     last page
    :param next_text:   the text of the "next page" link to iterate the chapter
    :param base_folder: the folder where the webcomic is being downloaded
    :param chapter_num: the number of this chapter
    :return:

    """
    current_page = start_url
    page_index = 1
    new_folder = make_new_folder(base_folder, chapter_num)

    image_index = 0
    while current_page != end_url:
        # get current page
        try:
            page = requests.get(current_page)
            if page.status_code != requests.codes.ok:
                break

            soup = BeautifulSoup(page.text, "html.parser")
            # get the url for the "Next page" link
            next_link = soup.find('a', href=True, text=next_text)['href']
            # get the current image
            img_link = soup.find('div', {'class': 'comic-table'}).findNext('div', {'id': 'comic'}).find('img')['src']

            # some pages have text
            # <div class="entry">
            image_text = soup.find('div', {'class': 'entry'}).get_text()

            img_path = save_image_from_url(img_link, image_index, new_folder)

            image_text = image_text.strip()
            if image_text != '':
                #   I want the text printed in the same image size as the last downloaded image
                #   so I extract the size from it.
                im = Image.open(img_path)
                image_size = im.size  # (width,height) tuple
                # get the image from the flask utility
                try:
                    get_image_from_text2pic(image_text, image_size, image_index, new_folder)
                except RequestException as ex:
                    print("Exception connecting to text2pic")
                    print(ex)
            # next loop step
            current_page = next_link
            page_index += 1
            image_index += 1
        except RequestException as ex:  # this covers everything
            print("Couldn´t get page" + current_page)
            print(ex)
            break
        except Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)  # __str__ allows args to be printed directly,
            # but may be overridden in exception subclasses#
    # end of chapter loop
    # create zip
    compress_folder(new_folder)
    delete_folder(new_folder)


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
    text2pic_host = 'http://localhost:5000'
    # compose input json for text2pic
    w_margin = size[0] * 0.15
    h_margin = size[1] * 0.15
    data = {'text': text, 'width': size[0], 'height': size[1],
            'margin-width': w_margin, 'margin-height': h_margin,
            'font': 'arial.ttf', 'font-size': 32}
    json_data = json.dumps(data)
    headers = {'Content-type': 'application/json'}
    img_request = requests.post(text2pic_host + '/text2pic', headers=headers, data=json_data, stream=True)
    if img_request.status_code == 200:
        # get json body and iterate
        # the json response is an array of image relative urls
        json_resp = img_request.json()
        for item in json_resp['images']:
            current_img_url = text2pic_host + item['filename']
            save_image_from_url(current_img_url, image_index, new_folder, True)
    else:
        # bad request
        print('Error in text from ' + image_index + ' image in chapter ' + new_folder + ')')
        print(img_request.text)


def get_end_of_chapter(start_url, next_chapter):
    page = requests.get(start_url)
    if page.status_code != requests.codes.ok:
        return ''

    soup = BeautifulSoup(page.text, "html.parser")
    # get the url for the "Next page" link
    next_link = soup.find('a', href=True, string=next_chapter)['href']
    return next_link
