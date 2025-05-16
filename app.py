import streamlit as st
import openai
import json
import pandas as pd
import re
import fitz

# --- OpenAI Setup ---
api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=api_key)

# --- Section Checklists ---
dpdpa_checklists = {
    "4": {
        "title": "Grounds for Processing Personal Data",
        "items": [
            {"id" : "4.1", "text" : "The policy must state that personal data is processed **only as per the provisions of the Digital Personal Data Protection Act, 2023**."},
            {"id" : "4.2", "text" : "The policy must confirm that personal data is processed **only for a lawful purpose**."},
            {"id" : "4.3", "text" : "The policy must define **lawful purpose** as any purpose **not expressly forbidden by law**."},
            {"id" : "4.4", "text" : "The policy must include a statement that personal data is processed **only with the consent of the Data Principal**."},
            {"id" : "4.5", "text" : "Alternatively, the policy must specify that personal data is processed **for certain legitimate uses**, as defined under the Act."}
        ]
    },
    "5": {
        "title": "Notice",
        "items": [
            {"id" : "5.1", "text" : "The policy must state that **every request for consent** is accompanied or preceded by a **notice from the Data Fiduciary to the Data Principal**."},
            {"id" : "5.2", "text" : "The notice must clearly specify the **personal data proposed to be processed**."},
            {"id" : "5.3", "text" : "The notice must clearly specify the **purpose for which the personal data is proposed to be processed**."},
            {"id" : "5.4", "text" : "The notice must explain the **manner in which the Data Principal can exercise her rights under Section 6(4)** (withdrawal of consent)."},
            {"id" : "5.5", "text" : "The notice must explain the **manner in which the Data Principal can exercise her rights under Section 13** (grievance redressal)."},
            {"id" : "5.6", "text" : "The notice must specify the **manner in which a complaint can be made to the Data Protection Board**."},
            {"id" : "5.7", "text" : "If consent was obtained **before the commencement of the Act**, the policy must state that a notice will be sent **as soon as reasonably practicable**."},
            {"id" : "5.8", "text" : "The post-commencement notice must mention the **personal data that has been processed**."},
            {"id" : "5.9", "text" : "The post-commencement notice must mention the **purpose for which the personal data has been processed**."},
            {"id" : "5.10", "text" : "The post-commencement notice must mention the **manner in which the Data Principal can exercise her rights under Section 6(4)**."},
            {"id" : "5.11", "text" : "The post-commencement notice must mention the **manner in which the Data Principal can exercise her rights under Section 13**."},
            {"id" : "5.12", "text" : "The post-commencement notice must mention the **manner in which a complaint can be made to the Board**."},
            {"id" : "5.13", "text" : "The policy must mention that the Data Fiduciary **may continue to process personal data** until the Data Principal **withdraws her consent**."},
            {"id" : "5.14", "text" : "The policy must provide the Data Principal an **option to access the contents of the notice** in **English or any language listed in the Eighth Schedule of the Constitution**."}
        ]
    },
    "6": {
        "title": "Consent",
        "items": [
            {"id" : "6.1", "text" : "The policy must state that **consent is free, specific, informed, unconditional, and unambiguous**, given through a **clear affirmative action**."},
            {"id" : "6.2", "text" : "The policy must specify that **consent signifies agreement to process personal data only for the specified purpose**."},
            {"id" : "6.3", "text" : "The policy must state that **consent is limited to such personal data as is necessary for the specified purpose**."},
            {"id" : "6.4", "text" : "The policy must mention that **any part of the consent that violates this Act, rules under it, or any other law in force is invalid to that extent**."},
            {"id" : "6.5", "text" : "The request for consent must be presented in **clear and plain language**."},
            {"id" : "6.6", "text" : "The request for consent must allow the Data Principal to access it in **English or any language listed in the Eighth Schedule of the Constitution**."},
            {"id" : "6.7", "text" : "The request for consent must provide **contact details of a Data Protection Officer** or **another authorised person** responsible for handling Data Principal queries."},
            {"id" : "6.8", "text" : "The policy must clearly state that the **Data Principal has the right to withdraw consent at any time**."},
            {"id" : "6.9", "text" : "The **ease of withdrawing consent** must be comparable to the **ease with which consent was given**."},
            {"id" : "6.10", "text" : "The policy must mention that **consequences of withdrawal shall be borne by the Data Principal**."},
            {"id" : "6.11", "text" : "The policy must state that **withdrawal does not affect the legality of data processing done before withdrawal**."},
            {"id" : "6.12", "text" : "The policy must mention that upon withdrawal of consent, the **Data Fiduciary and its Data Processors must cease processing** the personal data **within a reasonable time**, unless permitted by law."},
            {"id" : "6.13", "text" : "The policy must state that consent **can be managed, reviewed, or withdrawn through a Consent Manager**."},
            {"id" : "6.14", "text" : "The policy must specify that the **Consent Manager is accountable to the Data Principal** and acts on her behalf."},
            {"id" : "6.15", "text" : "The policy must specify that **every Consent Manager is registered with the Board** under prescribed conditions."},
            {"id" : "6.16", "text" : "The policy must mention that, in case of dispute, the **Data Fiduciary must prove that proper notice was given and valid consent was obtained** as per the Act and its rules."}
        ]
    },
    "7": {
        "title": "Certain Legitimate Uses",
        "items": [
            {"id" : "7.1", "text" : "The policy must allow personal data to be processed for the **specified purpose for which the Data Principal voluntarily provided the data**, if she has **not indicated non-consent** to such use."},
            {"id" : "7.2", "text" : "The policy must permit personal data to be processed by the State or its instrumentalities for providing or issuing **subsidy, benefit, service, certificate, licence, or permit**, as prescribed, where the Data Principal has **previously consented** to such processing."},
            {"id" : "7.3", "text" : "The policy must allow personal data to be processed by the State or its instrumentalities if the data is **already available in digital or digitised form in notified government databases**, subject to prescribed standards and government policies."},
            {"id" : "7.4", "text" : "The policy must allow personal data to be processed by the State or its instrumentalities for performing any **legal function** under existing Indian laws or **in the interest of sovereignty and integrity of India or State security**."},
            {"id" : "7.5", "text" : "The policy must allow personal data to be processed to **fulfil a legal obligation** requiring any person to disclose information to the State or its instrumentalities, as per applicable laws."},
            {"id" : "7.6", "text" : "The policy must permit personal data to be processed for **compliance with any judgment, decree, or order** issued under Indian law, or for **contractual or civil claims under foreign laws**."},
            {"id" : "7.7", "text" : "The policy must allow personal data to be processed to **respond to a medical emergency** involving a **threat to life or immediate health risk** of the Data Principal or any individual."},
            {"id" : "7.8", "text" : "The policy must allow personal data to be processed to **provide medical treatment or health services** during an **epidemic, outbreak, or other threat to public health**."},
            {"id" : "7.9", "text" : "The policy must permit processing of personal data to **ensure safety of or provide assistance/services to individuals** during any **disaster or breakdown of public order**."},
            {"id" : "7.10", "text" : "The policy must define 'disaster' in accordance with the **Disaster Management Act, 2005 (Section 2(d))**."},
            {"id" : "7.11", "text" : "The policy must allow personal data to be processed for purposes related to **employment**, or to **safeguard the employer from loss or liability**, including prevention of corporate espionage, confidentiality of trade secrets or IP, and enabling services/benefits to employee Data Principals."}
        ]
    },
    "8": {
        "title": "General Obligations of Data Fiduciary",
        "items": [
            {"id" : "8.1", "text" : "The policy must state that the Data Fiduciary is responsible for complying with the Act and its rules, even if the Data Principal fails to perform her duties."},
            {"id" : "8.2", "text" : "The policy must state that the Data Fiduciary may engage or involve a Data Processor **only under a valid contract** to process personal data for offering goods or services."},
            {"id" : "8.3", "text" : "The policy must ensure that if personal data is used to make a decision affecting the Data Principal, the data must be **complete, accurate, and consistent**."},
            {"id" : "8.4", "text" : "The policy must ensure that if personal data is disclosed to another Data Fiduciary, the data must be **complete, accurate, and consistent**."},
            {"id" : "8.5", "text" : "The policy must require the Data Fiduciary to implement **appropriate technical and organisational measures** to ensure compliance with the Act and its rules."},
            {"id" : "8.6", "text" : "The policy must mandate **reasonable security safeguards** to protect personal data from breaches, including breaches by its Data Processors."},
            {"id" : "8.7", "text" : "The policy must state that in the event of a **personal data breach**, the Data Fiduciary shall **inform both the Board and each affected Data Principal** in the prescribed manner."},
            {"id" : "8.8", "text" : "The policy must mandate that personal data be **erased upon withdrawal of consent** or as soon as it is reasonable to assume that the **specified purpose is no longer being served**, whichever is earlier."},
            {"id" : "8.9", "text" : "The policy must mandate that the Data Fiduciary must **cause its Data Processors to erase the data** when retention is no longer justified."},
            {"id" : "8.10", "text" : "The policy must define that the specified purpose is deemed no longer served if the Data Principal has neither **approached the Data Fiduciary for the purpose** nor **exercised her rights** within the prescribed time period."},
            {"id" : "8.11", "text" : "The policy must require publishing the **business contact details** of the Data Protection Officer (if applicable) or of an authorised person able to respond to questions about personal data processing."},
            {"id" : "8.12", "text" : "The policy must provide an **effective grievance redressal mechanism** for Data Principals."},
            {"id" : "8.13", "text" : "The policy must clarify that a Data Principal is considered as **not having approached** the Data Fiduciary if she has not initiated contact in person, or through physical or electronic communication, for the purpose within a prescribed period."}
        ]
    }
}

