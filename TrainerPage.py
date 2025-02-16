from BasePage import BasePage
from constant import TRAINER_ID


class TrainerPage(BasePage):
    Pokemon_Selector = '.pokemons-top > #dropdown'
    Pokeball_selector = 'div.trainer-item__content >> div.title-single__icon.k_title_icon_status_pok > img'
    History_selector = '(//a[1]/button)[2]'
    Battle_selector = '//div[contains(@class,"k_battle_0")]'
    Attacking_pokemons_id_selector = '(//div[contains(@class, "history-card__id pok_id")])[3]'
    Defending_pokemons_selector = '(//div[contains(@class, "history-card__id pok_id")])[4]'

    def __init__(self, page):
        super().__init__(page)
        self._endpoint = f'trainer/{TRAINER_ID}'

    def check_created_pokemon_in_trainers_bag(self, text):
        self.valid_url_on_page()
        self.click_selector(self.Pokemon_Selector)
        self.find_object_by_text(text)

    def check_pokeball(self, text):
        self.go_to_url()
        self.click_selector(self.Pokemon_Selector)
        self.find_object_by_text(text)
        self.object_is_visible(self.Pokeball_selector)

    def check_battle_and_attacking_pok(self, text):
        self.go_to_url()
        self.click_selector(self.History_selector)
        self.object_is_visible(self.Battle_selector)
        self.object_is_visible(self.Attacking_pokemons_id_selector)
        self.selector_have_text(self.Attacking_pokemons_id_selector, text)

    def check_battle_and_defending_pok(self, text):
        self.object_is_visible(self.Defending_pokemons_selector)
        self.selector_have_text(self.Defending_pokemons_selector, text)
