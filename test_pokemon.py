import pytest
from datetime import timedelta
from datetime import datetime
import random

from conftest import auth_session, choose_trainer, choose_pokemon
from db import create_request
from assertpy import assert_that
from constant import BASE_URL


def test_create_pokemon(create_pokemon):
    response, data = create_pokemon()
    assert_that(response.get('message')).is_equal_to('Покемон создан')
    pokemon_id = response.get('id')
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(table_data).is_length(1)
    assert_that(table_data).is_not_empty()
    assert_that(table_data[0]).contains_entry(
        {'id': int(pokemon_id)},
        {'name': data['name']},
        {'stage': 1},
        {'win_count': 0},
        {'attack': 1},
        {'trainer_id': 26010},
        {'status': 1},
        {'in_pokeball': 0},
        {'photo_id': int(data['photo_id'])}
    )
    pokemon_date = table_data[0].get('create_date')
    real_date = datetime.now() - timedelta(hours=+3)
    delta_time_1 = real_date - timedelta(seconds=8)
    delta_time_2 = real_date + timedelta(seconds=8)
    assert_that(pokemon_date).is_between(delta_time_1, delta_time_2)


def test_get_list_of_pokemons(auth_session):
    get_pokemons = auth_session.get(f'{BASE_URL}/v2/pokemons')
    response = get_pokemons.json()
    assert_that(response).is_not_empty()
    table_data = create_request(f'SELECT * FROM public.pokemons')
    assert_that(table_data).is_not_empty()


test_query_params = dict(
    argnames='query',
    argvalues=[
        'trainer_id',
        'status',
        'in_pokeball',
        'pokemon_id',
        'attack',
        'name',
        'stage'
    ]
)


@pytest.mark.parametrize(**test_query_params)
def test_get_list_with_query(auth_session, query, choose_trainer, choose_pokemon):
    def query_param():
        if query == 'trainer_id':
            random_trainer = choose_trainer().get('id')
            return random_trainer
        elif query == 'status':
            statuses = [0, 1]
            status = random.choice(statuses)
            return status
        elif query == 'in_pokeball':
            pok_statuses = [0, 1]
            pok_status = random.choice(pok_statuses)
            return pok_status
        elif query == 'pokemon_id':
            random_pokemon_by_id = choose_pokemon().get('id')
            return random_pokemon_by_id
        elif query == 'attack':
            attacks = [1, 2, 3, 4, 5, 6, 7]
            pokemon_attack = random.choice(attacks)
            return pokemon_attack
        elif query == 'name':
            random_pokemon_by_name = choose_pokemon().get('name')
            return random_pokemon_by_name
        elif query == 'stage':
            stages = [1, 2, 3]
            pokemon_stage = random.choice(stages)
            return pokemon_stage

    query_value = query_param()
    get_pokemons = auth_session.get(f'{BASE_URL}/v2/pokemons?{query}={query_value}')
    assert_that(get_pokemons.status_code).is_equal_to(200)
    if query == 'trainer_id':
        trainer = query_value
        table_data = create_request(f'SELECT * FROM public.pokemons WHERE trainer_id  = {trainer}')
        assert_that(table_data[0]).contains_entry(
            {'trainer_id': trainer}
        )
    elif query == 'status':
        table_data = create_request(f"SELECT * FROM public.pokemons WHERE status = '{query_value}'")
        assert_that(table_data[0]).contains_entry(
            {'status': query_value}
        )
    elif query == 'in_pokeball':
        table_data = create_request(f"SELECT * FROM public.pokemons WHERE status = '{query_value}'")
        assert_that(table_data[0]).contains_entry(
            {'status': query_value}
        )
    elif query == 'pokemon_id':
        table_data = create_request(f'SELECT * FROM public.pokemons WHERE id  = {query_value}')
        assert_that(table_data).is_length(1)
        assert_that(table_data[0]).contains_entry(
            {'id': query_value}
        )
    elif query == 'attack':
        table_data = create_request(f"SELECT * FROM public.pokemons WHERE attack = '{query_value}'")
        assert_that(table_data[0]).contains_entry(
            {'attack': query_value}
        )
    elif query == 'name':
        table_data = create_request(f"SELECT * FROM public.pokemons WHERE name = '{query_value}'")
        assert_that(table_data[0]).contains_entry(
            {'name': query_value}
        )
    elif query == 'stage':
        table_data = create_request(f'SELECT * FROM public.pokemons WHERE stage = {query_value}')
        assert_that(table_data[0]).contains_entry(
            {'stage': query_value}
        )
    else:
        table_data = create_request(f'SELECT * FROM public.pokemons order by attack asc')
        assert_that(table_data[0]).contains_entry(
            {'attack': 1}
        )
        table_data_reverse = create_request(f'SELECT * FROM public.pokemons order by attack desc')
        assert_that(table_data_reverse[0]).contains_entry(
            {'attack': 7}
        )


