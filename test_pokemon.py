import pytest
from datetime import timedelta
from datetime import datetime
import random
from constant import Login, Password
from conftest import auth_session, choose_trainer, choose_pokemon
from db import create_request
from assertpy import assert_that
from constant import BASE_URL


def test_create_pokemon(create_pokemon, auth):
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
    auth.login(Login, Password)


def test_get_list_of_pokemons(auth_session):
    get_pokemons = auth_session.get(f'{BASE_URL}/v2/pokemons')
    response = get_pokemons.json()
    assert_that(response).is_not_empty()
    table_data = create_request(f'SELECT * FROM public.pokemons ORDER BY "id" DESC LIMIT 60')
    assert_that(table_data).is_not_empty()
    for index, item in enumerate(response.get('data')):
        assert_that(item).contains_entry(
            {'id': str(table_data[index]['id'])},
            {'name': table_data[index]['name']},
            {'stage': str(table_data[index]['stage'])},
            {'photo_id': table_data[index]['photo_id']},
            {'attack': table_data[index]['attack']},
            {'trainer_id': str(table_data[index]['trainer_id'])},
            {'status': table_data[index]['status']},
            {'in_pokeball': table_data[index]['in_pokeball']}
        )


@pytest.mark.parametrize(
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
def test_get_list_with_query(auth_session, query, choose_trainer, choose_pokemon):
    query_value = {
        'trainer_id': choose_trainer()[0].get('id'),
        'status': random.choice([0, 1]),
        'in_pokeball': random.choice([0, 1]),
        'pokemon_id': choose_pokemon()[0].get('id'),
        'attack': random.choice([1, 2, 3, 4, 5, 6, 7]),
        'name': choose_pokemon()[0].get('name'),
        'stage': random.choice([1, 2, 3])
    }
    get_pokemons = auth_session.get(f'{BASE_URL}/v2/pokemons?{query}={query_value[query]}')
    assert_that(get_pokemons.status_code).is_equal_to(200)

    sql_query = query if query != 'pokemon_id' else 'id'
    sql_select = f'SELECT * FROM public.pokemons WHERE {sql_query} = {query_value[query]} ORDER BY "id" DESC LIMIT 60' \
        if query != 'name' else f'SELECT * FROM public.pokemons WHERE {sql_query} = \'{query_value[query]}\' '
    table_data = create_request(sql_select)

    db_ids = sorted([str(pok_id['id']) for pok_id in table_data])
    get_list_ids = sorted([pok_id['id'] for pok_id in get_pokemons.json().get('data')])
    assert_that(db_ids).is_equal_to(get_list_ids)



def test_change_pokemon(create_pokemon, auth_session, pokemon_data):
    response, data = create_pokemon()
    assert_that(response.get('message')).is_equal_to('Покемон создан')
    pokemon_id = response.get('id')
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(table_data).is_length(1)

    new_attributes_pokemon = pokemon_data()
    new_attributes_pokemon["pokemon_id"] = pokemon_id
    put_pokemon = auth_session.put(
        f'{BASE_URL}/v2/pokemons',
        json=new_attributes_pokemon
    )
    assert_that(put_pokemon.status_code).is_equal_to(200)
    response = put_pokemon.json()
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
    assert_that(add_pokemon.status_code).is_equal_to(200)
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(table_data[0]).contains_entry(
        {'in_pokeball': 1}
    )


def test_delete_pokemon_from_pokeball(auth_session, add_pokemon_in_pokeball):
    pokemon_id = add_pokemon_in_pokeball
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(table_data[0]).contains_entry(
        {'in_pokeball': 1}
    )
    delete_from_pokeball = auth_session.put(f'{BASE_URL}/v2/trainers/delete_pokeball',
                                            json={"pokemon_id": pokemon_id}
                                            )
    assert_that(delete_from_pokeball.status_code).is_equal_to(200)
    table_data = create_request(f"SELECT * FROM public.pokemons WHERE id = '{pokemon_id}'")
    assert_that(table_data[0]).contains_entry(
        {'in_pokeball': 0}
    )

def test_battle(battle):
    battle_id = battle.json().get('id')
    table_data = create_request(f"SELECT * FROM public.battles WHERE id = '{battle_id}'")
    assert_that(table_data).is_not_empty()
    assert_that(table_data[0]).contains_entry(
        {'id': int(battle_id)}
    )


def test_get_battles(auth_session):
    get_battle = auth_session.get(f'{BASE_URL}/v2/battle')
    assert_that(get_battle.status_code).is_equal_to(200)


@pytest.mark.parametrize(
    argnames='query',
    argvalues=[
        'trainer_id',
        'pokemon_id',
        'battle_id'
    ]
)
def test_get_battle_by_query(auth_session, choose_pokemon, choose_trainer, query, choose_battle):
    query_param = {
        'trainer_id': choose_trainer()[0].get('id'),
        'pokemon_id': choose_pokemon()[0].get('id'),
        'battle_id': choose_battle()[0].get('id')
    }
    get_battle = auth_session.get(f'{BASE_URL}/v2/battle?{query}={query_param[query]}')
    assert_that(get_battle.status_code).is_equal_to(200)
    if query == 'trainer_id':
        trainer = query_param[query]
        table_data = create_request(f'SELECT * FROM public.battles '
                                    f'WHERE trainer_winner_id  = {trainer} '
                                    f'or trainer_loser_id = {trainer}')

        for row in table_data:
            if trainer == row['trainer_winner_id'] or trainer == row['trainer_loser_id']:
                break
        else:
            raise AssertionError('Trainer not found')
    elif query == 'pokemon_id':
        table_data = create_request(f'SELECT * FROM public.battles WHERE attacking_pok_id  = {query_param[query]}')
        if table_data != []:
            assert_that(table_data[0]).contains_entry(
                {'attacking_pok_id': query_param}
            )
        else:
            table_data_dead_pokemon = create_request(f'SELECT "in_pokeball" from public.pokemons '
                                                     f'WHERE id = {query_param[query]} ')
            assert_that(table_data_dead_pokemon[0]).contains_entry(
                {'in_pokeball': 0}
            )

    else:
        table_data = create_request(f'SELECT * FROM public.battles WHERE id = {query_param[query]}')
        assert_that(table_data[0]).contains_entry(
            {'id': query_param[query]}
        )