# --- Block Splitter ---
def break_into_blocks(text):
    lines = text.splitlines()
    blocks, current_block = [], []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r'^([A-Z][A-Za-z\s]+|[0-9]+\.\s.*)$', stripped):
            if current_block:
                blocks.append(' '.join(current_block).strip())
                current_block = []
            current_block.append(stripped)
        else:
            current_block.append(stripped)
    if current_block:
        blocks.append(' '.join(current_block).strip())
    return blocks

# --- PDF Extractor ---
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def is_valid_block(text):
    text = text.strip()
    # 1. Must be at least 10 words
    if len(text.split()) < 8:
        return False

    return True

# --- Prompt Generator ---
def build_prompt(section_id, checklist_items, block_text):
    checklist_text = "\n".join([
        f"- {item['id']}: {item['text']}" for item in checklist_items
    ])

    prompt = f"""
    You are a data privacy compliance checker for the Indian DPDPA law.
    
    Evaluate the following policy block against each checklist item below.
    Use ONLY the block — do not assume anything not written.
    
    Checklist (Section {section_id}):
    {checklist_text}
    
    Policy Block:
    \"\"\"{block_text}\"\"\"
    
    For each checklist item, return:
    - checklist_id
    - status: Explicitly Mentioned / Partially Mentioned / Missing
    - matched_sentence: quote from the block, or blank if not found
    - justification: a short explanation for your choice
    
    Return your answer as a JSON list. Do NOT add extra text.
    """
    return prompt.strip()

