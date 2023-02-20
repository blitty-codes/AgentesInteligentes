import re
import json
import requests
from datetime import datetime

from globals import headers, base_url, issues_url


class Article:
    def __init__(self, debug=True, save_to_file=True):
        self._article_links = []
        self._issues_values = []
        self.debug = debug
        self.file_name = '' if save_to_file else None

    def get_issues(self):
        """
        Extrae el número de publicación y el número de la issue. Lo guarda en atributo _issues_values. Las issues son recorridas empezando desde el año actual hacia atrás.
        """

        if self.debug:
            print(f"[+] GET {issues_url}")

        with requests.get(issues_url, headers=headers) as issues:
            for issue in issues.json()["issuelist"]:
                if self.debug:
                    print(f"[*] Decade: {issue['decade']}")
                    print(f"\t{issue['years']}")

                for year in issue["years"]:
                    if self.debug:
                        print(f"\t\t[*] Year: {year['year']}")
                        print(
                            f"\t\t\t[-] Number of issues: {len(year['issues'])}")

                    for iss in year['issues']:
                        self._issues_values.append(
                            (iss['publicationNumber'], iss['issueNumber']))

    def get_n_articles(self, pub_number, issue_number, n):
        """
        Extrae el enlace del artículo pasado por parámetro. Se decartan los artículos "Table of Content" o "Editorial tutorials".

        :param pub_number: número de publicación
        :param issue_number: número de la issue (artículo)
        :param n: El número de artículos de los que extraer datos. Debe
            ser un entero mayor que 0.
        :raise Exception: No se encuentra la url o no puede ser alcanzada.
        """

        issue_url = f"{base_url}rest/search/pub/{pub_number}/issue/{issue_number}/toc"

        if self.debug:
            print(f"[+] POST {issue_url}")

        payload = {
            "isnumber": issue_number,
            "punumber": pub_number,
            "sortType": "vol-only-seq"
        }

        with requests.Session() as s:
            res = s.post(issue_url, headers=headers, json=payload)

            if res.status_code != 200:
                raise Exception(
                    f"Status code ({res.status_code}). No issue TOC with url: {issue_url}"
                )

            for article in res.json()["records"]:
                # don't get articles like TOC or tutorials from IEEE
                if "Editorial:" not in article["articleTitle"] and "Table of" not in article["articleTitle"]:
                    if "htmlLink" in article.keys():
                        self._article_links.append(article["htmlLink"])
                    else:
                        self._article_links.append(article["documentLink"])

        # no realizar busquedas de más
        self._article_links = self._article_links[:n]

        if self.debug:
            print(f"[*] INFO: Number of documents: {len(self._article_links)}")

    def get_info_article(self, article_url) -> (str, str, str, [str]):
        """
        Extrae "titulo del artículo", "abstract", "fecha de publicación" y "keywords" del enlace del artículo pasado por parámetro.

        :param article_url: URL del artículo.
        :raise Exception: No se encuentra la url o no puede ser alcanzada.
        :return: Una tupla de la siguiente forma : (str, str, str, List[str])
        """

        if self.debug:
            print(f"[+] GET {article_url}")

        with requests.get(article_url, headers=headers) as doc:
            if doc.status_code != 200:
                raise Exception(
                    f"Status code ({doc.status_code}). No article with url: {article_url}"
                )

            pattern = re.compile(
                r"xplGlobal.document.metadata=(.*?);$", re.MULTILINE | re.DOTALL)
            metadata = ''
            # search for variable and get json in string format
            if r := re.search(pattern, doc.content.decode('utf-8')):
                metadata = r.group(1)
            else:
                raise Exception(f"No group with pattern : {re}")

            # if any non-printable character in string, delete
            metadata = re.sub(r'/\\x[0-9a-zA-z][0-9a-zA-z]/g', '', metadata)

            # Convert string to json
            metadata = json.loads(metadata)

            # keywords = metadata['keywords'] if 'keywords' in metadata.keys() else [
            # ]

            # checking for missing fields
            if 'displayDocTitle' not in metadata:
                metadata['displayDocTitle'] = "None"
            
            if 'abstract' not in metadata:
                metadata['abstract'] = "None"

            if 'displayDocTitle' not in metadata:
                metadata['displayDocTitle'] = "None"
            
            if 'keywords' not in metadata:
                metadata['keywords'] = "None"

            # check for missing fields
            article_data = (metadata['displayDocTitle'], metadata['abstract'],
                            metadata['displayPublicationDate'], metadata['keywords'])

            # Más llamadas, pero se asegura que no se quede abierto el fichero
            # en caso de problemas y se guarden X datos o todos
            if self.file_name is not None:
                file = open(self.file_name, 'a')
                file.write(f'{str(article_data)}\n')
                file.close()

        return article_data

    def get_all_articles(self) -> [(str, str, str, str)]:
        """
        Helper function. Ayuda a coger la información de varios artículos

        :return: Una lista compuesta por [(str, str, str, str)]
        """

        articles = []

        i = 0
        for article in self._article_links:
            if self.debug:
                print(f"[*] INFO: {i}")

            articles.append(self.get_info_article(
                f"{base_url}{article[1:]}toc"))

            i += 1

        return articles

    def extract(self, n, since=None):
        """Extrae la información de ilos últimos n artículos hasta since

        :param n: El número de artículos de los que extraer datos. Debe
            ser un entero mayor que 0.
        :param since: La fecha desde cuándo sacar la información. Debe
            ser un objeto date. si no se especifica, se presupone la
            fecha del día en el que se ejecuta la función
        :return: Una lista de tuplas donde cada tupla tendrá la
            siguiente forma: (str, str, str, str, List[str])
        """

        self.get_issues()

        if self.file_name is not None:
            date = datetime.now()
            self.file_name = f'articles_info_{n}_{date.year}-{date.month}-{date.day}-{date.hour}-{date.minute}-{date.second}'

            f = open(self.file_name, "w")
            f.close()
            print(f"[*] INFO: File named: {self.file_name} created")

        for issue in self._issues_values:
            # get articles from one issue
            self.get_n_articles(issue[0], issue[1], n)

            # more values than needed
            if n <= len(self._article_links):
                break

        articles = self.get_all_articles()[:n]

        return articles
