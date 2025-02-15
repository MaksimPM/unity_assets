import time
from celery import shared_task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

@shared_task
def scrape_unity_assets():
    from assets.models import UnityAsset
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')

    # driver = webdriver.Chrome(options=chrome_options) для запуска не из докер
    driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=chrome_options
    )
    url = 'https://assetstore.unity.com/search#nf-ec_price_filter=0...0'
    driver.get(url)

    def scroll_to_bottom(driver):
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def collect_assets(driver):
        wait = WebDriverWait(driver, 3)
        try:
            asset_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article")))
        except TimeoutException:
            return []

        assets = []
        for asset in asset_elements:
            try:
                title = asset.find_element(By.CSS_SELECTOR, 'span.relative').text
                link = asset.find_element(By.CSS_SELECTOR, 'a.focus-outline').get_attribute('href')
                publisher = asset.find_element(By.CSS_SELECTOR, 'a.caption-regular').text

                rating_text = asset.find_element(By.CSS_SELECTOR, 'div.tiny-text').text.replace("(", "").replace(")", "")
                ratings = rating_text.split('\n')
                rating, rating_count = (ratings[0], ratings[1]) if len(ratings) == 2 else (rating_text, rating_text)

                assets.append({
                    'title': title,
                    'rating': rating,
                    'rating_count': rating_count,
                    'publisher': publisher,
                    'link': link
                })
            except NoSuchElementException:
                continue
        return assets

    def get_asset_details(asset):
        original_window = driver.current_window_handle

        driver.execute_script(f"window.open('{asset['link']}', '_blank');")
        time.sleep(3)

        driver.switch_to.window(driver.window_handles[-1])
        wait = WebDriverWait(driver, 3)

        def safe_find(selector, default="Не найдено"):
            try:
                return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            except TimeoutException:
                return default

        asset['price'] = safe_find('div.mErEH._223RA').text
        asset['file_size'] = safe_find('div._27124.product-size').find_element(By.CSS_SELECTOR, 'div.SoNzt').text
        asset['version'] = safe_find('div._27124.product-version').find_element(By.CSS_SELECTOR, 'div.SoNzt').text
        asset['release_date'] = safe_find('div._27124.product-date').find_element(By.CSS_SELECTOR, 'div.SoNzt').text

        try:
            consent_button = driver.find_element(By.CSS_SELECTOR, '#onetrust-accept-btn-handler')
            if consent_button.is_displayed():
                driver.execute_script("arguments[0].click();", consent_button)
        except NoSuchElementException:
            pass

        try:
            overview_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#description"]')))
            driver.execute_script("arguments[0].click();", overview_button)
            time.sleep(3)

            asset['description'] = safe_find('div._1_3uP._1rkJa').text.replace('\n', ' ')
        except (TimeoutException, NoSuchElementException):
            asset['description'] = None

        driver.close()
        driver.switch_to.window(original_window)

        return asset

    def safe_click(element):
        try:
            element.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", element)

    all_assets = []
    page_count = 0

    while True:
        page_count += 1
        total_processed = 0
        print(f"🔁 Обрабатываем страницу {page_count}...")

        scroll_to_bottom(driver)
        assets = collect_assets(driver)

        for asset in assets:
            asset = get_asset_details(asset)
            print(asset)
            all_assets.append(asset)
            total_processed += 1
            print(f"✅ Обработано {total_processed} из 96 объектов на странице")


        try:
            next_button = WebDriverWait(driver, 2).until(
                 EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Next"]'))
             )
            """Задача в тестовом режиме на одну страницу, для полноценного поиска необходимо раскомментировать код ниже"""
            # ActionChains(driver).move_to_element(next_button).perform()

            if next_button.get_attribute('enabled'):# if next_button.get_attribute('disabled'):
                print("✅ Поиск окончен, завершаем задачу!")
                break

            try:
                # next_button.click()
                print(f"Задача завершена!")
                break
            except:
                # safe_click(next_button)
                print(f"Задача завершена!")
            time.sleep(2)

        except:
            print(f"Поиск окончен, задача завершена!")
            break


    print(f"Всего собрано объектов: {len(all_assets)}\n")

    for asset in all_assets:
        obj, created = UnityAsset.objects.update_or_create(
            link=asset['link'],
            defaults={
                'title': asset['title'],
                'rating': asset['rating'],
                'rating_count': asset['rating_count'],
                'publisher': asset['publisher'],
                'price': asset['price'],
                'file_size': asset['file_size'],
                'version': asset['version'],
                'release_date': asset['release_date'],
                'description': asset['description']
            }
        )

    try:
        driver.quit()
    except Exception as e:
        print(f"Ошибка при закрытии WebDriver: {e}")

    return f"Объекты найдены и загружены в базу данных!"
