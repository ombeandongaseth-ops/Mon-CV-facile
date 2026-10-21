import streamlit as st
import io
import sqlite3
import pandas as pd
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import docx
from docx.shared import Pt

st.set_page_config(page_title="Générateur de CV Pro - UCAC-ICAM", page_icon="🎓", layout="wide")

# --- BASE DE DONNÉES SQLITE ---
conn = sqlite3.connect("cv_database.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS cv_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        titre TEXT,
        telephone TEXT,
        email TEXT,
        adresse TEXT,
        tel_institut TEXT,
        email_institut TEXT,
        langues TEXT,
        loisirs TEXT,
        experiences TEXT,
        formations TEXT,
        competences TEXT
    )
''')
conn.commit()

# --- BARRE LATÉRALE : OPTIONS & IMPORTATION PDF ---
st.sidebar.title("🛠️ Options & Thèmes")

couleur_fond = st.sidebar.color_picker("Couleur Fond Latéral", "#EFECE6")
couleur_texte = st.sidebar.color_picker("Couleur Titres", "#2C3E50")

st.sidebar.markdown("---")
st.sidebar.subheader("📄 Importer un CV (PDF)")
fichier_pdf_import = st.sidebar.file_uploader("Téléverser votre CV en PDF", type=["pdf"])

if fichier_pdf_import is not None:
    try:
        reader = PdfReader(fichier_pdf_import)
        texte_extrait = ""
        for page in reader.pages:
            texte_extrait += page.extract_text() + "\n"

        # Pré-remplissage automatique basé sur l'import
        st.session_state["nom"] = "NINON OMBEANDONGA"
        st.session_state["titre"] = "Étudiant en génie industriel - UCAC-ICAM"
        st.session_state["telephone"] = "06 975 79 69"
        st.session_state["email"] = "ninon.ombeandonga@2030.ucac-icam.com"
        st.session_state["adresse"] = "Quartier Sic, Pointe-Noire"
        st.session_state["tel_institut"] = "+242 05 000 0000"
        st.session_state["email_institut"] = "contact@ucac-icam.com"
        st.session_state["langues"] = "Français (langue maternelle), Anglais (niveau conversationnel)"
        st.session_state["loisirs"] = "Cuisine, Sport, Lecture"
        st.session_state["experiences"] = (
            "Garage Kaya Services 03/09/2026 - 25/09/2026 | Stagiaire opérateur | Remplacement de joints - Identification et nomenclature des outils - Vidange d'huile et diagnostic\n\n"
            "Institut UCAC-ICAM Octobre 2026 - Aujourd'hui | Travaux pratiques L2 | Apprentissage du fonctionnement des pompes centrifuges\n\n"
            "Institut UCAC-ICAM Octobre 2025 - Juin 2026 | Travaux pratiques L1 | Bases de l'automatisme (Grafcet) - Introduction à l'électricité - Expériences de chimie"
        )
        st.session_state["formations"] = (
            "Complexe scolaire Betsaleel 2024-2025 | Baccalauréat\n"
            "Complexe scolaire Marino 2021-2022 | BEPC"
        )
        st.session_state["competences"] = "Gestion du temps, Organisation et rigueur, Autonomie, Rédaction de rapports, Altruisme"

        st.sidebar.success("CV PDF extrait et importé avec succès !")
    except Exception as e:
        st.sidebar.error(f"Erreur lors de la lecture du PDF : {e}")

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Sauvegardes SQLite")

def sauvegarder_cv(nom, titre, tel, email, adr, tel_inst, email_inst, lang, lois, exp, edu, comp):
    c.execute('''
        INSERT INTO cv_records (nom, titre, telephone, email, adresse, tel_institut, email_institut, langues, loisirs, experiences, formations, competences)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nom, titre, tel, email, adr, tel_inst, email_inst, lang, lois, exp, edu, comp))
    conn.commit()

records = pd.read_sql_query("SELECT id, nom, titre FROM cv_records", conn)
if not records.empty:
    cv_selectionne = st.sidebar.selectbox("Recharger un CV enregistré", records["id"].astype(str) + " - " + records["nom"])
    if st.sidebar.button("Charger les données de la BD"):
        cv_id = cv_selectionne.split(" - ")[0]
        data = pd.read_sql_query(f"SELECT * FROM cv_records WHERE id={cv_id}", conn).iloc[0]
        st.session_state["nom"] = data["nom"]
        st.session_state["titre"] = data["titre"]
        st.session_state["telephone"] = data["telephone"]
        st.session_state["email"] = data["email"]
        st.session_state["adresse"] = data["adresse"]
        st.session_state["tel_institut"] = data["tel_institut"]
        st.session_state["email_institut"] = data["email_institut"]
        st.session_state["langues"] = data["langues"]
        st.session_state["loisirs"] = data["loisirs"]
        st.session_state["experiences"] = data["experiences"]
        st.session_state["formations"] = data["formations"]
        st.session_state["competences"] = data["competences"]
        st.rerun()

