from BasePage import BasePage


class PokemonsPage(BasePage):
    TRAINER_BUTTON_SELECTOR = "div.header__container > .header__id"

    def __init__(self, page):
        super().__init__(page)
        self._endpoint = ''

    def check_created_pokemon(self, text):
        self.go_to_url()
        self.find_object_by_text(text)
        self.click_selector(self.TRAINER_BUTTON_SELECTOR)
