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
    result = []
    # Aquí el cuerpo de la función
    return result


if __name__ == '__main__':
    for row in extract(n=20):
        print(row)
