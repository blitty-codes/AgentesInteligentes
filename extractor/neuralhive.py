"""Agente extractor de datos de artículos

Este agente se encarga de la extracción de datos de la revista
IEEE Communications Surveys & Tutorials.

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
import logging
import sys
from article import Article
from datetime import datetime

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Agente extractor de datos de artículos para la página: https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=9739')
    parser.add_argument('-n', '--num_files', type=int, required=True, help='Numero de articulos a extraer')
    parser.add_argument('--since', type=str, default=datetime.now().strftime('%Y-%m-%d'), help='Fecha inicial para la extracción con formato YYYY-MM-DD')
    parser.add_argument('--n_jobs', type=int, default=-1, help='Numero de threads')
    parser.add_argument('--save', action='store_true', help='Guardar extracción en fichero')
    parser.add_argument('--loglevel', default='info', choices=['debug', 'info', 'warning'], help='Nivel de Log')

    args = parser.parse_args()

    file_handler = logging.FileHandler(filename=f'app-n_{args.num_files}_since_{args.since}.log', mode='w', encoding='utf-8')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(level=args.loglevel.upper(), format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S', handlers=handlers)
    logging.info('Agente extractor de articulos provenientes de IEEE Communications Surveys & Tutorials')

    art = Article(save_to_file=args.save, n_jobs=args.n_jobs)
    articles = art.extract(n=args.num_files, since=datetime.strptime(args.since, '%Y-%m-%d'))

    logging.info(f'{len(articles)} articles successfully extracted')
