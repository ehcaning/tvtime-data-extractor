import requests
import os
import json
import datetime

# non-sensitive information
USER_AGENT = "TVTime for iOS 8.44.0-202208302674-prod"
APP_VERSION = "202208302674"
X_API_Key = "LhqxB7GE9a95beFHqiNC85GHdrX8hNi34H2uQ7QG"


def login():
    url = "https://api2.tozelabs.com/v2/signin"

    payload = {
        'username': os.getenv('USERNAME'),
        'password': os.getenv('PASSWORD')
    }
    response = requests.post(url,  data=payload)
    json_response = response.json()

    return json_response['tvst_access_token'], json_response['id']


def get_moveis(tvst_access_token, user_id):
    url = f'https://msapi.tvtime.com/prod/v1/tracking/cgw/follows/user/{user_id}?app_version=8.44.0&entity_type=movie&sort=watched_date,desc'
    headers = {
        'Authorization': f'Bearer {tvst_access_token}',
        'User-Agent': USER_AGENT,
        'X-API-Key': X_API_Key,
        'app-version': APP_VERSION,
        'country-code': "en",
        'user-lang-setting': "en",
    }

    response = requests.get(url, headers=headers)
    json_response = response.json()

    return json_response


def dump_to_file(data, file_name):
    with open(f'{file_name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_csv(data, file_name):
    with open(f'{file_name}.csv', 'w', encoding='utf-8') as f:
        f.write(
            'name\tposters\twatched_date\tis_watched\tgenres\tfirst_release_date\tis_released\truntime\n')
        for movie in data['data']['objects']:
            name = movie['meta']['name']
            posters = movie['meta']['posters'][0]['url'] if len(
                movie['meta']['posters']) > 0 else ""
            is_watched = True if 'is_watched' in movie[
                'extended'] and movie['extended']['is_watched'] else False
            watched_date = ""
            for item in movie['sorting']:
                if item['id'] == 'watched_date':
                    watched_date = item['value']
                    break
            genres = ",".join(movie['meta']['genres'])
            first_release_date = movie['meta']['first_release_date']
            is_released = movie['meta']['is_released']
            runtime = movie['meta']['runtime'] / 60
            f.write(
                f'{name}\t{posters}\t{watched_date}\t{is_watched}\t{genres}\t{first_release_date}\t{is_released}\t{runtime}\n')


if __name__ == "__main__":
    tvst_access_token, user_id = login()
    moveis_data = get_moveis(tvst_access_token, user_id)

    dump_to_file(moveis_data, str(datetime.datetime.now()))
    create_csv(moveis_data, str(datetime.datetime.now()))
