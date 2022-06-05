import os

import pandas as pd

from crawler.bookclub_crawler import Website, Crawler

dir_path = os.path.abspath("data/book_data.csv")

book_club = Website('BookClub', 'https://bookclub.ua', '^(/catalog/books/)', False,
                    tag_class="navbutt pagenav2_bl_next_act next-active")

crawler = Crawler(book_club)
header = ['Name', 'Author', 'Price', 'Link']

if __name__ == "__main__":
    crawler.crawl()

    unsorted_df = pd.DataFrame(crawler.data, columns=header)
    unsorted_df.to_csv(path_or_buf=dir_path, sep=':', encoding='utf-8')
