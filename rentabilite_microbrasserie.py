import streamlit as st
import pandas as pd
import altair as alt

# Initial page config
st.set_page_config(
     page_title='Analyse de la Rentabilité de la Micro-Brasserie',
     layout="wide",
)

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

# Disposition de la page
st.title('Analyse de la Rentabilité de la Micro-Brasserie')

# Utiliser des colonnes pour mettre les inputs à gauche et les graphiques à droite
col1, col2 = st.columns([1, 3])

with col1:
    with st.expander("Paramètres de Production", expanded=True):
        investissement_initial = st.number_input('Investissement initial (€)', min_value=0, value=10000, step=1000)
        cout_variable_par_unite = st.number_input('Coût variable par unité (€)', min_value=0.0, value=2.0, step=0.1)
        couts_fixes_mensuels = st.number_input('Coûts fixes mensuels (€)', min_value=0, value=1000, step=100)
        quantites_produites_input = st.text_input('Quantités produites (séparées par des virgules)', '100,200,300,400,500')
        quantites_produites = list(map(int, quantites_produites_input.split(',')))

    with st.expander("Paramètres Financiers", expanded=True):
        prix_vente_par_unite = st.number_input('Prix de vente par unité (€)', min_value=0.0, value=5.0, step=0.1)
        nb_mois = st.number_input('Nombre de mois', min_value=1, value=12, step=1)

    with st.expander("Paramètres de Taxe", expanded=True):
        taxe_biere_par_litre = st.number_input('Taxe sur la bière par litre d\'alcool pur (€)', min_value=0.0, value=7.5, step=0.1)
        volume_alcoolique = st.number_input('Volume alcoolique de la bière (%)', min_value=0.0, value=5.0, step=0.1)

try:
    df = get_rentabilite_data(investissement_initial, cout_variable_par_unite, prix_vente_par_unite, couts_fixes_mensuels, quantites_produites, nb_mois, taxe_biere_par_litre, volume_alcoolique)

    with col2:
        st.write("### Rentabilité en fonction de la quantité produite et du nombre de mois")

        # Créer un graphique pour chaque quantité produite
        for quantite in quantites_produites:
            data = df[df['Quantité Produite (unités/mois)'] == quantite]
            data_melted = data.melt(id_vars=['Mois'], value_vars=['Coût Total (€)', 'Recettes (€)', 'Bénéfice (€)', 'Taxe Alcool (€)'], var_name='Type', value_name='Valeur')
            chart = alt.Chart(data_melted).mark_line().encode(
                x=alt.X('Mois:Q', axis=alt.Axis(title='Mois')),
                y=alt.Y('Valeur:Q', axis=alt.Axis(title='Valeur (€)')),
                color='Type:N',
                tooltip=['Mois:Q', 'Type:N', 'Valeur:Q']
            ).properties(
                title=f'Évolution des Coûts Totaux, Recettes, Bénéfices et Taxes sur l\'Alcool au cours des mois pour {quantite} unités/mois'
            ).configure_legend(
                orient='bottom'
            ).configure_title(
                fontSize=14
            )

            st.altair_chart(chart, use_container_width=True)

except Exception as e:
    st.error(
        """
        **Une erreur est survenue.**
        Erreur : %s
    """
        % e
    )
