tokentxt = "botoken.txt"
URL = "https://api.telegram.org/bot{}/"

class Token():

    def __init__(self):
        self.infileTokentxt = None
        self.tokenKey = None

    def readBotoken(self):
        self.infileTokentxt = open(tokentxt, 'r')
        self.tokenKey = self.infileTokentxt.readline()
        return URL.format(self.tokenKey.rstrip())

    def getBotoken(self):
        return self.readBotoken()