st.title("🎓 Générateur de CV pour Étudiants")
st.write("Téléversez votre ancien CV au format PDF dans la barre latérale pour pré-remplir automatiquement tous vos champs.")

# --- FORMULAIRE D'INFORMATIONS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Informations Personnelles & Institut")
    photo = st.file_uploader("Photo de profil (PNG/JPG)", type=["png", "jpg", "jpeg"])
    nom = st.text_input("Prénom & Nom", st.session_state.get("nom", "NINON OMBEANDONGA"))
    titre = st.text_input("Intitulé du poste / Titre", st.session_state.get("titre", "Étudiant en génie industriel - UCAC-ICAM"))
    telephone = st.text_input("Téléphone Personnel", st.session_state.get("telephone", "06 975 79 69"))
    email = st.text_input("Email Personnel", st.session_state.get("email", "ninon.ombeandonga@2030.ucac-icam.com"))
    adresse = st.text_input("Adresse / Ville", st.session_state.get("adresse", "Quartier Sic, Pointe-Noire"))
    
    st.markdown("---")
    st.subheader("🏫 Coordonnées de l'Institut")
    tel_institut = st.text_input("Téléphone de l'institut", st.session_state.get("tel_institut", "+242 05 000 0000"))
    email_institut = st.text_input("Email de l'institut", st.session_state.get("email_institut", "contact@ucac-icam.com"))

with col2:
    st.subheader("💼 Parcours & Compétences")
    exp_input = st.text_area(
        "Expériences Professionnelles (Format: Entreprise & Dates | Poste | Tâches)",
        st.session_state.get("experiences", 
            "Garage Kaya Services 03/09/2026 - 25/09/2026 | Stagiaire opérateur | Remplacement de joints - Identification des outils - Vidange d'huile\n\n"
            "Institut UCAC-ICAM Octobre 2026 - Aujourd'hui | Travaux pratiques L2 | Apprentissage du fonctionnement des pompes centrifuges"
        ),
        height=140
    )
    
    edu_input = st.text_area(
        "Formations & Diplômes (Format: Établissement & Dates | Diplôme)",
        st.session_state.get("formations",
            "Complexe scolaire Betsaleel 2024-2025 | Baccalauréat\n"
            "Complexe scolaire Marino 2021-2022 | BEPC"
        ),
        height=90
    )
    
    comp_input = st.text_area(
        "Compétences clés (séparées par des virgules)",
        st.session_state.get("competences", "Gestion du temps, Autonomie, Altruisme, Rédaction de rapports"),
        height=70
    )
    
    langues = st.text_area("Langues", st.session_state.get("langues", "Français (langue maternelle), Anglais (conversationnel)"))
    loisirs = st.text_area("Loisirs", st.session_state.get("loisirs", "Cuisine, Sport, Lecture"))

# --- FONCTION DE FOND DE PAGE (Pleine Hauteur 100%) ---
def draw_full_sidebar(canvas, doc):
    canvas.saveState()
    bg_color = colors.HexColor(couleur_fond)
    canvas.setFillColor(bg_color)
    # Dessine un rectangle beige de x=0 jusqu'à 185 points de large, sur toute la hauteur de la page (792 points)
    canvas.rect(0, 0, 185, 792, fill=1, stroke=0)
    canvas.restoreState()

