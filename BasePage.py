from playwright.sync_api import expect, Locator


class BasePage:
    __Base_Url = 'https://pokemonbattle.ru'

    def __init__(self, page):
        self.page = page
        self._endpoint = ''

    def _full_url(self):
        return f'{self.__Base_Url}/{self._endpoint}'

    def go_to_url(self):
        full_url = self._full_url()
        self.page.goto(full_url)
        self.page.wait_for_load_state('load')
        expect(self.page).to_have_url(full_url)

    def type_text_to_selector(self, selector, value):
        self.page.wait_for_selector(selector)
        self.page.is_visible(selector)
        self.page.type(selector, value)

    def click_selector(self, selector):
        self.page.wait_for_selector(selector)
        expect(self.page.locator(selector)).to_be_visible()
        expect(self.page.locator(selector)).to_be_enabled()
        self.page.click(selector)

    def assert_next_page_have_text(self, text):
        expect(self.page.locator('body')).to_contain_text(text)

    def find_object_by_text(self, text):
        self.page.get_by_text(text)
        expect(self.page.get_by_text(text)).to_be_visible()

    def valid_url_on_page(self):
        expect(self.page).to_have_url(self._full_url())

    def object_is_visible(self, selector):
        expect(self.page.locator(selector)).to_be_visible()

    def selector_have_text(self, selector, text):
        expect(self.page.locator(selector)).to_have_text(text)
