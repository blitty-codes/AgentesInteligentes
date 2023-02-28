import re
import json
import requests
from datetime import datetime
from multiprocessing import Manager
from multiprocessing import Process

from globals import headers, base_url, issues_url

N_THREADS = 10


class Article:
    def __init__(self, debug=True, save_to_file=True):
        self._article_links = []
        self._issues_values = []
        self._date = datetime.now()
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

                for year in issue["years"]:
                    if self.debug:
                        print(f"\t\t[*] Year: {year['year']}")
                        print(
                            f"\t\t\t[-] Number of issues: {len(year['issues'])}")

                    # displayPublicationDate
                    if self._date.year >= int(year["year"]):
                        for iss in year['issues']:
                            self._issues_values.append(
                                (iss['publicationNumber'], iss['issueNumber']))

    def get_url_articles(self, pub_number, issue_number):
        """
        Extrae el enlace del artículo pasado por parámetro. Se decartan los artículos "Table of Content" o "Editorial tutorials".

        :param pub_number: Número de publicación
        :param issue_number: Número de la issue (artículo)
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
                if "Quarter" not in article["articleTitle"] and "Editorial:" not in article["articleTitle"] and "Table of" not in article["articleTitle"]:
                    if "htmlLink" in article.keys():
                        self._article_links.append(article["htmlLink"])
                    else:
                        self._article_links.append(article["documentLink"])

        if self.debug:
            print(f"[*] INFO: Number of documents: {len(self._article_links)}")

    def get_info_articles(self, ini, fini, articles_info: Manager, n):
        """
        Extrae "titulo del artículo", "abstract", "fecha de publicación" y "keywords" de los enlaces pasados, desde 'ini' hasta 'fini', guardándolo en el Manager `articles_info` pasado por parámetro.

        This is a thread based method.

        :param ini: Initial index to start.
        :param fini: Final index to stop.
        :param articles_info: List from a Manager object to save tuples.
        :raise Exception: No se encuentra la url o no puede ser alcanzada.
        """

        ini = int(ini)
        fini = int(fini)

        # Get information from slice [ini, fini]
        for i in range(ini, fini):
            article_url = f"{base_url}{self._article_links[i][1:]}toc"
            if self.debug:
                print(f"[+] GET {article_url} - article position: {i}")

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
                metadata = re.sub(
                    r'/\\x[0-9a-zA-z][0-9a-zA-z]/g', '', metadata)

                # Convert string to json
                metadata = json.loads(metadata)

                # checking for missing fields
                if 'displayDocTitle' not in metadata:
                    metadata['displayDocTitle'] = "None"

                if 'abstract' not in metadata:
                    metadata['abstract'] = "None"

                if 'displayDocTitle' not in metadata:
                    metadata['displayDocTitle'] = "None"

                if 'keywords' not in metadata:
                    metadata['keywords'] = "None"

                if datetime.strptime(metadata['displayPublicationDate'], '%d %B %Y') <= self._date:
                    article_data = (metadata['displayDocTitle'], metadata['abstract'],
                                    metadata['displayPublicationDate'], metadata['keywords'])
                    articles_info.append(article_data)

                # Más llamadas, pero se asegura que no se quede abierto el fichero
                # en caso de problemas y se guarden X datos o todos
                if self.file_name is not None and article_data:
                    file = open(self.file_name, 'a')
                    file.write(f'{str(article_data)}\n')
                    file.close()

    def get_all_articles(self, n) -> [(str, str, str, str)]:
        """
        Helper function. Ayuda a coger la información de varios artículos

        :return: Una lista compuesta por [(str, str, str, str)]
        """

        # lista de acceso común para todos los procesos involucrados
        manager = Manager()
        articles_info = manager.list()

        # gestión de slices para cada proceso (tamaño y función a ejecutar)
        n = len(self._article_links)
        size = n/N_THREADS

        # creación de procesos
        processes = []

        for i in range(0, N_THREADS):
            ini = i*size
            fini = ini + size

            proc = Process(target=self.get_info_articles,
                           args=(ini, fini, articles_info, n))
            processes.append(proc)

        for p in processes:
            p.start()

        for p in processes:
            p.join()

        # https://stackoverflow.com/questions/10415028/how-to-get-the-return-value-of-a-function-passed-to-multiprocessing-process

        return articles_info

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

        if since is not None:
            self._date = since
            self._date.replace(year = self._date.year + 1)

        self.get_issues()

        if self.file_name is not None:
            date = datetime.now()
            self.file_name = f'articles_info_{n}_{date.year}-{date.month}-{date.day}-{date.hour}-{date.minute}-{date.second}'

            f = open(self.file_name, "w")
            f.close()
            print(f"[*] INFO: File named: {self.file_name} created")

        for issue in self._issues_values:
            # get articles from one issue
            self.get_url_articles(issue[0], issue[1])

            # more values than needed
            if n <= len(self._article_links):
                break

        articles = self.get_all_articles(n)

        return sorted(articles, key=lambda x: datetime.strptime(x[2], '%d %B %Y'))[:n]