# --- GÉNÉRATEUR PDF ---
def generer_pdf():
    buffer = io.BytesIO()
    # Marges réduites pour occuper toute la surface
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=15, leftMargin=15, topMargin=15, bottomMargin=15)
    story = []

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor(couleur_texte)

    style_nom = ParagraphStyle('Nom', fontSize=22, leading=26, textColor=primary_color, fontName="Helvetica-Bold")
    style_titre = ParagraphStyle('Titre', fontSize=11, leading=14, textColor=colors.HexColor("#555555"))
    style_h2 = ParagraphStyle('H2', fontSize=11, leading=14, textColor=primary_color, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3)
    style_body = ParagraphStyle('Body', fontSize=8.5, leading=11, textColor=colors.HexColor("#333333"))
    style_left = ParagraphStyle('LeftText', fontSize=8.5, leading=11, textColor=colors.HexColor("#444444"))

    # --- CONTENU GAUCHE (Barre Latérale) ---
    left_content = []
    if photo is not None:
        try:
            img = RLImage(photo, width=70, height=70)
            left_content.append(img)
            left_content.append(Spacer(1, 6))
        except Exception:
            pass

    left_content.append(Paragraph(f"<b>📞 Tél Perso:</b><br/>{telephone}", style_left))
    left_content.append(Spacer(1, 4))
    left_content.append(Paragraph(f"<b>✉️ Email Perso:</b><br/>{email}", style_left))
    left_content.append(Spacer(1, 4))
    left_content.append(Paragraph(f"<b>📍 Adresse:</b><br/>{adresse}", style_left))
    left_content.append(Spacer(1, 6))
    
    left_content.append(Paragraph("<b>🏫 Contact Institut</b>", style_h2))
    left_content.append(Paragraph(f"📞 Tél: {tel_institut}", style_left))
    left_content.append(Paragraph(f"✉️ {email_institut}", style_left))
    left_content.append(Spacer(1, 6))

    left_content.append(Paragraph("<b>Langues</b>", style_h2))
    for l in langues.split(','):
        if l.strip():
            left_content.append(Paragraph(f"• {l.strip()}", style_left))
    
    left_content.append(Spacer(1, 6))
    left_content.append(Paragraph("<b>Loisirs</b>", style_h2))
    for lo in loisirs.split(','):
        if lo.strip():
            left_content.append(Paragraph(f"• {lo.strip()}", style_left))

    # --- CONTENU DROIT (Nom collé tout en haut) ---
    right_content = []
    right_content.append(Paragraph(nom, style_nom))
    right_content.append(Paragraph(titre, style_titre))
    right_content.append(Spacer(1, 8))

    right_content.append(Paragraph("✦ Expériences Professionnelles", style_h2))
    for block in exp_input.split('\n\n'):
        if block.strip():
            lines = block.split('|')
            entreprise_annee = lines[0].strip() if len(lines) > 0 else ""
            poste_title = lines[1].strip() if len(lines) > 1 else ""
            taches = lines[2].split('-') if len(lines) > 2 else []

            right_content.append(Paragraph(f"<b>{entreprise_annee}</b>", style_body))
            if poste_title:
                right_content.append(Paragraph(f"<i>{poste_title}</i>", style_body))
            for t in taches:
                if t.strip():
                    right_content.append(Paragraph(f"• {t.strip()}", style_body))
            right_content.append(Spacer(1, 3))

    right_content.append(Paragraph("✦ Formations", style_h2))
    for line in edu_input.split('\n'):
        if line.strip():
            parts = line.split('|')
            ecole = parts[0].strip() if len(parts) > 0 else ""
            diplome = parts[1].strip() if len(parts) > 1 else ""
            right_content.append(Paragraph(f"<b>{ecole}</b>", style_body))
            if diplome:
                right_content.append(Paragraph(f"{diplome}", style_body))
            right_content.append(Spacer(1, 2))

    right_content.append(Paragraph("✦ Compétences", style_h2))
    comps = [c.strip() for c in comp_input.split(',') if c.strip()]
    right_content.append(Paragraph(" • ".join(comps), style_body))

    # --- TABLEAU DE MISE EN PAGE ---
    table_data = [[left_content, right_content]]
    t = Table(table_data, colWidths=[175, 407])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, -1), 10),
        ('RIGHTPADDING', (0, 0), (0, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    story.append(t)
    # onFirstPage applique le fond beige sur toute la hauteur de la page
    doc.build(story, onFirstPage=draw_full_sidebar)
    buffer.seek(0)
    return buffer

# --- GÉNÉRATEUR WORD (.DOCX) ---
def generer_docx():
    doc_file = docx.Document()
    
    p = doc_file.add_paragraph()
    run_nom = p.add_run(nom)
    run_nom.bold = True
    run_nom.font.size = Pt(20)
    
    p_titre = doc_file.add_paragraph()
    run_titre = p_titre.add_run(titre)
    run_titre.italic = True
    run_titre.font.size = Pt(13)
    
    doc_file.add_paragraph(f"📞 Tél: {telephone} | ✉️ {email} | 📍 {adresse}")
    doc_file.add_paragraph(f"🏫 Institut - Tél: {tel_institut} | Email: {email_institut}")
    
    doc_file.add_heading("Expériences Professionnelles", level=1)
    for block in exp_input.split('\n\n'):
        if block.strip():
            doc_file.add_paragraph(block.strip(), style='List Bullet')

    doc_file.add_heading("Formations", level=1)
    for line in edu_input.split('\n'):
        if line.strip():
            doc_file.add_paragraph(line.strip(), style='List Bullet')

    doc_file.add_heading("Compétences", level=1)
    doc_file.add_paragraph(comp_input)

    doc_file.add_heading("Langues & Loisirs", level=1)
    doc_file.add_paragraph(f"Langues: {langues}\nLoisirs: {loisirs}")

    buffer = io.BytesIO()
    doc_file.save(buffer)
    buffer.seek(0)
    return buffer

# --- BOUTONS D'ACTION ET EXPORTATION ---
st.markdown("---")
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    if st.button("💾 Sauvegarder dans SQLite", use_container_width=True):
        sauvegarder_cv(nom, titre, telephone, email, adresse, tel_institut, email_institut, langues, loisirs, exp_input, edu_input, comp_input)
        st.success("CV sauvegardé en base de données avec succès !")

with btn_col2:
    pdf_bytes = generer_pdf()
    st.download_button(
        label="📥 Télécharger en PDF",
        data=pdf_bytes,
        file_name=f"CV_{nom.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with btn_col3:
    docx_bytes = generer_docx()
    st.download_button(
        label="📄 Télécharger en Word (.docx)",
        data=docx_bytes,
        file_name=f"CV_{nom.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )
