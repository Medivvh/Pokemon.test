import pytest
import requests
import random

from playwright.sync_api import sync_playwright
from requests import session
from sqlalchemy.orm import scoped_session
from LoginPage import LoginPage
from BasePage import BasePage
from db import create_request

from constant import HEADERS, BASE_URL
from faker import Faker
from assertpy import assert_that

fake = Faker('EN')


@pytest.fixture
def auth_session():
    """Создаёт сессию с авторизацией и возвращает объект сессии."""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


@pytest.fixture
def pokemon_data():
    def _pokemon_data():
        photo_id = str(random.randint(1, 1008))
        return {
            "name": fake.first_name() + f"{photo_id}",
            "photo_id": photo_id
        }

    return _pokemon_data


@pytest.fixture
def create_pokemon(auth_session, pokemon_data):
    pokemon_id = None

    def _create_pokemon():
        nonlocal pokemon_id
        data = pokemon_data()
        new_pokemon = auth_session.post(
            f"{BASE_URL}/v2/pokemons",
            json=data
        )
        assert_that(new_pokemon.status_code).is_equal_to(201)
        pokemon_id = new_pokemon.json().get('id')
        return new_pokemon.json(), data

    yield _create_pokemon
    pokemon_list = create_request(f'SELECT status FROM public.pokemons WHERE id = {pokemon_id}')
    if pokemon_list[0] == {'status': 1}:

        remove_pokemon = auth_session.post(
            f"{BASE_URL}/v2/pokemons/knockout",
            json={"pokemon_id": pokemon_id}
        )
        assert_that(remove_pokemon.status_code).is_equal_to(200)
    else:
        assert_that(pokemon_list[0]).contains_entry(
            {'status': 0}
        )


@pytest.fixture
def choose_trainer():
    def _choose_trainer():
        list_of_trainers = create_request(f'SELECT trainers.id FROM public.trainers '
                                          f'RIGHT JOIN public.pokemons ON trainers.id = pokemons.trainer_id '
                                          f'order by random() limit 1')
        return list_of_trainers  # random_trainer

    return _choose_trainer


@pytest.fixture
def choose_pokemon():
    def _choose_pokemon():
        list_of_pokemons = create_request(f'SELECT * FROM public.pokemons '
                                          f'order by random() limit 1')
        return list_of_pokemons

    return _choose_pokemon


@pytest.fixture
def choose_enemy_pokemon():
    def _choose_enemy_pokemon():
        list_of_pokemons = create_request(f'SELECT * FROM public.pokemons WHERE "in_pokeball" = 1 '
                                          f'AND NOT "trainer_id" = 26010 ORDER BY random() limit 1')
        random_pokemon = random.choice(list_of_pokemons)
        return random_pokemon

    return _choose_enemy_pokemon


@pytest.fixture
def add_pokemon_in_pokeball(auth_session, create_pokemon):
    def _add_in_pokeball():   #new
        response, data = create_pokemon()
        pokemon_id = response.get('id')
        add_pokemon = auth_session.post(f'{BASE_URL}/v2/trainers/add_pokeball',
                                        json={"pokemon_id": pokemon_id})
        assert_that(add_pokemon.status_code).is_equal_to(200)
        return pokemon_id

    return _add_in_pokeball


@pytest.fixture
def choose_battle():
    def _choose_battle():
        list_of_battles = create_request(f'SELECT * FROM public.battles order by random() limit 1')

        return list_of_battles

    return _choose_battle


@pytest.fixture
def battle(auth_session, add_pokemon_in_pokeball, choose_enemy_pokemon):
    mine_pokemon = add_pokemon_in_pokeball
    enemy_pokemon = str(choose_enemy_pokemon().get('id'))
    battle = auth_session.post(
        f'{BASE_URL}/v2/battle',
        json={
            "attacking_pokemon": mine_pokemon,
            "defending_pokemon": enemy_pokemon
        }
    )
    assert_that(battle.status_code).is_equal_to(200)
    assert_that(battle.json().get('message')).is_equal_to('Битва проведена')
    return battle


@pytest.fixture(scope='session')
def page():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, slow_mo=500)  # напомнить Тимуру показать без параметров
    page = browser.new_page()
    yield page
    browser.close()
    playwright.stop()


@pytest.fixture()
def base_page(page):
    base = BasePage(page)
    return base


@pytest.fixture()  # Fixture authorisation page
def auth(page):
    auth = LoginPage(page)
    return auth
