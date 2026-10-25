import numpy as np, pandas as pd
from pathlib import Path
OUT=Path(__file__).resolve().parent
SEED=20251025; N=500_000; TARGET=30_640_833_000
rng=np.random.default_rng(SEED)
segments=np.array(['Brasil','America do Norte','America do Sul'])
seg=rng.choice(segments,N,p=[.43,.49,.08])
classes=np.array(['Terrenos','Edificios','Maquinas e equipamentos','Moveis e utensilios','Veiculos','Obras em andamento','Direito de uso'])
cls=rng.choice(classes,N,p=[.025,.12,.50,.06,.055,.20,.04])
country=np.where(seg=='Brasil','Brasil',np.where(seg=='America do Norte',rng.choice(['Estados Unidos','Canada','Mexico'],N,p=[.82,.10,.08]),rng.choice(['Argentina','Uruguai','Peru'],N,p=[.55,.25,.20])))
units=np.char.add(np.char.add('UG_',np.char.replace(seg.astype(str),' ', '_')),np.char.zfill((rng.integers(1,31,N)).astype(str),2))
acq=pd.to_datetime('1990-01-01')+pd.to_timedelta(rng.integers(0,13149,N),unit='D')
construction=cls=='Obras em andamento'
in_service=np.where(construction,pd.NaT,np.minimum(acq+pd.to_timedelta(rng.integers(0,731,N),unit='D'),np.datetime64('2025-12-31')))
life_map={'Terrenos':0,'Edificios':35,'Maquinas e equipamentos':18,'Moveis e utensilios':10,'Veiculos':8,'Obras em andamento':0,'Direito de uso':7}
life=np.array([life_map[x] for x in cls]); life=np.where(life>0,np.maximum(1,life+rng.integers(-2,3,N)),0)
base=rng.lognormal(mean=10.3,sigma=1.15,size=N)
mult=np.select([cls=='Terrenos',cls=='Edificios',cls=='Maquinas e equipamentos',cls=='Obras em andamento'],[2.2,2.7,3.0,3.8],default=1.0)
cost=np.round(base*mult,2)
age=pd.Series((pd.Timestamp('2025-12-31')-pd.to_datetime(in_service)).total_seconds()/86400/365.25).fillna(0).clip(lower=0).to_numpy()
rate=np.divide(1.0,life,out=np.zeros_like(life,dtype=float),where=life>0)
dep=np.minimum(cost,np.round(cost*rate*age,2))
impair=np.where(rng.random(N)<.018,np.round((cost-dep)*rng.uniform(.05,.65,N),2),0)
nbv=np.maximum(0,cost-dep-impair)
# scale exactly to published balance
nbv=np.round(nbv*(TARGET/nbv.sum()),2)
diff=round(TARGET-nbv.sum(),2)
# distribute rounding adjustment without creating negative balances
adj_idx=int(np.argmax(nbv)); nbv[adj_idx]+=diff
# recompute cost as NBV + dep + impairment to preserve equation
cost=np.round(nbv+dep+impair,2)
exceptions=np.full(N,'',dtype=object)
idx_dup=rng.choice(N,120,replace=False); exceptions[idx_dup]='ID_DUPLICADO'
eligible_life=np.where((~construction)&(cls!='Terrenos'))[0]
idx_neg=rng.choice(np.setdiff1d(eligible_life,idx_dup),80,replace=False); exceptions[idx_neg]='VIDA_UTIL_INCONSISTENTE'; life[idx_neg]=0
idx_future=rng.choice(np.where(~construction)[0],60,replace=False); exceptions[idx_future]='DATA_SERVICO_FUTURA'; in_service[idx_future]=np.datetime64('2026-06-30')
idx_dep=rng.choice(np.where(~construction)[0],90,replace=False); exceptions[idx_dep]='DEPRECIACAO_SUPERIOR_CUSTO'; dep[idx_dep]=cost[idx_dep]+rng.uniform(1,1000,len(idx_dep))
asset_id=np.array([f'IMOB-{i:07d}' for i in range(1,N+1)],dtype=object)
asset_id[idx_dup[:60]]=asset_id[idx_dup[60:120]]
df=pd.DataFrame({'id_bem':asset_id,'segmento':seg,'pais':country,'unidade_sintetica':units,'classe_imobilizado':cls,'data_aquisicao':acq,'data_entrada_operacao':pd.to_datetime(in_service),'custo_historico_rs':cost,'vida_util_anos':life,'taxa_depreciacao_anual':rate,'depreciacao_acumulada_rs':dep,'impairment_acumulado_rs':impair,'valor_contabil_liquido_rs':nbv,'status_operacional':np.where(construction,'Em construcao',rng.choice(['Ativo','Ocioso','Em manutencao'],N,p=[.96,.01,.03])),'centro_custo':np.char.add('CC',np.char.zfill(rng.integers(1,2501,N).astype(str),4)),'projeto_capex':np.where(construction,np.char.add('CAPEX',np.char.zfill(rng.integers(1,801,N).astype(str),4)),''),'indicador_excecao':exceptions!='','tipo_excecao':exceptions,'dados_sinteticos':True})
df.to_csv(OUT/'base_sintetica_imobilizado_gerdau_2025.csv.gz',index=False,compression='gzip',date_format='%Y-%m-%d')
truth=df.loc[df.indicador_excecao,['id_bem','tipo_excecao']].copy(); truth.to_csv(OUT/'registro_excecoes_inseridas.csv',index=False)
# tests
tests=pd.DataFrame({'teste':['Duplicidade de ID','Vida util zero em bem depreciavel','Entrada em operacao apos 31/12/2025','Depreciacao superior ao custo'], 'inseridas':[120,80,60,90], 'identificadas':[df.id_bem.duplicated(False).sum(),((df.vida_util_anos==0)&(~df.classe_imobilizado.isin(['Terrenos','Obras em andamento']))).sum(),(df.data_entrada_operacao>pd.Timestamp('2025-12-31')).sum(),(df.depreciacao_acumulada_rs>df.custo_historico_rs).sum()]})
tests.to_csv(OUT/'resultados_testes_base.csv',index=False)
# monetary unit sample PPS approximation + random
p=np.maximum(nbv,0); p=p/p.sum(); sample_idx=rng.choice(N,200,replace=False,p=p)
sample=df.iloc[sample_idx].copy(); sample['metodo_amostra']='PPS sem reposicao'; sample.to_csv(OUT/'amostra_pt530.csv',index=False)
print({'linhas':len(df),'saldo':float(df.valor_contabil_liquido_rs.sum()),'excecoes_linhas':int(df.indicador_excecao.sum()),'testes':tests.to_dict('records'),'amostra':len(sample)})
