import requests
from sys import stderr
import os
import multiprocessing as mp
import json

POLYRATINGS_API_BASE = 'https://api-prod.polyratings.dev/'

# arbitrary chunk size, this should be adjusted based on the performance of the workflow runner
CHUNK_SIZE = 200

def get_professors(id_list):
    print(f'Current ids: {id_list}')
    try:
        resp = requests.post(
                POLYRATINGS_API_BASE + f'admin/bulk/professors', json={'keys':id_list},
                headers={'Authorization': f'Bearer {auth_token}'},
                timeout=20
        )
    # sometimes the request to Cloudflare hangs, so we put a timeout to re-fire the request
    except requests.exceptions.ReadTimeout as _:
        resp = requests.post(
                POLYRATINGS_API_BASE + f'admin/bulk/professors',
                json={'keys':id_list}, headers={'Authorization': f'Bearer {auth_token}'},
                timeout=20
        )

    if resp.status_code != 200:
        raise RuntimeError(f'Response from API for professor {id} was not 200: {resp.status_code} and text {resp.text}')

    return resp.json()


if __name__ == '__main__':
    response = requests.post(
            POLYRATINGS_API_BASE + 'login',
            json={
                'username': os.environ['POLYRATINGS_USERNAME'],
                'password': os.environ['POLYRATINGS_PASSWORD']
                }
    )
    if response.status_code != 200:
        raise RuntimeError(f'Response from API was not 200: {response.status_code}')

    auth_token = response.json()['accessToken']

    response = requests.get(
            POLYRATINGS_API_BASE + 'admin/bulk/professors',
            headers={'Authorization': f'Bearer {auth_token}'}
    )

    if response.status_code != 200:
        raise RuntimeError(f'Response from API was not 200: {response.status_code}')


    ids = response.json()
    num_processes = os.cpu_count() - 1

    try:
        chunked_ids = [ids[i:i+CHUNK_SIZE] for i in range(0, len(ids), CHUNK_SIZE)]
        pool = mp.Pool(num_processes)
        professors = list(pool.imap_unordered(get_professors, chunked_ids))
    finally:
        pool.close()
        pool.join()

    # flatten all of the responses and make sure that we don't include the truncated prof list
    professors = [prof for sublist in professors for prof in sublist if not isinstance(prof, list)]

    with open('professor-dump.json', 'w') as f:
        json.dump(professors, f)

    # truncated prof list is just professors without reviews
    for p in professors:
        p.pop('reviews')

    with open('professor-list.json', 'w') as f:
        json.dump(professors, f)

