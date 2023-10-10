import pandas as pd
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import chromedriver_autoinstaller


parent_path = Path(os.path.abspath(__file__)).parents[1]
data_path = 'dataset\meteo'
directory = os.path.join(parent_path, data_path)



def get_temperature(driver):
    driver.get('http://ecodata.kz:3838/dm_climat_ru/')


    temperature= driver.find_element(By.LINK_TEXT, "Температура")
    temperature.click()

    air_humidity = driver.find_element(By.LINK_TEXT, "Воздуха")
    air_humidity.click()

    region = driver.find_element(By.ID, 'region_3h_air-selectized')
    region.click()

    wait = WebDriverWait(driver, 10)
    region = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#region_3h_air + .selectize-control .selectize-dropdown-content")))

    
    kz_alm = region.find_element(By.XPATH, "//div[@data-value='KZ-ALM']")
    kz_alm.click()

    wait = WebDriverWait(driver, 10)
    city = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#stn_3h_air + .selectize-control .selectize-dropdown-content")))
    alm = city.find_element(By.XPATH, "//div[@data-value='4327690']")
    alm.click()

    date_range= driver.find_element(By.ID, "date_air")
    input_dates = date_range.find_elements(By.TAG_NAME, "input")
    input_dates[0].clear()
    input_dates[1].clear()
    input_dates[0].send_keys("2011-01-01")
    input_dates[1].send_keys("2023-01-01")

    wait = WebDriverWait(driver, 20)
    wait.until(EC.text_to_be_present_in_element_attribute((By.CLASS_NAME, 'dataTables_processing'), 'style', 'display: none'))


    wait = WebDriverWait(driver, 10)
    excel_download = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Excel')]")))
    excel_download.click()

    while True:
        time.sleep(1)
        files = os.listdir(directory)
        if any('.crdownload' in f for f in files):
            continue
        else:
            break

    old_file_name = max([os.path.join(directory, f) for f in os.listdir(directory)], key=os.path.getctime)
    new_file_name = os.path.join(directory, 'temperature.xlsx')
    os.rename(old_file_name, new_file_name)

def get_humidity(driver):
    driver.get('http://ecodata.kz:3838/dm_climat_ru/')


    air_humidity = driver.find_element(By.XPATH, "//a[@data-value='humidity_3h']")
    air_humidity.click()

    region = driver.find_element(By.ID, 'region_3h_humid-selectized')
    region.click()

    wait = WebDriverWait(driver, 10)
    region = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#region_3h_humid + .selectize-control .selectize-dropdown-content")))

    
    kz_alm = region.find_element(By.XPATH, "//div[@data-value='KZ-ALM']")
    kz_alm.click()

    wait = WebDriverWait(driver, 10)
    city = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#stn_3h_humid + .selectize-control .selectize-dropdown-content")))
    alm = city.find_element(By.XPATH, "//div[@data-value='4327690']")
    alm.click()

    date_range= driver.find_element(By.ID, "date_humid")
    input_dates = date_range.find_elements(By.TAG_NAME, "input")
    input_dates[0].clear()
    input_dates[1].clear()
    input_dates[0].send_keys("2011-01-01")
    input_dates[1].send_keys("2022-10-01")

    
    wait = WebDriverWait(driver, 20)

    wait.until(EC.text_to_be_present_in_element_attribute((By.CLASS_NAME, 'dataTables_processing'), 'style', 'display: none'))

    wait = WebDriverWait(driver, 10)
    excel_download = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Excel')]")))
    excel_download.click()

    while True:
        time.sleep(1)
        files = os.listdir(directory)
        if any('.crdownload' in f for f in files):
            continue
        else:
            break

    old_file_name = max([os.path.join(directory, f) for f in os.listdir(directory)], key=os.path.getctime)
    new_file_name = os.path.join(directory, 'humidity.xlsx')
    os.rename(old_file_name, new_file_name)



try:
    chromedriver_autoinstaller.install()

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("prefs", {
        "download.default_directory": directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=options)

    get_temperature(driver)
    get_humidity(driver)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit() 


temperature = pd.read_excel(os.path.join(directory, 'temperature.xlsx'),  
                            skiprows=2,
                            index_col=1, 
                            header=0).iloc[:, 1:]
df1 = temperature.copy()
df1.index = pd.to_datetime(df1.index)
df1 = df1.groupby(pd.Grouper(freq='M')).mean()
df1 = df1.rename(index=lambda Index: str(Index)[:7].replace('-', '_'))
df1['mean_temp'] = df1.mean(axis=1)
df1.drop(df1.columns.difference(['mean_temp']), axis=1, inplace=True)


humidity = pd.read_excel(os.path.join(directory, 'humidity.xlsx'),  
                            skiprows=2,
                            index_col=1, 
                            header=0).iloc[:, 1:]
df2 = humidity.copy()
df2.index = pd.to_datetime(df2.index)
df2 = df2.groupby(pd.Grouper(freq='M')).mean()
df2 = df2.rename(index=lambda Index: str(Index)[:7].replace('-', '_'))
df2['mean_rh'] = df2.mean(axis=1)
df2.drop(df2.columns.difference(['mean_rh']), axis=1, inplace=True)


dataset_dir = os.path.join(Path(directory).parents[0], 'dataset.csv')

df = pd.read_csv(dataset_dir, sep='\t', index_col=0)

df['temperature'] = df1['mean_temp']
df['humidity'] = df2['mean_rh']

df.to_csv(dataset_dir, sep='\t', encoding='utf-8')
