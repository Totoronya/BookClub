import re

import requests
from bs4 import BeautifulSoup


class Website:
    """
    Basic class. Contains information about website structure

    """

    def __init__(self, name: str, url: str, target_pattern: str, absolute_url: bool, tag_class: str) -> None:
        """
        Parameters
        __________

        name : str
            The name of a website
        url : str
            The link of the website
        target_pattern : str
            A pattern which is used for navigation between the website sections
        absolute_url : bool
            Contains information whether it is absolute url or not
        tag_class:
            An information about next page button
        """
        self.name = name
        self.url = url
        self.target_pattern = target_pattern
        self.absolute_url = absolute_url
        self.tag_class = tag_class


class Crawler:
    """
    Basic class. Gets data from a website
    ...

    Attributes:
        visited : list
            contains visited links
        data : list
            contains collected data

    """

    def __init__(self, site: Website) -> None:
        """
        Parameters
        __________

        site : Website
            the website with data
        """
        self.site = site
        self.visited = []
        self.data = []

    @classmethod
    def get_page(cls, url: str) -> BeautifulSoup | None:
        """
        Returns a webpage or None

        Parameters
        ----------

        url : str
            The link you want to get

        Raises
        ------
            RequestException
            If the page is inaccessible
        """
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, 'lxml')

    def parse(self, url: str) -> None:
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

                    # book_descr = book.select_one('div.mainGoodContent').text[:-22]

                    if len(self.data) == 0:
                        self.data.append([book_name, book_author, book_price,
                                          book_link])
                    elif len(self.data) > 0:
                        for obj in self.data:
                            if obj[3] != book_link:
                                self.data.append([book_name, book_author, book_price,
                                                  book_link])
                                return

                except AttributeError:
                    print('Missing some attributes. Can not save data')

    def crawl(self) -> None:
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
