# Data Raw — SIM (Sistema de Informações sobre Mortalidade)

This directory is intended to store the raw data files used in this project.
Due to file size limitations on GitHub, the original datasets are not included in this repository.

## Data Source

The data used in this project comes from the Brazilian Ministry of Health:
https://dadosabertos.saude.gov.br/dataset/sim

Dataset: Sistema de Informações sobre Mortalidade (SIM)

## How to Download

- Access the official dataset page: https://dadosabertos.saude.gov.br/dataset/sim
- Download the desired years (e.g., 2018–2022)
- Files are typically provided in compressed formats (ZIP) containing .dbc or .csv files.

## Expected Folder Structure

After downloading and extracting the files, organize them as follows:

data/
  raw/
    sim/
      2018/
      2019/
      2020/
      2021/
      2022/

Each folder should contain the original files exactly as provided (no modifications).

## Important Notes

- These are raw, unprocessed data files.
- No transformations, cleaning, or renaming should be applied at this stage.
- All processing steps are performed in the data/processed layer.

## Reproducibility

- To fully reproduce this project:
- Download the raw data from the official source
- Place the files in this directory following the structure above
- Run the ingestion and processing pipelines provided in the repository

## Disclaimer

This project uses publicly available data provided by the Brazilian government.
All data usage complies with open data policies.

## About the Project

This repository builds a scalable data pipeline to process mortality data from Brazil, enabling demographic, epidemiological, and public health analyses using modern data tools.
