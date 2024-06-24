import streamlit as st
import pandas as pd
import altair as alt

# Initial page config
st.set_page_config(
    page_title='Analyse de la Rentabilité de la Micro-Brasserie',
    layout="wide",
)

@st.cache_data
def get_rentabilite_data(investissement_initial, cout_variable_par_unite, prix_vente_par_unite, couts_fixes_mensuels, quantites_produites, nb_mois, volume_alcoolique, cout_main_oeuvre, cout_marketing, cout_distribution, smic_mensuel):
    data = []
    for quantite in quantites_produites:
        production_annuelle = quantite * 12  # Calcul automatique de la production annuelle
        cumul_benefice = 0
        for mois in range(1, nb_mois + 1):
            volume_biere_total = quantite * mois
            alcool_total = volume_biere_total * volume_alcoolique / 100

            # Calcul du droit spécifique sur les bières
            if volume_alcoolique <= 2.8:
                taxe_biere_par_litre = 3.82
            else:
                if production_annuelle <= 200000:
                    taxe_biere_par_litre = 3.70
                else:
                    taxe_biere_par_litre = 7.49

            cout_taxe_alcool = alcool_total * taxe_biere_par_litre

            # Calcul de la cotisation sécurité sociale sur les bières
            if volume_alcoolique > 18:
                if production_annuelle <= 200000:
                    cout_cotisation_ss = alcool_total * 1.50
                else:
                    cout_cotisation_ss = alcool_total * 3.00
            else:
                cout_cotisation_ss = 0

            cout_total_mensuel = (quantite * cout_variable_par_unite) + couts_fixes_mensuels + cout_main_oeuvre + cout_marketing + cout_distribution
            cout_total = investissement_initial + (cout_total_mensuel * mois) + cout_taxe_alcool + cout_cotisation_ss
            recettes = quantite * prix_vente_par_unite * mois
            benefice = recettes - cout_total
            cumul_benefice += benefice
            rentabilite = benefice > 0
            remboursement_investissement = cumul_benefice >= investissement_initial
            salaire_target = benefice >= smic_mensuel
            data.append([quantite, mois, cout_total, recettes, benefice, cout_taxe_alcool, cout_cotisation_ss, cumul_benefice, rentabilite, remboursement_investissement, salaire_target, production_annuelle])

    df = pd.DataFrame(data, columns=['Quantité Produite (unités/mois)', 'Mois', 'Coût Total (€)', 'Recettes (€)', 'Bénéfice (€)', 'Taxe Alcool (€)', 'Cotisation SS (€)', 'Cumul Bénéfice (€)', 'Rentabilité', 'Remboursement Investissement', 'Salaire Visé', 'Production Annuelle (hl)'])
    return df

st.title('Analyse de la Rentabilité de la Micro-Brasserie')

st.sidebar.title("Paramètres")
with st.sidebar.expander("Paramètres de Production", expanded=False):
    investissement_initial = st.number_input('Investissement initial (€)', min_value=0, value=10000, step=1000)
    cout_variable_par_unite = st.number_input('Coût variable par unité (€)', min_value=0.0, value=2.0, step=0.1)
    couts_fixes_mensuels = st.number_input('Coûts fixes mensuels (€)', min_value=0, value=1000, step=100)
    quantites_produites_input = st.text_input('Quantités produites (séparées par des virgules)', '500,1000')
    quantites_produites = list(map(int, quantites_produites_input.split(',')))

with st.sidebar.expander("Paramètres Financiers", expanded=False):
    prix_vente_par_unite = st.number_input('Prix de vente par unité (€)', min_value=0.0, value=5.0, step=0.1)
    nb_mois = st.number_input('Nombre de mois', min_value=1, value=12, step=1)
    smic_mensuel = st.number_input('Salaire visé', min_value=0, value=1500, step=50)

with st.sidebar.expander("Paramètres de Taxe", expanded=False):
    volume_alcoolique = st.number_input('Volume alcoolique de la bière (%)', min_value=0.0, value=5.0, step=0.1)

with st.sidebar.expander("Autres Coûts", expanded=False):
    cout_main_oeuvre = st.number_input('Coût de la main-d\'œuvre mensuel (€)', min_value=0, value=0, step=100)
    cout_marketing = st.number_input('Coût marketing mensuel (€)', min_value=0, value=0, step=50)
    cout_distribution = st.number_input('Coût de distribution mensuel (€)', min_value=0, value=0, step=50)

try:
    df = get_rentabilite_data(investissement_initial, cout_variable_par_unite, prix_vente_par_unite, couts_fixes_mensuels, quantites_produites, nb_mois, volume_alcoolique, cout_main_oeuvre, cout_marketing, cout_distribution, smic_mensuel)

    st.write("## :grey[Rentabilité en fonction de la quantité produite et du nombre de mois]")
    st.divider()

    # Créer un graphique pour chaque quantité produite
    for quantite in quantites_produites:
        st.write(f"### Pour une production de :orange[{quantite}] unités/mois")
        col1, col2 = st.columns(2)
        with col1:
            data = df[df['Quantité Produite (unités/mois)'] == quantite]
            data_melted = data.melt(id_vars=['Mois'], value_vars=['Coût Total (€)', 'Recettes (€)', 'Bénéfice (€)'], var_name='Type', value_name='Valeur')
            
            chart = alt.Chart(data_melted).mark_line().encode(
                x=alt.X('Mois:Q', axis=alt.Axis(title='Mois')),
                y=alt.Y('Valeur:Q', axis=alt.Axis(title='Valeur (€)')),
                color='Type:N',
                tooltip=['Mois:Q', 'Type:N', 'Valeur:Q']
            ).properties(
                title=f'Évolution des Coûts Totaux, Recettes, Bénéfices et Taxes'
            ).configure_legend(
                orient='bottom'
            ).configure_title(
                fontSize=14
            )

            st.altair_chart(chart, use_container_width=True)

        with col2:
            data = df[df['Quantité Produite (unités/mois)'] == quantite]
            
            mois_rentable = data[data['Rentabilité'] == True]['Mois'].min()
            mois_remboursement = data[data['Remboursement Investissement'] == True]['Mois'].min()
            mois_smic = data[data['Salaire Visé'] == True]['Mois'].min()
            production_annuelle = quantite * 12
            
            st.write(f"- Production annuelle : {production_annuelle} hl")
            st.write(f"- Mois où l'entreprise devient rentable : {mois_rentable if pd.notna(mois_rentable) else ':red[Non atteint]'}")
            st.write(f"- Mois où l'investissement initial est remboursé : {mois_remboursement if pd.notna(mois_remboursement) else ':red[Non atteint]'}")
            st.write(f"- Mois où les bénéfices permettent de tirer le salaire visé : {mois_smic if pd.notna(mois_smic) else ':red[Non atteint]'}")
        
        st.divider()

except Exception as e:
    st.error(
        f"**Une erreur est survenue.**\n\nErreur : {e}"
    )
