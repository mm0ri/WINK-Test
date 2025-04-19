""" TODO
Необходимо взять карту любого сайта, проверить на ней доступность каждой ссылки,
выведя в файл все ссылки чьи коды не 200 формата: ссылка - статус код.

Также найти на каждой странице rel=«canonical» и проверить его на соответствие запрошенному урлу:
выведя в отдельный файл все несовпадения формата: запрошенный url - canonical.

При наличии хотя бы одного несовпадения валить тест.

Получается, валить тест если ссылка недоступна? Или как, но если ссылка недоступна, то она будет не 200?
Получается, валить тест если рел соответствует? Короче как-то поставлена задача странно.
"""

import requests
import pytest
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

class TestRelCheckerSuite:
    site_url = 'https://github.com/'

    @pytest.fixture(scope='function')
    def links_getter(self) -> list:
        res_list = []

        for link in BeautifulSoup(requests.get(self.site_url, timeout=5).text, 'html.parser').find_all('link'):
            try:
                if link.get('href') is not None and ('https:' in link.get('href') or 'http' in link.get('href')):
                    res_list.append({'url': link.get('href'), 'rel': link.get('rel')})
            except requests.exceptions.ReadTimeout:
                pytest.fail('ReadTimeout Exception. Connection problems?')

        return res_list

    @pytest.fixture(scope='function')
    def get_canonical(self) -> str:
        return BeautifulSoup(requests.get(self.site_url).text, 'html.parser').find('link', {'rel': 'canonical'}).get('href')

    def test_check_correct_status_codes(self, links_getter, get_canonical):
        url_list = links_getter
        main_canon_url = get_canonical

        with open('codes_result_file.txt', 'w+') as res_file:
            for url_elem in url_list:
                try:
                    res = requests.get(url_elem['url'], timeout=5)
                    if res.status_code != 200:
                        res_file.write(f'{url_elem["url"]} - {str(res.status_code)}\n')
                except requests.exceptions.ReadTimeout:
                    print('ReadTimeout Exception. Connection problems? But here is not a problem for us.')

        with open('canonical_result_file.txt', 'w+') as cn_res_file:
            for url in url_list:
                try:
                    canonical = BeautifulSoup(requests.get(url['url'], timeout=5).text, 'html.parser').find('link', {'rel': 'canonical'})
                except requests.exceptions.ReadTimeout:
                    pytest.fail('ReadTimeout Exception. Connection problems?')

                if canonical is not None:
                    if canonical.get('href') != main_canon_url:
                        cn_res_file.write(f'{url["url"]} - {canonical.get('href')}\n')
                        pytest.fail(f'Main canonical URL and current canonical URL is not similar. Main URL: {main_canon_url}, Current URL: {canonical.get('href')}')
