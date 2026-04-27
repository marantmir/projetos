import ordenador
import pytest
import contatempos

class TestaOrdenador:

    # Para usar @pytest.fixture deve-se importar o modulo pytest
    @pytest.fixture
    def o(self):
        return ordenador.Ordenador()


    @pytest.fixture
    def l_quase(self):
        c = contatempos.Contatempos()
        return c.lista_quase_ordenada(100)

    @pytest.fixture
    def l_aleatoria(self):
        c = contatempos.Contatempos()
        return c.lista_aleatoria(100)
    
    def esta_ordenada(self,l):
        for i in range(len(l)-1):
            if l[i] > l[i+1]:
                return False
        return True

    def test_bolha_curts_aleat(self,o,l_aleatoria):
        o.bolha(l_aleatoria)
        assert self.esta_ordenada(l_aleatoria)

    def test_selecao_direta(self,o,l_aleatoria):
        o.selecao_direta(l_aleatoria)
        assert self.esta_ordenada(l_aleatoria)

