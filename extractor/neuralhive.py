"""Agente extractor de datos de artículos

Este agente se encarga de la extracción de datos de la revista
COMOSELLAME.

Para funcionar, el script requiere que estén instaladas las
bibliotecas `numpy` y `requests`.

Para más información acerca de buenas prácticas de documentación
de código el siguiente enlace es muy bueno:

    - https://realpython.com/documenting-python-code/

También, para una introducción rápida a Python con bastante cosas que
ya habéis visto y otras tantas nuevas, podéis visitar los siguientes
enlaces:

    - https://docs.python.org/3/tutorial/
    - https://try.codecademy.com/learn-python-3
    - https://realpython.com/python-first-steps/
"""

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException


def extract(n, since=None):
    """Extrae la información de ilos últimos n artículos hasta since

    :param n: El número de artículos de los que extraer datos. Debe
        ser un entero mayor que 0.
    :param since: La fecha desde cuándo sacar la información. Debe
        ser un objeto date. si no se especifica, se presupone la
        fecha del día en el que se ejecuta la función
    :return: Una lista de tuplas donde cada tupla tendrá la
        siguiente forma: (str, str, str, str, List[str])
    """

    base_url = "https://ieeexplore.ieee.org/"
    page_url = base_url + "xpl/RecentIssue.jsp?punumber=9739"

    last_article_query = "stats-jhp-latest-articles-tab"
    show_all_query = "u-mt-02"
    articles_query = "List-results-items"
    title_query = "//a[contains(@href, '/document')]"

    # Results from scrap
    result = []

    # Using Firefox explorer for dynamic scrapping
    driver = webdriver.Firefox()
    driver.get(page_url)

    try:
        # Create a wait for Firefox
        wait = WebDriverWait(driver, timeout=10, poll_frequency=1, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])

        # Wait for element "Latest articles" to be clickable
        menu = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, last_article_query)))

        # Scroll to "Latest articles"
        driver.execute_script(f"window.scrollTo({menu.location['x']}, {menu.location['y']})")
        menu.click()

        # if number of articles > 5, change page.
        if n > 5:
            # Wait for element "Show all" to be visible
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, show_all_query)))
            show_more = driver.find_element(By.CLASS_NAME, 'u-mt-02')

            # TODO: This can be done with ActionChain
            # Scroll to "Show all"
            driver.execute_script(f"window.scrollTo({show_more.location['x']}, {show_more.location['y']})")
            show_more.click()

            # Get all divs from articles
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, articles_query)))

            # TODO: use namedtuple Article
            # Information like "Article name", "date", "abstract" is inside $page_url
            # Fill result with (str, str, str, str, [str]) or Article
            result = [
                (
                    # Get title from article
                    article.find_element(By.XPATH, title_query).get_attribute("innerHTML"),
                )
                # iterate over different values
                for article in driver.find_elements(By.CLASS_NAME, articles_query)
            ]
        else:
            result = [
                (
                    article.find_element(By.CLASS_NAME, title_query).get_attribute("innerHTML"),
                )
                for article in driver.find_elements(By.TAG_NAME, "li")
            ]

    except Exception as e:
        print(e)
    else:
        # Do things
        print(article_links)
    finally:
        driver.quit()

        # Aquí el cuerpo de la función
        return result


if __name__ == '__main__':
    # for row in extract(n=20):
    print(extract(10))
