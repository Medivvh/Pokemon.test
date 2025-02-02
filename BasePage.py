from playwright.sync_api import expect, Locator

class BasePage:
    __Base_Url = 'https://pokemonbattle.ru'

    def __init__(self, page):
        self.page = page
        self._endpoint = ''

    def go_to_url(self):
        url_with_path = f'{self.__Base_Url}/{self._endpoint}'
        self.page.goto(url_with_path)
        self.page.wait_for_load_state('load')
        expect(self.page).to_have_url(url_with_path)

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