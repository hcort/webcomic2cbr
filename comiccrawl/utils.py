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


def save_image_from_url(img_link, image_index, new_folder):
    """
    Makes a request to the given image URL and saves the image
    in the given folder.

    The filename is composed of the index of the image in the
    chapter and its name in the URL
    """
    # get filename from url
    url_filename = img_link.rsplit('/', 1)[1]
    filename, extension = os.path.splitext(url_filename)
    filename = slugify(filename)
    img_path = f'{image_index:03d}_{filename}{extension}'
    img_path = os.path.join(new_folder, img_path)
    # download the image
    r = requests.get(img_link, stream=True)
    if r.status_code == 200:
        with open(img_path, 'wb') as img_file:
            for chunk in r.iter_content(1024):
                img_file.write(chunk)
    else:
        print(f'Error downloading file: {image_index} from {img_link}')
    return img_path


def make_new_folder(base_folder, chapter_num):
    chapter_title = 'chapter_' + str(chapter_num).zfill(3)
    new_folder = os.path.join(base_folder, chapter_title)
    os.mkdir(new_folder)
    return new_folder


def delete_folder(folder_path):
    shutil.rmtree(folder_path, ignore_errors=True)
