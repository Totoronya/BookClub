import os

import pandas as pd

from crawler.bookclub_crawler import Website, Crawler

if __name__ == "__main__":
    file_path = os.path.abspath("data/book_data.csv")

    book_club = Website('BookClub', 'https://bookclub.ua', '^(/catalog/books/)', False,
                        tag_class="navbutt pagenav2_bl_next_act next-active")

    crawler = Crawler(book_club)
    crawler.crawl()

    header = ['Name', 'Author', 'Price', 'Link']

    unsorted_df = pd.DataFrame(crawler.data, columns=header)
    unsorted_df.to_csv(path_or_buf=file_path, sep=':', encoding='utf-8')
    sorted_df = pd.read_csv(file_path, sep=':')
    new_df = sorted_df.drop_duplicates(subset=['Name', 'Link'], keep='last').reset_index(drop=True)
    save_df = new_df.to_csv(path_or_buf=file_path, sep=':', encoding='utf-8')
