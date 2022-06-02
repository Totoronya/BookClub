import os
import pandas as pd

from crawler.bookclub_crawler import Website, Crawler

dir_path = os.path.abspath("bookdata")

bookclub = Website('BookClub', 'https://bookclub.ua', '^(/catalog/books/)', False,
                   tag_class="navbutt pagenav2_bl_next_act next-active")

crawler = Crawler(bookclub, dir_path)
header = ['Name', 'Author', 'Price', 'Link']

if __name__ == "__main__":
    crawler.crawl()

    df = pd.DataFrame(crawler.data, columns=header)
    df.to_csv(path_or_buf=dir_path + '/book_data.csv', sep=':', encoding='utf-8')
    df.drop_duplicates()