def test_change_pokemon(create_pokemon, auth_session, pokemon_data):
    response, data = create_pokemon()
    assert_that(response.get('message')).is_equal_to('Покемон создан')
    pokemon_id = response.get('id')
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(table_data).is_length(1)
    assert_that(table_data).is_not_empty()

    new_attributes_pokemon = pokemon_data()
    new_attributes_pokemon["pokemon_id"] = pokemon_id
    put_pokemon = auth_session.put(
        f'{BASE_URL}/v2/pokemons',
        json=new_attributes_pokemon
    )
    response = put_pokemon.json()
    assert_that(put_pokemon.status_code).is_equal_to(200)
    assert_that(response.get('message')).is_equal_to('Информация о покемоне обновлена')
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(table_data[0]).contains_entry(
        {'id': int(pokemon_id)},
        {'name': new_attributes_pokemon['name']},
        {'photo_id': int(new_attributes_pokemon['photo_id'])}
    )


def test_add_pokemon_in_pokeball(auth_session, create_pokemon):
    response, data = create_pokemon()
    pokemon_id = response.get('id')
    add_pokemon = auth_session.post(f'{BASE_URL}/v2/trainers/add_pokeball',
                                    json={"pokemon_id": pokemon_id})
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(add_pokemon.status_code).is_equal_to(200)
    assert_that(table_data[0]).contains_entry(
        {'in_pokeball': 1}
    )


def test_add_and_delete_pokemon_from_pokeball(auth_session, add_pokemon_in_pokeball):
    pokemon_id = add_pokemon_in_pokeball
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(table_data[0]).contains_entry(
        {'in_pokeball': 1}
    )
    delete_from_pokeball = auth_session.put(f'{BASE_URL}/v2/trainers/delete_pokeball',
                                            json={"pokemon_id": pokemon_id}
                                            )
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(delete_from_pokeball.status_code).is_equal_to(200)
    assert_that(table_data[0]).contains_entry(
        {'in_pokeball': 0}
    )


def test_battle(auth_session, add_pokemon_in_pokeball, choose_enemy_pokemon):
    mine_pokemon = add_pokemon_in_pokeball
    enemy_pokemon = str(choose_enemy_pokemon().get('id'))
    battle = auth_session.post(f'{BASE_URL}/v2/battle',
                               json={
                                   "attacking_pokemon": mine_pokemon,
                                   "defending_pokemon": enemy_pokemon
                               }
                               )
    assert_that(battle.status_code).is_equal_to(200)
    response = battle.json()
    assert_that(response.get('message')).is_equal_to('Битва проведена')


def test_get_battle(auth_session):
    get_battle = auth_session.get(f'{BASE_URL}/v2/battle')
    assert_that(get_battle.status_code).is_equal_to(200)


test_query_battle = dict(
    argnames='query',
    argvalues=[
        'trainer_id',
        'pokemon_id',
        'battle_id'
    ]
)


@pytest.mark.parametrize(**test_query_battle)
def test_get_battle_by_query(auth_session, choose_pokemon, choose_trainer, query, choose_battle):
    def query_battle_param():
        if query == 'trainer_id':
            random_trainer = choose_trainer().get('id')
            return random_trainer
        elif query == 'pokemon_id':
            random_pokemon_by_id = choose_pokemon().get('id')
            return random_pokemon_by_id
        else:
            random_battle = choose_battle().get('id')
            return random_battle

    query_param = query_battle_param()
    get_battle = auth_session.get(f'{BASE_URL}/v2/battle?{query}={query_param}')
    assert_that(get_battle.status_code).is_equal_to(200)
    if query == 'trainer_id':
        trainer = query_param
        table_data = create_request(f'SELECT * FROM public.battles '
                                    f'WHERE trainer_winner_id  = {trainer} or trainer_loser_id = {trainer}')

        for row in table_data:
            if trainer == row['trainer_winner_id'] or trainer == row['trainer_loser_id']:
                break
        else:
            raise AssertionError('Trainer not found')
    elif query == 'pokemon_id':
        table_data = create_request(f'SELECT * FROM public.battles WHERE attacking_pok_id  = {query_param}')
        if table_data != []:
            assert_that(table_data[0]).contains_entry(
                {'attacking_pok_id': query_param}
            )
        else:
            table_data_dead_pokemon = create_request(f'SELECT "in_pokeball" from public.pokemons '
                                                     f'WHERE id = {query_param} ')
            assert_that(table_data_dead_pokemon[0]).contains_entry(
                {'in_pokeball': 0}
            )

    else:
        table_data = create_request(f'SELECT * FROM public.battles WHERE id = {query_param}')
        assert_that(table_data[0]).contains_entry(
            {'id': query_param}
        )
