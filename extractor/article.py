import re
import json
import requests
import time
import logging
import pandas as pd
from datetime import datetime
from typing import Text, List, Tuple
from multiprocessing import Manager, Process, cpu_count
import pandas as pd

from globals import HEADERS, ISSUES_URL, MAGAZINE_URL, BASE_URL


class Article:
    def __init__(self, save_to_file=True, n_jobs=-1):
        self._article_links = []
        self._issues_values = []
        self._date = datetime.now()
        self._checkpoint = "UwU" if save_to_file else None
        self._article_columns = ["Survey", "Title", "Abstract", "Date", "Keywords"]
        self._n = 0
        self.n_threads = cpu_count()-1 if n_jobs == -1 else min(n_jobs, cpu_count()-1)
        self.magazine_name = self.get_magazine_name()

    def get_magazine_name(self):
        """
        Extrae el título de la revista de IEEE
        """
        
        with requests.get(MAGAZINE_URL, headers=HEADERS) as mgz:
            return mgz.json()[0]["title"]

    def get_issues(self):
        """
        Extrae el número de publicación y el número de la issue. Lo guarda en atributo _issues_values. Las issues son recorridas empezando desde el año actual hacia atrás.
        """

        logging.debug(f"GET {ISSUES_URL}")

        with requests.get(ISSUES_URL, headers=HEADERS) as issues:
            for issue in issues.json()["issuelist"]:
                for year in issue["years"]:
                    logging.debug(f"Number of issues found in the decade of {issue['decade']} by the year {year['year']}: {len(year['issues'])}")

                    # displayPublicationDate
                    if self._date.year >= int(year["year"]):
                        for iss in year['issues']:
                            self._issues_values.append(
                                (iss['publicationNumber'], iss['issueNumber']))


    def get_url_articles(self, pub_number: Text, issue_number: Text):
        """
        Extrae el enlace del artículo pasado por parámetro. Se decartan los artículos "Table of Content" o "Editorial tutorials".

        :param pub_number: Número de publicación
        :param issue_number: Número de la issue (artículo)
        :raise Exception: No se encuentra la url o no puede ser alcanzada.
        """

        issue_url = f"{BASE_URL}rest/search/pub/{pub_number}/issue/{issue_number}/toc"

        logging.debug(f"POST {issue_url}")

        payload = {
            "isnumber": issue_number,
            "punumber": pub_number,
            "sortType": "vol-only-seq"
        }

        with requests.Session() as s:
            res = s.post(issue_url, headers=HEADERS, json=payload)

            if res.status_code != 200:
                raise Exception(
                    f"Status code ({res.status_code}). No issue TOC with url: {issue_url}"
                )

            for article in res.json()["records"]:
                if "htmlLink" in article.keys():
                    self._article_links.append(article["htmlLink"])
                else:
                    self._article_links.append(article["documentLink"])

        logging.info(f"Number of documents: {len(self._article_links)}")


    def parse_article_data(self, doc: str, i: int) -> Tuple[str, str, str, List[str]]:
        """
        Dado un documento HTML de un artículo, extrae la información de titulo, abstract, fecha y palabras clave. En caso de que no exista alguno de los tres primeros mencionados, la función devolverá un Exception.

        :param doc: Contenido del documento de un artículo.
        :param i: Identificador del documento en el array (para mayor traicing de errores).
        :exception: Si no existe titulo, abstract o fecha.
        :return: Tupla de valores (title, abstract, date, keywords)
        """

        def parse_quarter(pub_date: str) -> str:
            """
            Date parser. Si la fecha no está formateada de la forma YYYY-MM-DD, entonces la convierte al primer día y mes del cuarto pasado.

            :param pub_date: Fecha de publicación en string.
            :return: DD M(Letra) YYYY
            """
            year = pub_date.split()[2]

            if 'First' in pub_date:
                return f"1 January {year}"
            elif 'Second' in pub_date:
                return  f"1 April {year}"
            elif 'Third' in pub_date:
                return  f"1 July {year}"
            elif 'Fourth' in pub_date:
                return  f"1 October {year}"
            
            return pub_date

        pattern = re.compile(
                    r"xplGlobal.document.metadata=(.*?);$", re.MULTILINE | re.DOTALL)
        metadata = ''
        # search for variable and get json in string format
        if r := re.search(pattern, doc.content.decode('utf-8')):
            metadata = r.group(1)
        else:
            raise Exception(f"No group with pattern : {re}")

        # if any non-printable character in string, delete
        metadata = re.sub(
            r'/\\x[0-9a-zA-z][0-9a-zA-z]/g', '', metadata)

        # Convert string to json
        metadata = json.loads(metadata)

        title = ''
        abstract = ''
        date = ''
        keywords = []
        
        if 'title' in metadata:
            title = metadata['title']
        elif 'displayDocTitle' in metadata:
            title = metadata['displayDocTitle']
        else:
            raise Exception(f'This IEEE website is a pice of 💩. This article does not have a Title - position: {i}')

        if "keywords" in metadata:
            ieeekeywords = metadata["keywords"][0]
            keywords = ieeekeywords["kwd"]
        else:
            raise Exception(f'No keywords on article: "{title}" - position: {i}')

        if 'abstract' not in metadata:
            raise Exception(f'No abstract on article: "{title}" - position: {i}')
        else:
            abstract = metadata['abstract']

        if 'displayPublicationDate' in metadata:
            date = parse_quarter(metadata['displayPublicationDate'])
        elif 'dateOfInsertion' in metadata:
            date = parse_quarter(metadata['dateOfInsertion'])
        else:
            raise Exception(f'No date of publication on article: "{title}" - position: {i}')

        return title, abstract, date, keywords


    def get_info_articles(self, ini: int, fini: int, articles_info: Manager) -> None:
        """
        Extrae "titulo del artículo", "abstract", "fecha de publicación" y "keywords" de los enlaces pasados, desde 'ini' hasta 'fini', guardándolo en el Manager `articles_info` pasado por parámetro.

        This is a thread based method.

        :param ini: Initial index to start.
        :param fini: Final index to stop.
        :param articles_info: List from a Manager object to save tuples.
        :raise Exception: No se encuentra la url o no puede ser alcanzada.
        """

        # Get information from slice [ini, fini]
        for i in range(int(ini), int(fini)):
            article_url = f"{BASE_URL}{self._article_links[i][1:]}"
            logging.info(f"GET {article_url} - article position: {i}")

            with requests.get(article_url, headers=HEADERS) as doc:
                if doc.status_code != 200:
                    raise Exception(
                        f"Status code ({doc.status_code}). No article with url: {article_url}"
                    )

                try:
                    title, abstract, date, keywords = self.parse_article_data(doc, i)
                except Exception as e:
                    logging.error(f'EXCEPTION: {str(e)}')
                else:
                    if datetime.strptime(date, '%d %B %Y') <= self._date:
                        article_data = (self.magazine_name, title, abstract, date, keywords)
                        articles_info.append(article_data)
                    else:
                        logging.error(f'GET article position: {i} is from dates ({date})')

    def get_all_articles(self) -> List[Tuple[Text, Text, Text, Text]]:
        """
        Helper function. Ayuda a coger la información de varios artículos

        :return: Una lista compuesta por [(Text, Text, Text, Text)]
        """

        # lista de acceso común para todos los procesos involucrados
        manager = Manager()
        articles_info = manager.list()

        # gestión de slices para cada proceso (tamaño y función a ejecutar)
        n_art = len(self._article_links)
        size = n_art/self.n_threads
        logging.debug(f'Extractor running in {self.n_threads} processes')

        # creación de procesos
        processes = []

        for i in range(0, self.n_threads):
            proc = Process(target=self.get_info_articles,
                           args=((i*size), (i*size + size), articles_info))
            processes.append(proc)

        for p in processes:
            p.start()

        for p in processes:
            p.join()

        # https://stackoverflow.com/questions/10415028/how-to-get-the-return-value-of-a-function-passed-to-multiprocessing-process
        return articles_info


    def extract(self, n: int, since: datetime = datetime.now()) -> List[Tuple[Text, Text, Text, Text]]:
        """Extrae la información de ilos últimos n artículos hasta since

        :param n: El número de artículos de los que extraer datos. Debe
            ser un entero mayor que 0.
        :param since: La fecha desde cuándo sacar la información. Debe
            ser un objeto date. si no se especifica, se presupone la
            fecha del día en el que se ejecuta la función
        :return: Una lista de tuplas donde cada tupla tendrá la
            siguiente forma: (str, str, str, str, List[str])
        """
        st = time.time()

        self._n = n
        self._date = since
        self._date = self._date.replace(year=self._date.year + 1)

        if self._checkpoint:
            self._checkpoint = f"app_n_{n}_since_{since.strftime('%Y-%m-%d')}.csv"

        self.get_issues()

        for issue in self._issues_values:
            # get articles from one issue
            self.get_url_articles(issue[0], issue[1])

            # more values than needed
            if self._n * 2 <= len(self._article_links):
                break

        articles = self.get_all_articles()
        articles = sorted(articles, key=lambda x: datetime.strptime(x[3], '%d %B %Y') and since >= datetime.strptime(x[3], '%d %B %Y'), reverse=True)[:n]

        if self._checkpoint:
            df_articles = pd.DataFrame(articles, columns=self._article_columns)
            # sorting for readability, placing abstract at the end
            new_order = ["Date", "Survey", "Title", "Keywords", "Abstract"]
            df_articles=df_articles.reindex(columns=new_order)

            df_articles.to_csv(self._checkpoint, index=False)
            logging.info(f"HE METIDO {len(df_articles)} ARTICULOS AL CSV, SALUDOS")


        logging.info(f'Tiempo de extracción: {round(time.time() - st, 3)}s')

        return articles
