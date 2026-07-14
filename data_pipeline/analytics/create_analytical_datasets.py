from pathlib import Path
import pandas as pd

# ==========================================================
# CAMINHOS
# ==========================================================

BASE_DIR = Path("/home/tatiane/repositorios/brazil-health-data-project/data_pipeline/data/").resolve().parents[0]

print("BASE_DIR =", BASE_DIR)

SIM_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sim"
    / "standardization"
    / "sim_2018_2022.parquet"
)

POP_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "ibge_populacao"
    / "ibge_populacao2.parquet"
)

PNAD_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "ibge_pnad_continua"
    / "ibge_pnad_continua.parquet"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "analytical"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ==========================================================
# LEITURA
# ==========================================================

print("Lendo SIM...")

sim = pd.read_parquet(
    SIM_PATH,
    columns=[
        "ano",
        "cod_mun_res",
        "sexo",
        "idade",
        "causa_bas"
    ]
)

print("Lendo população...")

pop = pd.read_parquet(POP_PATH)

print("Lendo PNAD...")

pnad = pd.read_parquet(PNAD_PATH)

# ==========================================================
# CRIAÇÃO COD_UF E PADRONIZAÇÃO
# ==========================================================

print("Criando cod_uf no SIM...")

sim["cod_uf"] = (
    sim["cod_mun_res"]
    .astype(str)
    .str[:2]
    .astype(int)
)

sim["ano"] = (
    sim["ano"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
    .astype("Int64")
)

# ==========================================================
# POPULAÇÃO POR UF E ANO
# ==========================================================

pop["ano"] = (
    pop["ano"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
    .astype("Int64")
)

print("Agregando população por UF e ano...")

pop_uf = (
    pop
    .groupby(
        ["cod_uf", "ano"],
        as_index=False
    )
    .agg(
        populacao=("populacao", "sum")
    )
)

# ==========================================================
# PADRONIZA PNAD
# ==========================================================

pnad["ano"] = (
    pnad["ano"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
    .astype("Int64")
)

pnad = pnad[
    [
        "cod_uf",
        "ano",
        "renda_media"
    ]
].copy()

# ==========================================================
# FUNÇÃO GENÉRICA
# ==========================================================

def criar_dataset_analitico(
    df_sim,
    nome_obitos,
    nome_taxa,
    nome_arquivo
):

    print(f"\nGerando {nome_arquivo}...")

    obitos = (
        df_sim
        .groupby(
            ["cod_uf", "ano"],
            as_index=False
        )
        .size()
        .rename(
            columns={
                "size": nome_obitos
            }
        )
    )

    df_final = (
        obitos
        .merge(
            pop_uf,
            on=["cod_uf", "ano"],
            how="left"
        )
        .merge(
            pnad,
            on=["cod_uf", "ano"],
            how="left"
        )
    )

    df_final[nome_taxa] = (
        df_final[nome_obitos]
        / df_final["populacao"]
    ) * 100000

    caminho_saida = OUTPUT_DIR / nome_arquivo

    df_final.to_parquet(
        caminho_saida,
        index=False
    )

    print(
        f"Salvo: {caminho_saida}"
    )

    print(
        f"Linhas: {len(df_final):,}"
    )

    return df_final

# ==========================================================
# DATASET 1 - MORTALIDADE GERAL
# ==========================================================

criar_dataset_analitico(
    df_sim=sim,
    nome_obitos="obitos",
    nome_taxa="taxa_mortalidade",
    nome_arquivo="mortalidade_geral_uf_ano.parquet"
)

# ==========================================================
# DATASET 2 - MORTALIDADE MASCULINA
# ==========================================================

sim_masc = sim[
    sim["sexo"]
    .astype(str)
    .str.upper()
    .isin(
        [
            "M",
            "MASCULINO",
            "1"
        ]
    )
].copy()

criar_dataset_analitico(
    df_sim=sim_masc,
    nome_obitos="obitos_masc",
    nome_taxa="taxa_mortalidade_masc",
    nome_arquivo="mortalidade_masculina_uf_ano.parquet"
)

# ==========================================================
# DATASET 3 - MORTALIDADE FEMININA
# ==========================================================

sim_fem = sim[
    sim["sexo"]
    .astype(str)
    .str.upper()
    .isin(
        [
            "F",
            "FEMININO",
            "2"
        ]
    )
].copy()

criar_dataset_analitico(
    df_sim=sim_fem,
    nome_obitos="obitos_fem",
    nome_taxa="taxa_mortalidade_fem",
    nome_arquivo="mortalidade_feminina_uf_ano.parquet"
)

# ==========================================================
# DATASET 4 - MORTALIDADE PREMATURA (<70)
# ==========================================================

sim_prematura = sim[
    sim["idade"] < 70
].copy()

criar_dataset_analitico(
    df_sim=sim_prematura,
    nome_obitos="obitos_prematuros",
    nome_taxa="taxa_mortalidade_prematura",
    nome_arquivo="mortalidade_prematura_uf_ano.parquet"
)

# ==========================================================
# DATASET 5 - DCNT
# ==========================================================

sim["causa_bas"] = (
    sim["causa_bas"]
    .astype(str)
    .str.upper()
)

filtro_dcnt = (
    sim["causa_bas"].str.startswith("I", na=False)
    |
    sim["causa_bas"].str.startswith("C", na=False)
    |
    sim["causa_bas"].str.startswith("D", na=False)
    |
    sim["causa_bas"].str.startswith("J", na=False)
    |
    sim["causa_bas"].str.startswith(
        (
            "E10",
            "E11",
            "E12",
            "E13",
            "E14"
        ),
        na=False
    )
)

sim_dcnt = sim[
    filtro_dcnt
].copy()

criar_dataset_analitico(
    df_sim=sim_dcnt,
    nome_obitos="obitos_dcnt",
    nome_taxa="taxa_mortalidade_dcnt",
    nome_arquivo="mortalidade_dcnt_uf_ano.parquet"
)

print("\nProcessamento concluído com sucesso!")
