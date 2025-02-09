from BasePage import BasePage
from constant import TRAINER_ID


class TrainerPage(BasePage):
    Pokemon_Selector = ('#root > div > main:nth-child(2) > section > div.trainer-item__content '
                        '> div.content__inner > div.content__box.content__box-mobile '
                        '> div.trainer-item__pokemons.k_cart_trainer_pokemons_history_div > a')
    Pokeball_selector = ('#root > div > main:nth-child(2) > section > div.trainer-item__content '
                         '> div.content__inner > div.content__box.content__box-mobile '
                         '> div.trainer-item__pokemons.list-open.k_cart_trainer_pokemons_history_div '
                         '> div.pokemons-dropdown__list.list-open.k_cart_trainer_pokemons_history_div_drop '
                         '> div:nth-child(150) > div > div > div.k_pokemon_flex_att_icon '
                         '> div.title-single__icon.k_title_icon_status_pok > img')
    History_selector = ('#root > div > main:nth-child(2) > section > div.trainer-item__content '
                        '> div.content__inner > div.content__box.content__box-mobile > div.trainer-item__history > a')
    Battle_selector = ('#root > div > main:nth-child(2) > section > div.trainer-item__content > div.content__inner '
                       '> div.content__box.content__box-mobile > div.trainer-item__history.list-open '
                       '> div.history__list.list-open.k_trassing_repeater_battles '
                       '> div.history-item.k_trassing_block_battles.k_battle_0 > div.history-item__content')
    Attacking_pokemons_id_selector = ('#root > div > main:nth-child(2) > section > '
                                      'div.trainer-item__content > div.content__inner '
                                      '> div.content__box.content__box-mobile > div.trainer-item__history.list-open '
                                      '> div.history__list.list-open.k_trassing_repeater_battles '
                                      '> div.history-item.k_trassing_block_battles.k_battle_0 '
                                      '> div.history-item__content > div.history-card.k_trassing_r_my_pokemon.victory '
                                      '> div.history-card__box.pokemons__link_h > div')
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

    def check_battle(self, text):
        self.go_to_url()
        self.click_selector(self.History_selector)
        self.object_is_visible(self.Battle_selector)
        self.object_is_visible(self.Attacking_pokemons_id_selector)
