import pandas as pd

class analise:
    
    def read_csv(arquivo):
        arquivo_csv =pd.read_csv(arquivo)
        return pd.DataFrame(arquivo_csv)
    
    
