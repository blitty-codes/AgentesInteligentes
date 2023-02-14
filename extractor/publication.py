class Publication:
    def __init__(self, url, n, since=None):
        self.url = url
        self.name = ""
        self.articles = self.extract(n, since)

        if self.articles != []:
            self.name = self.articles[0].name

    def extract(n, since=None) -> [Article]:
        pass

