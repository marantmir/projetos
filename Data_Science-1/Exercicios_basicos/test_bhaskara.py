import bhaskara_poo
import pytest

class TestBhaskara:

    @pytest.fixture
    def b(self):
        return bhaskara_poo.bhaskara()

    @pytest.mark.parametrize("e1,e2,e3,valor_esperado",[
        (1,0,0,(1,0)),
        (1,-5,6,(2,3,2)),
        (10,10,10,0),
        (10,20,10,(1,-1))
        ])

    def testa_duas_raizes(self,b,e1,e2,e3,valor_esperado):
        assert b.calcula(e1,e2,e3) == valor_esperado
        
