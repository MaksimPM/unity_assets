import time
from celery import shared_task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

@shared_task
def scrape_unity_assets():
    from assets.models import UnityAsset

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')

    driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=chrome_options
    )
    url = 'https://assetstore.unity.com/search#nf-ec_price_filter=0...0'
    driver.get(url)

    def scroll_to_bottom(driver):
        last_height = driver.execute_script("return document.body.scrollHeight")
        retries = 0
        while retries < 5:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                retries += 1
            else:
                retries = 0
            last_height = new_height

    def collect_assets(driver):
        wait = WebDriverWait(driver, 30)
        asset_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "atomic-layout-section ul")))
        asset_elements = asset_element.find_elements(By.CSS_SELECTOR, "article")

        assets = []
        for asset in asset_elements:
            try:
                title = asset.find_element(By.CSS_SELECTOR, 'span.relative').text
                rating = asset.find_element(By.CSS_SELECTOR, 'div.tiny-text').text.replace("(", "").replace(")", "")
                link = asset.find_element(By.CSS_SELECTOR, 'a.focus-outline').get_attribute('href')
                publisher = asset.find_element(By.CSS_SELECTOR, 'a.caption-regular').text

                ratings = rating.split('\n')
                if len(ratings) == 2:
                    rating_value, rating_count = ratings
                else:
                    rating_value = rating
                    rating_count = None

                assets.append({
                    'title': title,
                    'rating': rating_value,
                    'rating_count': rating_count,
                    'publisher': publisher,
                    'link': link
                })
            except Exception as e:
                print(f"Ошибка при обработке элемента: {e}")
        return assets

    all_assets = []
    page_count = 0

    while True:
        page_count += 1
        print(f"Обрабатываем страницу {page_count}...")

        scroll_to_bottom(driver)
        assets = collect_assets(driver)
        all_assets.extend(assets)
        print(f"Найдено {len(assets)} объектов на странице {page_count}")

        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Next"]'))
            )

            ActionChains(driver).move_to_element(next_button).perform()

            if next_button.get_attribute('disabled'):
                print("Поиск окончен, завершаем задачу!")
                break

            try:
                next_button.click()
            except:
                driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)

        except:
            print(f"Поиск окончен, задача завершена!")
            break

    try:
        driver.quit()
    except Exception as e:
        print(f"Ошибка при закрытии WebDriver: {e}")

    print(f"Всего собрано {len(all_assets)} объектов.")

    # Сохранение в БД
    for asset in all_assets:
        obj, created = UnityAsset.objects.update_or_create(
            link=asset['link'],
            defaults={
                'title': asset['title'],
                'rating': asset['rating'],
                'rating_count': asset['rating_count'],
                'publisher': asset['publisher']
            }
        )

    return f"Объекты найдены и загружены в базу данных!"



"""Для работы не из докера рекомендуется использовать этот код:"""

# import time
# from celery import shared_task
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from assets.models import UnityAsset
#
#
# @shared_task
# def scrape_unity_assets():
#     chrome_options = Options()
#     chrome_options.add_argument('--headless')
#
#     driver = webdriver.Chrome(options=chrome_options)
#     url = 'https://assetstore.unity.com/search#nf-ec_price_filter=0...0'
#     driver.get(url)
#
#     def scroll_to_bottom(driver):
#         last_height = driver.execute_script("return document.body.scrollHeight")
#         while True:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(2)
#             new_height = driver.execute_script("return document.body.scrollHeight")
#             if new_height == last_height:
#                 break
#             last_height = new_height
#
#     def collect_assets(driver):
#         wait = WebDriverWait(driver, 60)
#         asset_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "atomic-layout-section ul")))
#         asset_elements = asset_element.find_elements(By.CSS_SELECTOR, "article")
#
#         assets = []
#         for asset in asset_elements:
#             try:
#                 title = asset.find_element(By.CSS_SELECTOR, 'span.relative').text
#                 rating = asset.find_element(By.CSS_SELECTOR, 'div.tiny-text').text.replace("(", "").replace(")", "")
#                 link = asset.find_element(By.CSS_SELECTOR, 'a.focus-outline').get_attribute('href')
#                 publisher = asset.find_element(By.CSS_SELECTOR, 'a.caption-regular').text
#
#                 ratings = rating.split('\n')
#                 if len(ratings) == 2:
#                     rating_value, rating_count = ratings
#                 else:
#                     rating_value = rating
#                     rating_count = None
#
#                 assets.append({
#                     'title': title,
#                     'rating': rating_value,
#                     'rating_count': rating_count,
#                     'publisher': publisher,
#                     'link': link
#                 })
#             except Exception as e:
#                 print(f"Ошибка при обработке элемента: {e}")
#         return assets
#
#     all_assets = []
#
#     while True:
#         scroll_to_bottom(driver)
#         assets = collect_assets(driver)
#         all_assets.extend(assets)
#
#         try:
#             next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next"]')
#             if next_button.get_attribute('disabled'):
#                 break
#             else:
#                 next_button.click()
#                 time.sleep(5)
#         except Exception as e:
#             print(f"Ошибка при переходе на следующую страницу: {e}")
#             break
#
#     driver.quit()
#
#     # Сохраняем данные в базу
#     for asset in all_assets:
#         UnityAsset.objects.update_or_create(
#             link=asset['link'],
#             defaults={
#                 'title': asset['title'],
#                 'rating': asset['rating'],
#                 'rating_count': asset['rating_count'],
#                 'publisher': asset['publisher']
#             }
#         )
#
#     return f"Собрано {len(all_assets)} объектов»
#
#