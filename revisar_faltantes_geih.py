import pandas as pd

modulos = ['otros_ingresos', 'migracion', 'no_ocupados']

for mod in modulos:
    print(f'=== {mod} ===')
    df = pd.read_parquet(f'data/1_processed/geih/2024/01/{mod}.parquet')
    df = df.replace('', pd.NA)
    faltantes = df.isnull().mean().mul(100).round(2).sort_values(ascending=False)
    print(faltantes[faltantes > 0].head(15))
    print()
