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

import argparse
from article import Article
from datetime import datetime


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Agente extractor de datos de artículos para la página: https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=9739')
    parser.add_argument('-n', '--num_files', type=int, required=True, help='Numero de articulos a extraer')
    parser.add_argument('--since', type=lambda s: datetime.strptime(s, '%Y-%m-%d'), help='Fecha inicial para la extracción con formato YYYY-MM-DD')
    parser.add_argument('-d', '--debug', action='store_true', help='Modo debug')
    parser.add_argument('--save', action='store_true', help='Guardar extracción en fichero')

    args = parser.parse_args()

    art = Article(debug=args.debug, save_to_file=args.save)
    articles = art.extract(n=args.num_files, since=args.since)

    print(len(articles))
