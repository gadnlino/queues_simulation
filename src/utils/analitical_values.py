def get_lambda(rho):
    return rho/2

def E_U(rho, mu):
    return rho * E_X(rho, mu) * (1/(1-rho))

def E_T(rho, mu):
    lbd = get_lambda(rho)

    rho_1 = lbd / mu

    return (E_U(rho, mu) + E_X(rho, mu) + E_X(rho, mu))/(1-rho_1)

def E_X(rho, mu):
    return 1/mu

def E_W1(rho, mu):
    lbd = get_lambda(rho)

    rho_1 = lbd / mu
    return (rho_1/(1-rho_1))*(1/mu)

def Var_W1(rho, mu):
    lbd = get_lambda(rho)

    rho_1 = lbd / mu

    return E_W1(rho, mu) ** 2 + (lbd/(3 - 3*rho_1))*(6/(mu**3))

def E_NQ1(rho, mu):
    lbd = get_lambda(rho)

    return lbd * E_W1(rho, mu)

def E_T1(rho, mu):
    return E_W1(rho, mu) + E_X(rho, mu)

def E_N1(rho, mu):
    lbd = get_lambda(rho)

    return lbd * E_T1(rho, mu)

def E_T2(rho, mu):
    return E_T(rho, mu) - E_T1(rho, mu)

def E_W2(rho, mu):
    return E_T2(rho, mu) - E_X(rho, mu)

def E_N2(rho, mu):
    lbd = get_lambda(rho)

    return lbd * E_T2(rho, mu)

def E_NQ2(rho, mu):
    lbd = get_lambda(rho)

    return lbd * E_W2(rho, mu)

if(__name__ == '__main__'):
    mu = 1

    rho_values = [.2, .4, .6, .8, .9]

    print(f'rho, mu , E_W1 , Var_W1 , E_NQ1 , E_T1 , E_N1 , E_W2 , E_NQ2 , E_T2 , E_N2')

    for rho in rho_values:
        

        e_w1 = E_W1(rho, mu)
        var_w1 = Var_W1(rho, mu)
        e_nq1 = E_NQ1(rho, mu)
        e_t1 = E_T1(rho, mu)
        e_n1 = E_N1(rho, mu)
        
        e_w2 = E_W2(rho, mu)
        e_nq2 = E_NQ2(rho, mu)
        e_t2 = E_T2(rho, mu)
        e_n2 = E_N2(rho, mu)

        print(f'{rho}, {mu}, {e_w1}, {var_w1},  {e_nq1}, {e_t1}, {e_n1},  {e_w2},  {e_nq2}, {e_t2}, {e_n2}')