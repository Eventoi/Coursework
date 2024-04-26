import json
import pprint
import requests
import sys
import tqdm



vk_owner_id = input('Введите VK ID: ')
vk_access_token = input('Введите VK токен: ')
yandex_disk_token = input('Введите токен Яндекс Диска: ')



class VK:
    def get_vk_photos(self, vk_owner_id, vk_access_token):
        session = requests.Session()
        response = session.get(f"https://api.vk.com/method/photos.get?owner_id={vk_owner_id}&album_id=profile&extended=1&count=5&access_token={vk_access_token}&v=5.199")

# Пришлось добавить каунтер из-за возможного одинакового количества лайков. Это единственное быстрое решение, пришедшее в голову
# Так же: фотки, добавленные до 2012 года, не забэкапятся с максимальным разрешением
# (см. https://dev.vk.com/ru/reference/objects/photo-sizes#%D0%97%D0%BD%D0%B0%D1%87%D0%B5%D0%BD%D0%B8%D1%8F%20type%20%D0%B4%D0%BB%D1%8F%20%D1%84%D0%BE%D1%82%D0%BE%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D0%B9)

        photos = []
        file_counter = 0
        for item in response.json()['response']['items']:
            max_size = max(item['sizes'], key=lambda x: x['width'] * x['height'])
            photos.append({'file_name': f"{item['likes']['count']}_{file_counter}.jpg", 'url': max_size['url']})
            file_counter += 1

        return photos

pprint.pprint(VK().get_vk_photos(vk_owner_id, vk_access_token))



class Yandex:
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    
    def save_photos_to_disk(self, photos, yandex_disk_token, folder_name):
        headers = {'Authorization': f'OAuth {yandex_disk_token}'}
        params = {'path': folder_name}
        requests.put(self.url, headers=headers, params=params)
        for photo in tqdm.tqdm(photos, desc='Загрузка фотографий', unit='photo'):
            upload_url = f"{self.url}/upload?path={folder_name}/{photo['file_name']}"
            response = requests.post(upload_url, headers=headers, params={'url': photo['url']})

        print('Фотографии загружены успешно!')



class Logs:
    def save_photos_info_to_json(self, photos, file_name):
        with open(file_name, 'w') as file:
            json.dump(photos, file, indent=4)
        print(f'Информация о фотографиях сохранена в {file_name}')



if __name__ == '__main__':
    # Получаем фотографии с профиля пользователя ВКонтакте
    vk_photos = VK().get_vk_photos(vk_owner_id, vk_access_token)

    # Создаем папку на Яндекс.Диске и сохраняем фотографии
    vk_photos_to_yandex_disk = Yandex().save_photos_to_disk(vk_photos, yandex_disk_token, folder_name=input('Введите имя папки: '))

    # Сохраняем информацию по фотографиям в JSON-файл
    save_logs = Logs().save_photos_info_to_json(vk_photos, file_name='photos.json')

    # Спрашиваем пользователя о выходе. Это для компиляции экзешника
    input("Для выхода из программы нажмите любую клавишу...")
    sys.exit()