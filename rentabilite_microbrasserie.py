import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def get_rentabilite_data(investissement_initial, cout_variable_par_unite, prix_vente_par_unite, couts_fixes_mensuels, quantites_produites, nb_mois, taxe_biere_par_litre, volume_alcoolique):
    data = []
    for quantite in quantites_produites:
        for mois in range(1, nb_mois + 1):
            volume_biere_total = quantite * mois  # Volume total produit en litres
            alcool_total = volume_biere_total * volume_alcoolique / 100  # Volume d'alcool pur en litres
            cout_taxe_alcool = alcool_total * taxe_biere_par_litre  # Coût total de la taxe sur l'alcool

            cout_total_mensuel = (quantite * cout_variable_par_unite) + couts_fixes_mensuels
            cout_total = investissement_initial + (cout_total_mensuel * mois) + cout_taxe_alcool
            recettes = quantite * prix_vente_par_unite * mois
            benefice = recettes - cout_total
            data.append([quantite, mois, cout_total, recettes, benefice, cout_taxe_alcool])

    df = pd.DataFrame(data, columns=['Quantité Produite (unités/mois)', 'Mois', 'Coût Total (€)', 'Recettes (€)', 'Bénéfice (€)', 'Taxe Alcool (€)'])
    return df

# Inputs pour les variables
st.title('Analyse de la Rentabilité de la Micro-Brasserie')

investissement_initial = st.number_input('Investissement initial (€)', min_value=0, value=10000, step=1000)
cout_variable_par_unite = st.number_input('Coût variable par unité (€)', min_value=0.0, value=2.0, step=0.1)
prix_vente_par_unite = st.number_input('Prix de vente par unité (€)', min_value=0.0, value=5.0, step=0.1)
couts_fixes_mensuels = st.number_input('Coûts fixes mensuels (€)', min_value=0, value=1000, step=100)
quantites_produites_input = st.text_input('Quantités produites (séparées par des virgules)', '100,200,300,400,500')
nb_mois = st.number_input('Nombre de mois', min_value=1, value=12, step=1)
taxe_biere_par_litre = st.number_input('Taxe sur la bière par litre d\'alcool pur (€)', min_value=0.0, value=7.5, step=0.1)
volume_alcoolique = st.number_input('Volume alcoolique de la bière (%)', min_value=0.0, value=5.0, step=0.1)

# Convertir les quantités en liste d'entiers
quantites_produites = list(map(int, quantites_produites_input.split(',')))

try:
    df = get_rentabilite_data(investissement_initial, cout_variable_par_unite, prix_vente_par_unite, couts_fixes_mensuels, quantites_produites, nb_mois, taxe_biere_par_litre, volume_alcoolique)

    st.write("### Rentabilité en fonction de la quantité produite et du nombre de mois", df)

    # Graphique des coûts totaux
    couts_chart = alt.Chart(df).mark_line().encode(
        x='Mois:Q',
        y='Coût Total (€):Q',
        color='Quantité Produite (unités/mois):N'
    ).properties(
        title='Coût Total au cours des mois',
        width=700,
        height=400
    )
    st.altair_chart(couts_chart, use_container_width=True)

    # Graphique des recettes
    recettes_chart = alt.Chart(df).mark_line().encode(
        x='Mois:Q',
        y='Recettes (€):Q',
        color='Quantité Produite (unités/mois):N'
    ).properties(
        title='Recettes au cours des mois',
        width=700,
        height=400
    )
    st.altair_chart(recettes_chart, use_container_width=True)

    # Graphique des bénéfices
    benefices_chart = alt.Chart(df).mark_line().encode(
        x='Mois:Q',
        y='Bénéfice (€):Q',
        color='Quantité Produite (unités/mois):N'
    ).properties(
        title='Bénéfice au cours des mois',
        width=700,
        height=400
    )
    st.altair_chart(benefices_chart, use_container_width=True)

    # Graphique des taxes sur l'alcool
    taxes_chart = alt.Chart(df).mark_line().encode(
        x='Mois:Q',
        y='Taxe Alcool (€):Q',
        color='Quantité Produite (unités/mois):N'
    ).properties(
        title='Taxe Alcool au cours des mois',
        width=700,
        height=400
    )
    st.altair_chart(taxes_chart, use_container_width=True)

except Exception as e:
    st.error(
        """
        **Une erreur est survenue.**
        Erreur : %s
    """
        % e
    )
