import streamlit as st
import pandas as pd
import requests
from requests.exceptions import HTTPError
import base64

def enrich_data(df):
  # Call API for each row in the data frame and enrich the data

  try:
    enriched_data = []
    for index, row in df.iterrows():
        enriched_row = enrich_row(row) 
        enriched_data.append(enriched_row)
    # Return the enriched data as a data frame
    return pd.DataFrame(enriched_data)

  except Exception as err:
    print(f"Une erreur s'est produite: {err}")

@st.cache
def enrich_row(row):
    try:    
        # Make API call and get response
        response = requests.get(f"https://api.recherche-entreprises.fabrique.social.gouv.fr/api/v1/search?query={row['Nom']}&limit=1&open=true&employer=false&convention=false&ranked=true&matchingLimit=100")
        response.raise_for_status()
        data = response.json()
        # print(data)
        # Enrich the data
        enriched_row = {
        'Nom': data['entreprises'][0]['simpleLabel'],
        'siren': data['entreprises'][0]['siren'],
        'siret': data['entreprises'][0]['firstMatchingEtablissement']['siret']
        }
        return enriched_row

    except HTTPError as http_err:
        print(f"Une erreur HTTP s'est produite: {http_err}")
    except Exception as err:
        print(f"Une erreur s'est produite: {err}")


def main():
  st.title('CSV Enricher')

  # Allow the user to upload a CSV file
  uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
  if uploaded_file is not None:
    # Read the CSV file into a data frame
    df = pd.read_csv(uploaded_file)
    # Enrich the data
    enriched_df = enrich_data(df)
    # Display the enriched data
    st.dataframe(enriched_df)
    # Allow the user to download the enriched data
    st.markdown('Click the button below to download the enriched data as a CSV file.')
    if st.button('Download CSV'):
      csv = enriched_df.to_csv(index=False)
      b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
      href = f'<a href="data:file/csv;base64,{b64}" download="enriched_data.csv">Download enriched data</a>'
      st.markdown(href, unsafe_allow_html=True)

if __name__ == '__main__':
  main()