# --- GPT Call ---
def analyze_block_against_section(section_id, block, checklist_items, client):
    try:
        prompt = build_prompt(section_id, checklist_items, block["text"])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a legal compliance evaluator."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()
        evaluations = json.loads(content)

        return {
            "block_id": block["block_id"],
            "section_id": section_id,
            "evaluations": evaluations
        }

    except Exception as e:
        print(f"GPT error on block {block['block_id']}: {e}")
        return None

        
def update_compiled_output(compiledOutput, gpt_result):
    for evaluation in gpt_result["evaluations"]:
        checklist_id = evaluation["checklist_id"]
        status = evaluation["status"]
        sentence = evaluation["matched_sentence"]
        justification = evaluation["justification"]

        # Only add Explicitly/Partially Mentioned
        if status in ["Explicitly Mentioned", "Partially Mentioned"]:
            formatted = (
                f"{sentence} matches this checklist item because {justification} "
                f"({status})"
            )

            # Find or create entry in compiledOutput
            found = False
            for entry in compiledOutput:
                if entry["checklist_id"] == checklist_id:
                    entry["Match-justification mapping list"].append(formatted)
                    found = True
                    break

            if not found:
                compiledOutput.append({
                    "checklist_id": checklist_id,
                    "Match-justification mapping list": [formatted]
                })
                
