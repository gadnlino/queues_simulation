#https://www.geeksforgeeks.org/pseudo-random-number-generator-prng/
from datetime import datetime
from math import log

class PRNG:
    def __init__(self, a, c, m, seed) -> None:
        self.__initial_value = None

        if(seed != None and self.__initial_value == None):
            self.__initial_value = seed
        elif(self.__initial_value == None):
            #usando o timestamp do momento da instanciação da classe como o seed inicial
            self.__initial_value = int(datetime.utcnow().timestamp())

        if(a != None):
            self.__a = a
        else:
            self.__a = 7

        if(c != None):
            self.__c = c
        else:
            self.__c = 7

        if(m != None):
            self.__m = m
        else:
            self.__m = (2**63)-1
        

    #Utilizando o seguinte gerador de números pseudo-aleatórios
    #https://pt.wikipedia.org/wiki/Geradores_congruentes_lineares
    def random(self):
        next_value = (self.__a*self.__initial_value + self.__c) % self.__m
        self.__initial_value = next_value
        return next_value

    #apostila, página 137
    def uniform(self):
        return self.random()/self.__m

    #https://en.wikipedia.org/wiki/Inverse_transform_sampling
    def exponential(self, rate):
        u = self.uniform()
        return log(1-u)/(-rate)

def stop_when_repeated(generator: PRNG):
    generated = []
    r = prng.random()
    while r not in generated:
        print(r)
        generated.append(r)
        r = prng.random()   

if __name__ == "__main__":
    prng = PRNG(None, None, None, None)
    
    #capacidade do gerador de números aleatórios
    #stop_when_repeated(prng)

    # for i in range(0, 200):
    #     #exemplo do livro do Knuth
    #     #https://books.google.com.br/books?id=Zu-HAwAAQBAJ&pg=PT4&redir_esc=y#v=onepage&q&f=false
    #     print(prng.random(7,7,(2**36)-1))
    
    # for i in range(0, 200):
    #     #exemplo do livro do Knuth
    #     #https://books.google.com.br/books?id=Zu-HAwAAQBAJ&pg=PT4&redir_esc=y#v=onepage&q&f=false
    #     print(prng.uniform())

    for i in range(0, 200):
        #exemplo do livro do Knuth
        #https://books.google.com.br/books?id=Zu-HAwAAQBAJ&pg=PT4&redir_esc=y#v=onepage&q&f=false
        print(prng.exponential(0.5))
