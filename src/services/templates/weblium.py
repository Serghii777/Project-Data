import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL сайту
url = 'https://gramatykapolskiego.weblium.site/?fbclid=IwZXh0bgNhZW0BMAABHR9muhl4oxnVssmnYPEWV_yqgFU5zrdtVsVeejiUutwkGdNZ8G0hm4Sduw_aem_y1vax2peYf1w4Woqj2Re6Q&sfnsn=mo'

# Створюємо папку для збереження файлів
if not os.path.exists('site_data'):
    os.makedirs('site_data')

# Отримуємо HTML-код
response = requests.get(url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Функція для завантаження файлів
def download_file(url, folder):
    file_name = os.path.join(folder, os.path.basename(url))
    with open(file_name, 'wb') as file:
        file.write(requests.get(url).content)
    return file_name

# Завантажуємо всі стилі (CSS-файли)
for link in soup.find_all('link', {'rel': 'stylesheet'}):
    href = link.get('href')
    css_url = urljoin(url, href)
    file_path = download_file(css_url, 'site_data')
    link['href'] = file_path  # Оновлюємо шлях у HTML

# Завантажуємо всі зображення (img-теги)
for img in soup.find_all('img'):
    src = img.get('src')
    img_url = urljoin(url, src)
    file_path = download_file(img_url, 'site_data')
    img['src'] = file_path  # Оновлюємо шлях у HTML

# Завантажуємо всі скрипти (JS-файли)
for script in soup.find_all('script', {'src': True}):
    src = script.get('src')
    js_url = urljoin(url, src)
    file_path = download_file(js_url, 'site_data')
    script['src'] = file_path  # Оновлюємо шлях у HTML

# Зберігаємо оновлений HTML з локальними шляхами
with open('site_data/index.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))

print("Завантаження завершено. Відкрийте 'site_data/index.html', щоб переглянути сайт.")
