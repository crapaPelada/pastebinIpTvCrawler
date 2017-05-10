import pickle
import requests
from selenium import webdriver
from time import sleep, time
from pathlib import Path
from os.path import expanduser


def timer(func):
    def wrapper(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        duration = time() - t1
        print(func.__name__, duration)
        return result
    return wrapper


@timer
def crawlNewResults(url):
    # driver = webdriver.Chrome()
    driver = webdriver.PhantomJS()
    driver.get(url)
    sleep(2)
    driver.find_element_by_class_name('gsc-selected-option').click()
    sleep(2)
    driver.find_elements_by_class_name('gsc-option')[1].click()
    sleep(2)
    url_elements = driver.find_elements_by_css_selector('.gsc-url-top .gs-visibleUrl-long')
    keys = {element.text.split('/')[-1] for element in url_elements if element.text}
    driver.quit()
    return keys


def saveResults(results, path='urls.data'):
    with open(path, 'wb+') as fp:
        pickle.dump(results, fp)


def loadResults(path='urls.data'):
    my_file = Path(path)
    if my_file.exists():
        with open(path, 'rb+') as fp:
            results = pickle.load(fp)
            return results
    else:
        return set()


def generatePlistFile(keys, keyword, path=expanduser("~") + '/Desktop/iptv.m3u'):
    channels = []
    for key in keys:
        lines = iter(getRawFile(key).splitlines())
        for line in lines:
            if line.startswith('#EXTINF') and keyword.lower() in line.lower():
                channels.append(line)
                channels.append(next(lines))

    with open(path, 'a') as fp:
        fp.write('#EXTM3U\n')
        fp.writelines('\n'.join(channels))


def getRawFile(key, basePath='https://pastebin.com/raw/'):
        return requests.get(basePath + key).text


if __name__ == "__main__":
    # keywords to search for
    keywords = ['CNN', 'BBC']

    URL = 'https://pastebin.com/search?q='
    results = loadResults()
    for keyword in keywords:
        newResults = crawlNewResults(URL + keyword)
        results |= newResults
        generatePlistFile(results, keyword)
    saveResults(results)
