import re

import bs4.element
import requests
from bs4 import BeautifulSoup


class Website:
    """Contains information about website structure"""

    def __init__(self, name: str, url: str, target_pattern: str, absolute_url: bool, tag_class: str):
        self.name = name
        self.url = url
        self.target_pattern = target_pattern
        self.absolute_url = absolute_url
        self.tag_class = tag_class


class SectionContent:
    """
    Common base class for all content in sections
    """

    def __init__(self, url: str, book_name: str, book_author: str, book_descr: str, book_price, book_link: str):
        self.url = url
        self.book_name = book_name
        self.book_author = book_author
        self.book_descr = book_descr
        self.book_price = book_price
        self.book_link = book_link

    def print(self):
        """
        Flexible printing function controls output
        """
        print("++++++++++++++++++++++++++")
        print('URL: {}'.format(self.url))
        print('NAME: {}'.format(self.book_name))
        print('AUTHOR: {}'.format(self.book_author))
        print('PRICE: {}'.format(self.book_price))
        print("+++++++++++++++++++++++++++++\n")


class Crawler:

    def __init__(self, site: str, path_to_save: str):
        self.site = site
        self.visited = []
        self.path_to_save = path_to_save
        self.data = []

    def get_page(self, url) -> BeautifulSoup | None:
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, 'lxml')

    def safe_get(self, page_obj: bs4.BeautifulSoup, selector: str):
        """
        Utility function used to get a content string from a Beautiful Soup
        object and a selector. Returns an empty string if no object
        is found for the given selector
        """
        selected_elms = page_obj.select(selector)
        if selected_elms is not None and len(selected_elms) > 0:
            return '\n'.join([elem.get_text() for elem in selected_elms])
        return ''

    def parse(self, url):
        """
        Extract content from a given page URL
        """
        bs = self.get_page(url)
        if bs is not None:

            for book in bs.select('section.book-inlist'):
                try:
                    book_author = book.select_one('div.authorName').text

                    book_name = book.select_one('div.book-inlist-name').find('a').get('title')
                    book_link = ''.join([self.site.url, book.select_one('div.book-inlist-name').find('a').get('href')])

                    book_price = book.select_one('div.book-inlist-price').text[1:-5]
                    if len(book_price) == 6:
                        book_price = book_price[0: -3]

                    book_descr = book.select_one('div.mainGoodContent').text[:-22]

                    # book_content = SectionContent(url=url, book_name=book_name, book_author=book_author,
                    #                               book_descr=book_descr,
                    #                               book_price=book_price, book_link=book_link)

                    self.data.append([book_name, book_author, book_price,
                                      book_link])
                except AttributeError:
                    print('Missing some attributes. Can not save data')

    def crawl(self):
        """
        Get pages from website home page
        """
        bs = self.get_page(self.site.url)
        section_pages = bs.findAll('a', class_='sec-menu-link', href=re.compile(self.site.target_pattern))
        for section_page in section_pages:
            print('[+]Collecting data about books in section:', section_page.text, '[+]')
            section_page = section_page.attrs['href']
            if section_page not in self.visited:
                self.visited.append(section_page)
                if not self.site.absolute_url:
                    section_page = '{site_url}{section_href}'.format(site_url=self.site.url, section_href=section_page)
                    cur_page = self.get_page(section_page)
                    tag_parent = cur_page.find('div', class_=self.site.tag_class)
                    self.parse(section_page)
                    while tag_parent is not None:
                        next_page_href = tag_parent.find_parent('a').get('href')
                        next_section_page = ''.join([section_page, next_page_href])
                        self.parse(next_section_page)
                        cur_page = self.get_page(next_section_page)
                        tag_parent = cur_page.find('div', class_=self.site.tag_class)

        print('[+]Data collected[+]')
