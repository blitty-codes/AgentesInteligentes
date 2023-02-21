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

from article import Article


if __name__ == '__main__':
    # for row in extract(n=20):
    art = Article(debug=True, save_to_file=False)
    articles = art.extract(2000)

    print(len(articles))
