import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components

st.set_page_config(layout="wide")  # Utiliser la mise en page large

# Centrer le titre
st.markdown("<h1 style='text-align: center;'>Ze Calculator de Salaire</h1>", unsafe_allow_html=True)

# Move the salary input, warnings, and info to the sidebar
with st.sidebar:
    st.markdown(
        """
        <div style="
            background-color: #E6F3FF;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        ">
            <h3 style="margin: 0;">Informations</h3>
            <p style="margin: 5px 0;">Nous sommes en 2024.</p>
            <p style="margin: 5px 0;">Le plafond mensuel de la Sécurité Sociale est de 3 864,00 euros.</p>
            <p style="margin: 5px 0;">Le Smic Mensuel est de 1 766,96 euros.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    salary = st.number_input('Saisis le salaire brut mensuel :', min_value=0)
    num_employees = st.number_input('Nombre de salariés dans l\'entreprise :', min_value=1, step=1)

    if salary < 1766.96:
        st.warning('ALERTE: Ce salaire est en-dessous du SMIC')
    elif salary > 3864:
        st.warning('ALERTE: Ce salaire est au-dessus du plafond de la Sécurité Sociale')

salary_brut_annuel = round(salary * 12, 2)
smic_mens_mala = 151.67 * 11.52 * 12 * 2.5
smic_mens_caf = 151.67 * 11.52 * 12 * 3.5

# Calcul détaillé des cotisations
cotisations = {
    "Sécurité Sociale": {
        "Cotisation Maladie 7%": round(salary_brut_annuel * 0.07, 2),
        "Cotisation Complément Maladie 6%": round(salary_brut_annuel * 0.06, 2) if salary_brut_annuel > smic_mens_mala else 0,
        "Cotisation Vieillesse déplafonnée": round(salary_brut_annuel * 0.0202, 2),
        "Cotisation Vieillesse plafonnée": round(min(salary_brut_annuel, 46368) * 0.0855, 2),
        "Cotisation Allocations Familiales": round(salary_brut_annuel * 0.0345, 2),
        "Cotisation Complément Allocations Familiales": round(salary_brut_annuel * 0.0345, 2) if salary_brut_annuel > smic_mens_caf else 0,
    },
    "Assurance Chômage": {
        "Cotisation Chômage": round(salary_brut_annuel * 0.0405, 2),
    },
    "Retraite Complémentaire": {
        "Cotisation AGIRC-ARRCO Tranche 1": round(min(salary_brut_annuel, 43992) * 0.0481, 2),
        "Cotisation AGIRC-ARRCO Tranche 2": round(max(0, min(salary_brut_annuel - 43992, 329928)) * 0.13, 2),
    },
    "Formation Professionnelle": {
        "Contribution à la formation professionnelle": round(salary_brut_annuel * 0.0155, 2),
    },
    "Autres Taxes": {
        "Versement transport": round(salary_brut_annuel * 0.0255, 2),
        "Taxe d'apprentissage": round(salary_brut_annuel * 0.0068, 2),
        "Participation à l'effort de construction": round(salary_brut_annuel * 0.0045, 2),
    }
}

# Calculer le total des charges
total_charges = sum(sum(sous_cat.values()) for sous_cat in cotisations.values())
cout_total_employeur = salary_brut_annuel + total_charges

# Format the numbers with thousands separators and 2 decimal places
def formater_montant(montant):
    return "{:,.2f}".format(montant).replace(",", " ").replace(".", ",")

# Afficher les deux cartouches principales
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div style="
            background-color: #E6F3FF;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        ">
            <h3 style="margin: 0;">Salaire brut annuel</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{formater_montant(salary_brut_annuel)} €</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="
            background-color: #FFF3E6;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        ">
            <h3 style="margin: 0;">Coût total pour l'employeur</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{formater_montant(cout_total_employeur)} €</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Définir une palette de couleurs bleu
colors = ['#E6F3FF', '#BDDEFF', '#94C9FF', '#6BB4FF', '#42A0FF']

# Afficher les cartouches colorées avec détails
st.subheader('Répartition détaillée des cotisations')

# Créer des colonnes pour les cartouches
cols = st.columns(len(cotisations))

for i, (categorie, sous_categories) in enumerate(cotisations.items()):
    with cols[i]:
        total_categorie = sum(sous_categories.values())
        st.markdown(
            f"""
            <div style="
                background-color: {colors[i]};
                padding: 10px;
                border-radius: 5px;
                height: 100%;
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                transition: 0.3s;
            ">
                <h3 style="margin: 0; color: #000;">{categorie}</h3>
                <p style="font-size: 18px; margin: 5px 0; color: #000;">Total : {formater_montant(total_categorie)} €</p>
                <hr style="margin: 10px 0; border-color: #000;">
                {''.join(f'<p style="margin: 5px 0; font-size: 14px; color: #000;"><strong>{sous_cat}:</strong> {formater_montant(montant)} €</p>' for sous_cat, montant in sous_categories.items())}
            </div>
            """,
            unsafe_allow_html=True)

        

# Créer un dataframe pour le graphique récapitulatif
df_cotisations = pd.DataFrame([(cat, sum(sous_cat.values())) for cat, sous_cat in cotisations.items()], 
                              columns=['Catégorie', 'Montant'])

# Créer un graphique Altair avec des libellés horizontaux
chart = alt.Chart(df_cotisations).mark_bar().encode(
    y=alt.Y('Catégorie:N', sort='-x'),
    x=alt.X('Montant:Q', title='Montant (€)'),
    color=alt.Color('Catégorie:N', scale=alt.Scale(range=colors))
).properties(
    title='Graphique récapitulatif des cotisations',
    width=600,
    height=300
)

# Afficher le graphique Altair
st.altair_chart(chart, use_container_width=True)