def generate_final_summary(compiledOutput, checklist_ids):
    final_summary = []

    for cid in checklist_ids:
        # Find if this checklist_id exists in compiledOutput
        entry = next((e for e in compiledOutput if e["checklist_id"] == cid), None)

        if entry:
            matches = entry["Match-justification mapping list"]
            has_explicit = any("(Explicitly Mentioned)" in m for m in matches)
            has_partial = any("(Partially Mentioned)" in m for m in matches)

            if has_explicit:
                coverage = "Explicitly Mentioned"
                score = 1.0
            elif has_partial:
                coverage = "Partially Mentioned"
                score = 0.5
            else:
                coverage = "Missing"
                score = 0.0
        else:
            # Completely missing
            matches = []
            coverage = "Missing"
            score = 0.0

        final_summary.append({
            "checklist_id": cid,
            "coverage": coverage,
            "confidence_score": score,
            "matches": matches
        })

    return final_summary


def set_custom_css():
    st.markdown("""
    <style>
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #2E2E38;
        color: white !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Main text and headers */
    section.main div.block-container {
        color: #2E2E38 !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #2E2E38 !important;
    }

    /* Fix for input text color */
    input, textarea, select, div[role="textbox"] {
        color: #2E2E38 !important;
        caret-color: #2E2E38
    }

    /* Fix for selectbox and dropdowns */
    .stSelectbox div, .stRadio div, .stCheckbox div, .stTextInput div, .stDownloadButton div {
        color: #2E2E38 !important;
    }

    /* Fix file uploader text inside black box */
    .stFileUploader div, .stFileUploader span {
    color: white !important;
    }
    /* --- Force white text in selectbox/multiselect dropdowns with dark bg --- */
    div[data-baseweb="select"] {
        color: white !important;
    }
    
    div[data-baseweb="select"] * {
        color: white !important;
    }


    /* Fix Browse files button text inside file uploader */
    .stFileUploader button,
    .stFileUploader label {
    color: black !important;
    font-weight: 500;
    }

    /* Fix download and regular buttons */
    .stButton > button, .stDownloadButton > button {
        color: white !important;
        background-color: #1a9afa;
        font-weight: 600;
        border-radius: 6px;
        border: none;
    }
    
        
    /* Only for actual input and textarea fields */
    input, textarea {
        background-color: #FFFFFF !important;
        color: #2E2E38 !important;
        border: 1px solid #2E2E38 !important;
        border-radius: 6px !important;
        caret-color: #2E2E38
    }
    /* Additional fix for Streamlit's internal markdown editor (if used) */
    div[contenteditable="true"] {
        caret-color: #2E2E38 !important;
        color: #2E2E38 !important;
    }

    
    /* For Streamlit selectboxes */
    div[data-baseweb="select"] {
        background-color: #2E2E38 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
    }
    div[data-baseweb="select"] * {
        color: white !important;
    }

    /* === Fix Streamlit checkbox visibility === */
    div[data-baseweb="checkbox"] > label > div {
        background-color: white !important;
        border: 2px solid #2E2E38 !important;
        border-radius: 4px !important;
        width: 20px !important;
        height: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-right: 10px !important;
    }
    
    /* Show checkmark when selected */
    div[data-baseweb="checkbox"] svg {
        stroke: #2E2E38 !important;
        stroke-width: 2.5px !important;
    }
    /* === FIX: Cursor visibility in text areas === */
    textarea,
    .stTextArea textarea,
    div[role="textbox"],
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #2E2E38 !important;
        caret-color: #2E2E38 !important;
        border: 1px solid #2E2E38 !important;
        border-radius: 6px !important;
    }
    
    /* Explicit caret fix for editable areas */
    div[contenteditable="true"] {
        caret-color: #2E2E38 !important;
        color: #2E2E38 !important;
    }

    /* Force DataFrame cell background and text to be readable */
.css-1r6slb0 .element-container {
        background-color: white !important;
        color: black !important;
    }

    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.set_page_config(page_title="DPDPA Compliance Tool", layout="wide")
set_custom_css()
st.sidebar.markdown("<h1 style='font-size:42px; font-weight:700;'>Navigation</h1>", unsafe_allow_html=True)

menu = st.sidebar.radio("", [
    "Homepage",
    "Policy Compliance Checker",
    "Policy Generator",
    "Dashboard & Reports",
    "Knowledge Assistant",
    "Admin Settings"
])
st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown("""
    <div style='padding: 0px 12px 0px 0px;'>
        <img src='https://i.postimg.cc/j2dv9kZ2/EY-Parthenon-idp-Wq1a8hl-0.png' width='200'>
    </div>
""", unsafe_allow_html=True)
# --- Homepage ---
if menu == "Homepage":
    st.title("DPDPA Compliance Tool")
    st.markdown("""
    Welcome to the Digital Personal Data Protection Act (DPDPA) Compliance Platform.
    Use the navigation panel to begin generating or matching your policy to India's latest data protection laws.
    """)

# --- Policy Generator ---
elif menu == "Policy Generator":
    st.title("Create a new Policy")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Full Policy Generator", "Section-wise Generator", "Lifecycle-wise Template", 
        "GPT Draft Assistant", "Saved Drafts"])

    with tab1:
        st.subheader("Full Policy Generator")
        st.text_area("Enter your complete policy draft:", height=300)
        st.button("Generate Suggestions with GPT")

    with tab2:
        st.subheader("Section-wise Generator")
        section = st.selectbox("Choose Section", ["Notice", "Consent", "Data Principal Rights", "Security"])
        st.text_area(f"Draft for {section}:", height=200)
        st.button("Suggest Completion")

    with tab3:
        st.subheader("Lifecycle-wise Template")
        st.markdown("Fill stage-specific privacy info:")
        stages = ["Collection", "Processing", "Storage", "Sharing", "Erasure"]
        for stage in stages:
            st.text_area(f"{stage} Stage", key=stage)

    with tab4:
        st.subheader("GPT-Assisted Draft Builder")
        prompt = st.text_input("Describe your need (e.g. privacy for HR data):")
        st.button("Generate Draft")

    with tab5:
        st.subheader("Saved Drafts")
        st.dataframe({"Draft": ["HR Policy", "Marketing Policy"], "Last Modified": ["2025-05-10", "2025-05-01"]})

# --- Policy Compliance Checker ---
elif menu == "Policy Compliance Checker":

    #st.title("Match Policy to DPDPA")
    st.markdown("<h1 style='font-size:38px; font-weight:800;'>Match Policy to DPDPA</h1>", unsafe_allow_html=True)
    
    #st.header("1. Upload Your Policy Document")
    st.markdown("<h3 style='font-size:24px; font-weight:700;'>1. Upload Your Policy Document</h3>", unsafe_allow_html=True)

    upload_option = st.radio("Choose input method:", ["Paste text", "Upload PDF"])
    if upload_option == "Paste text":
        policy_text = st.text_area("Paste your Privacy Policy text:", height=300)
    elif upload_option == "Upload PDF":
        uploaded_pdf = st.file_uploader("Upload PDF file", type="pdf", label_visibility="collapsed")

        if uploaded_pdf:
            # 👇 Custom visible filename
            st.markdown(f"""
            <div style="padding: 6px 12px; background-color:#f1f1f1; display:inline-block;
                        border-radius:6px; font-weight:600; color:#000; font-family: Arial, sans-serif;">
            📄 Uploaded file: {uploaded_pdf.name}
            </div>
            """, unsafe_allow_html=True)

            policy_text = extract_text_from_pdf(uploaded_pdf)
        else:
            policy_text = ""


    #st.header("4. Industry Context (Optional)")
    st.markdown("<h3 style='font-size:24px; font-weight:700;'>2. Industry Context (Optional)</h3>", unsafe_allow_html=True)
    industry = st.selectbox("", ["General", "Automotive", "Healthcare", "Fintech", "Other"])
    if industry == "Other":
        custom_industry = st.text_input("Specify your industry")
    else:
        custom_industry = None

    st.markdown("<h3 style='font-size:24px; font-weight:700;'>3. Choose DPDPA Section</h3>", unsafe_allow_html=True)
    section_options = [f"{sid} — {dpdpa_checklists[sid]['title']}" for sid in dpdpa_checklists] + ["All Sections"]
    section_id = st.selectbox("Choose DPDPA Section", section_options)
    section_key = section_id.split(" — ")[0] if " — " in section_id else section_id
    
    # Run
    st.markdown("<h3 style='font-size:24px; font-weight:700;'>4. Run Compliance Check</h3>", unsafe_allow_html=True)
    if st.button("Run Compliance Check"):
        with st.spinner("🧠 Running GPT analysis..."):
            raw_blocks = break_into_blocks(policy_text)
            blocks = [b for b in raw_blocks if is_valid_block(b["text"])]
            st.markdown(f"✅ Detected **{len(blocks)}** valid blocks for evaluation.")
            with st.expander("📄 Preview: Blocks being sent to GPT", expanded=False):
                for block in blocks:
                    st.markdown(f"**{block['block_id']}:**")
                    st.markdown(block["text"])
                    st.markdown("---")
    
            st.markdown("### ⚙️ Evaluation Settings")
            st.markdown(f"- **Selected Section:** {section_id}")
            st.markdown(f"- **Industry Context:** General")
            st.markdown("---")
    
            compiledOutput = []
    
            if section_key == "All Sections":
                st.markdown("#### 📘 Running for **All Sections**")
                for sid in dpdpa_checklists:
                    st.markdown(f"### 🔍 Section {sid}: {dpdpa_checklists[sid]['title']}")
                    checklist_items = dpdpa_checklists[sid]["items"]
                    checklist_ids = [item["id"] for item in checklist_items]
                    for block in blocks:
                        result = analyze_block_against_section(sid, block, checklist_items, client)
                        if result:
                            update_compiled_output(compiledOutput, result)
                final_summary = generate_final_summary(compiledOutput, checklist_ids)
            else:
                st.markdown(f"#### 📘 Running for **Section {section_key}: {dpdpa_checklists[section_key]['title']}**")
                checklist_items = dpdpa_checklists[section_key]["items"]
                checklist_ids = [item["id"] for item in checklist_items]
                for block in blocks:
                    result = analyze_block_against_section(section_key, block, checklist_items, client)
                    if result:
                        update_compiled_output(compiledOutput, result)
                final_summary = generate_final_summary(compiledOutput, checklist_ids)
    
            st.success("✅ GPT evaluation complete. Displaying results...")
    
            st.markdown("### 📋 Final Checklist Coverage")
            st.write("DEBUG: Final Summary Output", final_summary)

            for item in final_summary:
                coverage = item["coverage"]
                color = {
                    "Explicitly Mentioned": "#198754",
                    "Partially Mentioned": "#FFC107",
                    "Missing": "#DC3545"
                }.get(coverage, "#6c757d")
    
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <strong>{item['checklist_id']}</strong><br>
                    <span style="color:white;background-color:{color};padding:3px 10px;border-radius:6px;font-size:13px;">{coverage}</span>
                    <span style="margin-left:10px;">Confidence Score: {item['confidence_score']}</span>
                </div>
                """, unsafe_allow_html=True)
    
                if item["matches"]:
                    with st.expander("📌 Matches & Justifications"):
                        for m in item["matches"]:
                            st.markdown(f"> {m}")
                else:
                    st.markdown("*No matches found.*")
    
                st.markdown("---")


