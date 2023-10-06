import threading
from html import unescape

from comiccrawl.chapterthread import get_end_of_chapter, crawl_chapter


def main():

    # starting point
    start_url = "https://killsixbilliondemons.com/comic/kill-six-billion-demons-chapter-1/"
    next_page = "Next Page &gt;"
    next_chapter = "Next Chapter ]&gt;"
    count = 1

    """
    Problem with HTML entities
        >>> from BeautifulSoup import BeautifulSoup
        >>> BeautifulSoup("<p>&pound;682m</p>", convertEntities=BeautifulSoup.HTML_ENTITIES)
    https://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string/2087433#2087433
    """

    next_page = unescape(next_page)
    next_chapter = unescape(next_chapter)

    # base folder
    # base_folder = 'C:\\Users\\Héctor\\Documents\\Kill_Six_Billion_Demons\\'
    base_folder = '/home/hector/killsixbilliondemons/'
    # get end url for chapter
    current_url = start_url
    next_url = current_url
    while '' != next_url:
        next_url = get_end_of_chapter(current_url, next_chapter)
        # iterate all the chapters
        print("Parsing url: " + current_url)
        # crawl_chapter( start_url, end_url, next_text, base_folder, chapter_num ):
        crawl_chapter(current_url, next_url, next_page, base_folder, count)
#        t = threading.Thread(target=crawl_chapter, args=(current_url, next_url, next_page, base_folder, count))
#        t.start()
        count += 1
        current_url = next_url

    # won´t use threads, delete this
    # # get main thread
    # mt = threading.currentThread()
    # # join all threads save main
    # for th in threading.enumerate():
    #     # si es el hilo principal saltar o entraremos en deadlock
    #     if th is mt:
    #         continue
    #     th.join()


if "__main__" == __name__: main()
