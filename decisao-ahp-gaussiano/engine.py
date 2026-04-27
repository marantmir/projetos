import pandas as pd
import numpy as np

class AHPGaussianoEngine:
    """
    Motor de cálculo para o método AHP Gaussiano.
    Transforma dados brutos em decisões fundamentadas.
    """
    
    @staticmethod
    def processar_custo(df, tipos_criterios):
        """Ajusta critérios de 'MIN' (custo) para que valores menores pontuem melhor."""
        df_ajustado = df.copy()
        for col in df.columns:
            if tipos_criterios.get(col) == 'MIN':
                # Inversão linear para manter a proporcionalidade sem erro de divisão por zero
                max_val = df[col].max()
                min_val = df[col].min()
                df_ajustado[col] = max_val - df[col] + min_val
        return df_ajustado

    @staticmethod
    def calcular_pesos_gaussianos(df_norm):
        """Calcula pesos automáticos baseados na variabilidade (entropia) dos dados."""
        media = df_norm.mean()
        desvio = df_norm.std(ddof=0) # Desvio padrão populacional
        
        # O Fator Gaussiano é o coeficiente de variação
        # Se media for 0, o fator é 0 para evitar erro matemático
        fator_gaussiano = np.where(media != 0, desvio / media, 0)
        
        # Normalização dos pesos (soma = 1)
        soma_fatores = np.sum(fator_gaussiano)
        if soma_fatores == 0:
            return pd.Series(1/len(df_norm.columns), index=df_norm.columns)
            
        pesos = fator_gaussiano / soma_fatores
        return pd.Series(pesos, index=df_norm.columns)

    def resolver(self, df_entrada, tipos_criterios):
        """Executa o pipeline completo do AHP Gaussiano."""
        # 1. Tratamento de critérios de custo
        matriz_ajustada = self.processar_custo(df_entrada, tipos_criterios)
        
        # 2. Normalização da Matriz (Soma das colunas = 1)
        matriz_norm = matriz_ajustada / matriz_ajustada.sum()
        
        # 3. Cálculo de Pesos Automáticos
        pesos = self.calcular_pesos_gaussianos(matriz_norm)
        
        # 4. Ponderação e Ranking
        matriz_ponderada = matriz_norm.multiply(pesos, axis=1)
        ranking = matriz_ponderada.sum(axis=1).sort_values(ascending=False)
        
        return ranking, pesos