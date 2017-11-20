#   Downloads a whole chapter from the webcomic
#   Parameters
#       Starting point
#       End url
#       Text to search "next page" link

# requests to make HTTP requests
import json

import requests
from PIL import Image
from requests import RequestException
# beautiful soup for HTML parsing
from bs4 import BeautifulSoup

import os

# page.findNext('div',{'class':'class_value'}).findNext('div',{'id':'id_value'}).findAll('a')
#   div[class=class_value]/div[id=id_value]/a


def save_image_from_url(img_link, image_index, new_folder):
    print("\nImagen: " + img_link)
    # get filename from url
    url_filename = img_link.rsplit('/', 1)[1]
    img_path = str(image_index).zfill(3) + '_' + url_filename
    img_path = os.path.join(new_folder, img_path)
    print("\nImagen (path): " + img_path)

    # download the image
    r = requests.get(img_link, stream=True)
    if r.status_code == 200:
        with open(img_path, 'wb') as img_file:
            for chunk in r.iter_content(1024):
                img_file.write(chunk)
                #                    for chunk in r:
                #                        img_file.write(chunk)
    return img_path


def make_new_folder(base_folder, chapter_num):
    # make a new folder for this chapter in the base folder
    chapter_title = 'chapter_' + str(chapter_num).zfill(3)
    # zfill to pad chapter number with zeroes
    new_folder = os.path.join(base_folder, chapter_title)
    print("Making folder: " + new_folder)
    try:
        os.mkdir(new_folder)
    except FileExistsError:
        # do nothing
        pass
    return new_folder


def crawl_chapter(start_url, end_url, next_text, base_folder, chapter_num):
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
                print("\nTexto: " + image_text)
                im = Image.open(img_path)
                image_size = im.size  # (width,height) tuple
                # get the image from the flask utility
                get_image_from_text2pic(image_text, image_size, image_index, new_folder, img_link)

            current_page = next_link
            page_index += 1
            image_index += 1
        except RequestException as ex:  # this covers everything
            print("Couldn´t get page" + current_page)
            print(ex)
            break
        except Exception as inst:
            print(type(inst))   # the exception instance
            print(inst.args)    # arguments stored in .args
            print(inst)         # __str__ allows args to be printed directly,
                                # but may be overridden in exception subclasses#

def get_image_from_text2pic(text, size, image_index, new_folder, img_link):
    # compose json
    w_margin = size[0]*0.15
    h_margin = size[1]*0.15
    data = {'text': text, 'width': size[0], 'height': size[1],
            'margin-width':w_margin, 'margin-height': h_margin,
            'font': 'arial.ttf', 'font-size': 32 }
    json_data = json.dumps(data)
    headers = {'Content-type': 'application/json'}
    img_request = requests.post( 'http://localhost:5000/text2pic', headers=headers, data=json_data, stream = True)
    if img_request.status_code == 200:
        url_filename = img_link.rsplit('/', 1)[1]
        img_path = str(image_index).zfill(3) + 'Z' + url_filename
        img_path = os.path.join(new_folder, img_path)
        with open(img_path, 'wb') as img_file:
            for chunk in img_request.iter_content(1024):
                img_file.write(chunk)
    elif img_request.status_code == 400:
        # bad request
        print('Error in text from ' + img_link + ' (image ' + image_index + ' in chapter ' + new_folder +')')
        print( img_request.text)



def get_end_of_chapter(start_url, next_chapter):
    page = requests.get(start_url)
    if page.status_code != requests.codes.ok:
        return ''

    soup = BeautifulSoup(page.text, "html.parser")
    # get the url for the "Next page" link
    next_link = soup.find('a', href=True, string=next_chapter)['href']
    return next_link
