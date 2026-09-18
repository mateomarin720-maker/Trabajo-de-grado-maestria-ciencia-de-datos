import pandas as pd
geih = pd.read_parquet('data/2_models/geih_estandarizado_2024.parquet')
print('GEIH estandarizado:', len(geih), 'hogares')
print(geih['mes'].value_counts().sort_index())
print()
sisben = pd.read_parquet('data/2_models/sisben_estandarizado_2024.parquet')
print('Sisben estandarizado:', len(sisben), 'hogares')
