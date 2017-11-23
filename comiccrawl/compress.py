"""

    I´ll put the compressing utils in this file

    A CBZ is just a Zip file with another extension

    The crawler stores each chapter in a folder so
    I can take that folder, zip it and create the
    output CBZ file

"""
import os
from zipfile import ZipFile


def compress_folder(folder_path):
    # I´ll take the last item in the path
    cbz_file = folder_path + '.cbz'
    # add all the images in the folder to the zip file
    with ZipFile(cbz_file, 'w') as output_cbz:
        for file in sorted(os.listdir(folder_path)):
            file_to_add = os.path.join(folder_path, file)
            output_cbz.write(file_to_add)
