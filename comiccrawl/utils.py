import os
import requests
import shutil
import unicodedata


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    import re
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    # return mark_safe(re.sub(r'[-\s]+', '-', value))
    return value

def save_image_from_url(img_link, image_index, new_folder, text2pic=False):
    """
    Makes a request to the given image URL and saves the image
    in the given folder.

    The filename is composed of the index of the image in the
    chapter and its name in the URL

    The flag text2pic is used to append a Z character after the
    image index to make sure the text images are stored after
    the proper image
    """
    # get filename from url
    url_filename = img_link.rsplit('/', 1)[1]
    url_filename = slugify(url_filename)
    if text2pic:
        img_path = str(image_index).zfill(3) + 'Z' + url_filename
    else:
        img_path = str(image_index).zfill(3) + '_' + url_filename
    img_path = os.path.join(new_folder, img_path)
    # download the image
    r = requests.get(img_link, stream=True)
    if r.status_code == 200:
        with open(img_path, 'wb') as img_file:
            # download the file in 1024 bytes chunks
            for chunk in r.iter_content(1024):
                img_file.write(chunk)
    else:
        print( 'Error downloading file: ' + str(image_index) + ' from ' + img_link )
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


def delete_folder(folder_path):
    print('Deleting folder: ' + folder_path)
    # delete contents and then delete folder
    shutil.rmtree(folder_path, ignore_errors=True)
    # for file in sorted(os.listdir(folder_path)):
    #     if file.closed:
    #         os.remove(os.path.join(folder_path, file))
    #     else:
    #         print('File is not closed: ' + folder_path + '/' + file)
    # os.rmdir(folder_path)