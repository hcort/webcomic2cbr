from comiccrawl.chapterthread import iterate_webcomic


def main():
    start_url = "https://killsixbilliondemons.com/comic/kill-six-billion-demons-chapter-1/"
    base_folder = '/home/hector/killsixbilliondemons/'
    iterate_webcomic(start_url, base_folder)


if "__main__" == __name__:
    main()

