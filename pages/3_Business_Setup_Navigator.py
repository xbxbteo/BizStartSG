
import streamlit as st
import sys
import re
from pathlib import Path
from src.auth import require_login


# ==========================================================
# 1. CONNECT TO THE RAG ENGINE
# ==========================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from rag_engine import ask_bizstart


# ==========================================================
# 2. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Business Setup Navigator",
    page_icon="🧭",
    layout="wide"
)

require_login()

# ==========================================================
# 3. SOURCE CATALOGUE
# ==========================================================

SOURCE_CATALOGUE = {
    "ACRA-01": "ACRA — Registering a business",
    "ACRA-02": "ACRA — Understanding requirements and eligibility",
    "ACRA-03": "ACRA — Choosing a business structure",
    "ACRA-04": "ACRA — Post-registration guide for local companies",
    "IRAS-01": "IRAS — Basic guide for self-employed individuals",
    "IRAS-02": "IRAS — Basic guide to corporate income tax for companies",
    "IRAS-03": "IRAS — Keeping proper records and accounts",
    "MOM-01": "MOM — Who is entitled to CPF contributions",
    "SFA-01": "SFA — Requirements for Home-based Food Businesses",
    "SFA-02": "SFA — About HDB/URA Home-based Business Scheme",
    "SFA-03": "SFA — Requirements for Licence / Permit for Food Retail"
}


# ==========================================================
# 4. ANALYSE THE BUSINESS SCENARIO
# ==========================================================

def analyse_business_scenario(
    business_activity,
    business_structure,
    operating_location,
    hiring_employees,
    additional_information
):
    """
    Identify relevant agencies and permitted source IDs
    using deterministic scenario-based filtering.
    """

    combined_text = (
        business_activity + " " + additional_information
    ).lower()

    structure = business_structure.lower()
    location = operating_location.lower()

    # Identify food-related businesses.
    food_keywords = [
        "food", "bakery", "baker", "baking",
        "cake", "cakes", "pastry", "pastries",
        "bread", "restaurant", "cafe", "café",
        "catering", "cooked meals", "snacks",
        "beverages", "drinks", "food products"
    ]

    is_food_business = any(
        keyword in combined_text
        for keyword in food_keywords
    )

    # Identify business structure.
    is_company = "private limited company" in structure
    is_sole_proprietorship = "sole proprietorship" in structure
    is_partnership = structure == "partnership"
    is_llp = "limited liability partnership" in structure
    structure_undecided = "not sure" in structure

    # Identify operating arrangement.
    is_home_based = "home" in location

    is_physical_shop = (
        "physical shop" in location
        or "commercial premises" in location
    )

    # Identify employment requirements.
    has_employees = hiring_employees == "Yes"
    employees_undecided = hiring_employees == "Not sure yet"

    # Core ACRA sources.
    allowed_source_ids = [
        "ACRA-01",
        "ACRA-02",
        "ACRA-03"
    ]

    # Company-specific source.
    if is_company:
        allowed_source_ids.append("ACRA-04")

    # Tax source selection.
    if is_company:
        allowed_source_ids.append("IRAS-02")

    elif (
        is_sole_proprietorship
        or is_partnership
        or is_llp
        or structure_undecided
    ):
        allowed_source_ids.append("IRAS-01")

    # Record keeping applies across business structures.
    allowed_source_ids.append("IRAS-03")

    # Employment source only when the user intends to hire.
    if has_employees:
        allowed_source_ids.append("MOM-01")

    # Food-specific sources.
    if is_food_business:

        if is_home_based:
            allowed_source_ids.extend([
                "SFA-01",
                "SFA-02"
            ])

        elif is_physical_shop:
            allowed_source_ids.append("SFA-03")

        else:
            # Location is undecided or not covered by the options.
            allowed_source_ids.extend([
                "SFA-01",
                "SFA-02",
                "SFA-03"
            ])

    # Remove duplicates while preserving order.
    allowed_source_ids = list(dict.fromkeys(allowed_source_ids))

    # Identify relevant agencies for retrieval.
    agencies = ["ACRA", "IRAS"]

    if is_food_business:
        agencies.append("SFA")

    if has_employees:
        agencies.append("MOM")

    # Identify vague business ideas.
    vague_phrases = [
        "selling products",
        "sell products",
        "small business",
        "not decided",
        "not sure what",
        "exploring business ideas",
        "haven't decided",
        "have not decided"
    ]

    is_vague = any(
        phrase in combined_text
        for phrase in vague_phrases
    )

    # Treat very short generic descriptions as vague.
    if len(business_activity.strip().split()) <= 4:

        generic_terms = [
            "products",
            "business",
            "selling",
            "retail"
        ]

        if any(
            term in business_activity.lower()
            for term in generic_terms
        ):
            is_vague = True

    # An undecided structure alone does not make a business idea vague.
    if (
        structure_undecided
        and location == "not decided yet"
        and (
            "product" in combined_text
            or "business" in combined_text
        )
    ):
        is_vague = True

    return {
        "agencies": agencies,
        "allowed_source_ids": allowed_source_ids,
        "is_food_business": is_food_business,
        "is_company": is_company,
        "is_sole_proprietorship": is_sole_proprietorship,
        "is_partnership": is_partnership,
        "is_llp": is_llp,
        "structure_undecided": structure_undecided,
        "is_home_based": is_home_based,
        "is_physical_shop": is_physical_shop,
        "has_employees": has_employees,
        "employees_undecided": employees_undecided,
        "is_vague": is_vague
    }


# ==========================================================
# 5. VALIDATE SOURCE CITATIONS
# ==========================================================

def validate_answer_citations(
    answer,
    allowed_source_ids,
    retrieved_source_ids
):
    """
    A citation is valid only if:
    1. It is permitted for the user's scenario.
    2. The corresponding source was actually retrieved.
    """

    allowed_ids = set(allowed_source_ids)
    retrieved_ids = set(retrieved_source_ids)

    verified_ids = allowed_ids.intersection(retrieved_ids)

    citation_pattern = re.compile(
        r"Source:\s*\(?\s*Source ID:\s*([A-Z]+-\d+)\s*\)?"
        r"|Source ID:\s*([A-Z]+-\d+)",
        re.IGNORECASE
    )

    cited_source_ids = set()

    def replace_citation(match):

        source_id = (
            match.group(1) or match.group(2)
        ).upper()

        if source_id in verified_ids:
            cited_source_ids.add(source_id)
            return f"Source ID: {source_id}"

        return (
            "Source: Further verification needed "
            "(the cited source was not retrieved or "
            "is not applicable to this scenario)"
        )

    cleaned_answer = citation_pattern.sub(
        replace_citation,
        answer
    )

    # Replace source IDs mentioned elsewhere if they were
    # not validated in a citation line.
    source_id_pattern = re.compile(
        r"\b(?:ACRA|IRAS|MOM|SFA|GB)-\d+\b",
        re.IGNORECASE
    )

    def replace_unverified_id(match):

        source_id = match.group(0).upper()

        if source_id in cited_source_ids:
            return source_id

        return "an unverified source"

    cleaned_answer = source_id_pattern.sub(
        replace_unverified_id,
        cleaned_answer
    )

    return cleaned_answer, cited_source_ids


# ==========================================================
# 6. BUILD THE NAVIGATOR PROMPT
# ==========================================================

def build_navigator_prompt(
    business_activity,
    business_structure,
    operating_location,
    hiring_employees,
    additional_information,
    scenario
):

    allowed_ids = scenario["allowed_source_ids"]

    source_list = "\n".join(
        f"- {source_id}: {SOURCE_CATALOGUE[source_id]}"
        for source_id in allowed_ids
    )

    if scenario["is_vague"]:

        response_guidance = """
The business idea is currently too vague for a fully
personalised checklist.

Do NOT generate a definitive or overly detailed checklist.

Instead:

1. Explain that the business idea needs further clarification.
2. Provide only general preliminary steps supported by sources.
3. Do not assume what products the user intends to sell.
4. Do not assume the user needs a food licence.
5. Do not assume the user will operate from home or a shop.
6. Do not assume the user will hire employees.
7. Do not apply company-specific requirements.
8. Do not assume a particular tax treatment.
9. End with a section titled "Questions to Clarify Your Business Idea".

Ask useful questions, especially:

- What products or services do you intend to offer?
- Will you operate online, from home or from physical premises?
- Will you operate alone or with business partners?
- Are you considering hiring employees?

Keep the guidance concise and preliminary.
"""

    else:

        response_guidance = """
Generate a practical, personalised checklist for this
specific business scenario.

Prioritise the steps relevant to the user's business
activity, structure and operating arrangement.

Do not include requirements that clearly do not apply.

Explain when a requirement is conditional or depends
on further details about the business.
"""

    prompt = f"""
You are BizStart SG, an educational business setup
information assistant for Singapore.

Your task is to help aspiring business owners understand
the preliminary steps involved in setting up a business.

BUSINESS SCENARIO

Business activity:
{business_activity}

Preferred business structure:
{business_structure}

Operating arrangement:
{operating_location}

Employees:
{hiring_employees}

Additional information:
{additional_information if additional_information.strip() else "None provided."}

RELEVANT SOURCE IDs PERMITTED FOR THIS SCENARIO

{source_list}

IMPORTANT SOURCE RULES

1. You may only cite source IDs listed above.
2. Never invent, modify or guess a source ID.
3. Only cite a source when its retrieved content supports the statement.
4. ACRA-03 covers business structure selection.
5. ACRA-02 covers registration eligibility and requirements.
6. ACRA-01 covers business registration.
7. ACRA-04 is specifically about post-registration requirements
   for local companies. Do not apply it to other structures.
8. IRAS-01 covers self-employed tax guidance.
9. IRAS-02 covers corporate income tax for companies.
10. IRAS-03 covers proper records and accounts.
11. MOM-01 covers CPF contributions. Use it for relevant
    CPF guidance when employees are part of the scenario.
    Do not cite ACRA-04 as the source for CPF obligations.
12. SFA sources apply only to food-related businesses.
13. Do not cite a source simply because it was retrieved.
14. If no permitted source supports a statement, say
    "Further verification needed".
15. Do not cite IRAS-01 for general record-keeping guidance.
    Use IRAS-03 when its retrieved content supports the claim.

BUSINESS STRUCTURE RULES

- Sole proprietorship: do not apply company secretary,
  company auditor or corporate income tax requirements.
- Ordinary partnership: explain that partnership tax
  treatment differs from company tax treatment.
- LLP: do not treat it as an ordinary partnership or company.
- Private limited company: company-specific requirements
  may be discussed when supported by retrieved sources.
- If the structure is undecided, explain considerations
  without selecting a structure for the user.
- Do not assume tax treatment when the structure is undecided.
- For an undecided structure, IRAS-01 may be used only
  to explain preliminary self-employed tax considerations.
  Make clear that final tax treatment depends on the chosen structure.

ELIGIBILITY RULES

- Use ACRA-02 for registration eligibility information
  when its retrieved content supports the claim.
- ACRA-03 may also support structure-specific eligibility
  or Medisave information when its retrieved content
  directly supports the claim.
- Do not assume the user's age, residency, bankruptcy
  status or Medisave contribution status.
- Present these as matters for the user to check,
  not as facts about the user.

EMPLOYMENT RULES

- If the user has no employees, do not include employee
  CPF obligations as an immediate checklist requirement.
- If hiring is undecided, explain that employment obligations
  should be reviewed if the user eventually hires staff.
- If discussing CPF obligations, use MOM-01 when retrieved
  content supports the statement.
- Do not attribute CPF Submission Number requirements
  to ACRA-04.

CONTENT RULES

- Do not invent licences, fees, deadlines or legal requirements.
- Do not make unsupported claims about tax savings or liability.
- Distinguish confirmed information from matters requiring
  further verification.
- Use plain English and explain technical terms.
- Avoid repeating the same advice in multiple checklist items.
- Do not give professional legal, tax or financial advice.

CITATION FORMAT

For every checklist item supported by a retrieved source,
include a separate source line in this format:

Source ID: ACRA-01

Use only the permitted IDs listed above.

If no permitted retrieved source supports the item, state:

Further verification needed.

Do not put parentheses around the citation line.
Do not write "Source:" before "Source ID:".

{response_guidance}

For a sufficiently detailed business scenario, use:

1. A numbered checklist in a logical sequence.
2. What the user should do.
3. Why it is relevant.
4. The supporting source.

End with a section titled "Your Next Steps".

This is an educational prototype and must not be relied
upon for real-world business decisions.
"""

    return prompt


# ==========================================================
# 7. PAGE HEADER
# ==========================================================

st.title("🧭 Business Setup Navigator")

st.write(
    """
    Planning to start a business in Singapore?

    Tell us about your intended business and preferences.
    BizStart SG will use information retrieved from its
    government-source knowledge base to generate a
    personalised starting checklist.
    """
)

st.info(
    """
    **Your privacy matters**

    You do not need to provide personal identification
    details, business registration numbers or confidential
    information. Use general descriptions only.

    Not sure about something? Select **Not sure yet**.
    """
)

st.divider()


# ==========================================================
# 8. BUSINESS INFORMATION FORM
# ==========================================================

st.subheader("Let's understand your business idea")

st.write(
    """
    Complete the sections below. Your answers help the
    application identify which business setup information
    may be relevant to your situation.
    """
)

with st.form("business_setup_form"):

    # Business idea
    st.markdown("#### 1. Your business idea")

    business_activity = st.text_area(
        "What type of business are you planning to start?",
        placeholder=(
            "Example: Home-based bakery selling cakes and pastries, "
            "freelance IT consulting, or an online clothing store."
        ),
        help="Describe the main products or services you intend to offer.",
        height=110
    )

    st.divider()

    # Business structure
    st.markdown("#### 2. Business structure")

    business_structure = st.selectbox(
        "What business structure are you considering?",
        [
            "Not sure yet",
            "Sole proprietorship",
            "Partnership",
            "Limited Liability Partnership (LLP)",
            "Private Limited Company (Pte Ltd)"
        ],
        help=(
            "You can select 'Not sure yet' if you would like "
            "to understand the different structures first."
        )
    )

    st.divider()

    # Operating arrangement
    st.markdown("#### 3. Operating arrangement")

    operating_location = st.selectbox(
        "Where do you intend to operate your business?",
        [
            "Not decided yet",
            "From home",
            "From a physical shop or commercial premises",
            "Online only",
            "From an office",
            "From a shared or co-working space",
            "Other"
        ],
        help=(
            "Your operating arrangement may affect which "
            "licences or premises-related requirements apply."
        )
    )

    st.divider()

    # Staffing
    st.markdown("#### 4. Staffing")

    hiring_employees = st.radio(
        "Do you intend to hire employees?",
        [
            "Yes",
            "No",
            "Not sure yet"
        ],
        horizontal=True
    )

    st.divider()

    # Additional information
    st.markdown("#### 5. Additional information")

    additional_information = st.text_area(
        "Anything else about your business? (Optional)",
        placeholder=(
            "Example: I intend to sell mainly through social media. "
            "I may expand to a physical shop in the future."
        ),
        help="Include any other general details that may help personalise your checklist.",
        height=100
    )

    submitted = st.form_submit_button(
        "🧭 Generate My Personalised Checklist",
        type="primary",
        width="stretch"
    )


# ==========================================================
# 9. PROCESS THE FORM
# ==========================================================

if submitted:

    if not business_activity.strip():

        st.error(
            "Please describe the type of business you intend to start."
        )

    else:

        # Analyse the business scenario.
        scenario = analyse_business_scenario(
            business_activity,
            business_structure,
            operating_location,
            hiring_employees,
            additional_information
        )

        # Build detailed instructions for the LLM.
        navigator_question = build_navigator_prompt(
            business_activity,
            business_structure,
            operating_location,
            hiring_employees,
            additional_information,
            scenario
        )

        # Build a separate focused retrieval query.
        retrieval_question = f"""
Business activity: {business_activity}

Business structure: {business_structure}

Operating arrangement: {operating_location}

Employees: {hiring_employees}

Additional information:
{additional_information if additional_information.strip() else "None provided."}

Find official Singapore government information relevant
to this business scenario.

Prioritise information about:

- ACRA business registration eligibility and requirements
- Minimum age and residency requirements, where relevant
- Medisave requirements, where relevant
- Choosing a business structure
- Business registration procedures
- Relevant self-employed or company income tax information
- Business record keeping
- Relevant employment or food business requirements, if applicable
"""

        st.divider()
        st.subheader("Your Personalised Business Setup Checklist")

        with st.spinner(
            "Searching relevant government information and preparing your checklist..."
        ):

            try:

                # Retrieve documents using the focused query.
                # Generate the response using the detailed prompt.
                result = ask_bizstart(
                    question=navigator_question,
                    agencies=scenario["agencies"],
                    retrieval_query=retrieval_question
                )

                answer = result["answer"]
                retrieved_sources = result["sources"] or []

                # Extract source IDs actually retrieved.
                retrieved_source_ids = {
                    source.get("source_id", "").upper()
                    for source in retrieved_sources
                    if source.get("source_id")
                }

                # Validate citations.
                answer, cited_source_ids = validate_answer_citations(
                    answer,
                    scenario["allowed_source_ids"],
                    retrieved_source_ids
                )

                # Display only retrieved and cited sources.
                relevant_sources = []
                displayed_source_ids = set()

                for source in retrieved_sources:

                    source_id = source.get(
                        "source_id", ""
                    ).upper()

                    if (
                        source_id in cited_source_ids
                        and source_id not in displayed_source_ids
                    ):

                        relevant_sources.append(source)
                        displayed_source_ids.add(source_id)

                # Save the generated result.
                st.session_state.navigator_result = {
                    "answer": answer,
                    "sources": relevant_sources,
                    "cited_source_ids": sorted(
                        cited_source_ids.intersection(displayed_source_ids)
                    ),
                    "business_activity": business_activity,
                    "business_structure": business_structure,
                    "operating_location": operating_location,
                    "hiring_employees": hiring_employees,
                    "is_vague": scenario["is_vague"]
                }

            except Exception as error:

                st.error(
                    f"Unable to generate your checklist: {error}"
                )


# ==========================================================
# 10. DISPLAY THE GENERATED CHECKLIST
# ==========================================================

if "navigator_result" in st.session_state:

    result = st.session_state.navigator_result

    st.divider()

    # Display the checklist.
    st.markdown(result["answer"])

    # Additional clarification for incomplete business ideas.
    if result["is_vague"]:

        st.info(
            """
            **Your business idea is still at an early stage.**

            The guidance above is preliminary. Once you decide
            what products or services you intend to offer and
            how you plan to operate, you can generate a more
            personalised checklist.
            """
        )

    # Display government sources.
    if result["sources"]:

        with st.expander(
            "📚 View government sources used",
            expanded=False
        ):

            for source in result["sources"]:

                st.markdown(
                    f"**{source['agency']} — "
                    f"{source['document_title']}**"
                )

                st.caption(
                    f"Source ID: {source['source_id']}"
                )

                st.markdown(
                    f"[Open official source]({source['url']})"
                )

                st.divider()

    else:

        st.warning(
            """
            No verifiable source references were identified
            in the generated checklist. Please treat the
            guidance as preliminary and verify requirements
            with the relevant government agencies.
            """
        )

    st.caption(
        """
        This checklist is generated using information available
        in the BizStart SG knowledge base. Some requirements may
        not be covered by the current sources. Always verify
        requirements with the relevant government agencies.
        """
    )

    st.divider()

    if st.button(
        "🔄 Start a New Business Setup",
        width="stretch"
    ):

        del st.session_state.navigator_result
        st.rerun()


# ==========================================================
# 11. EDUCATIONAL DISCLAIMER
# ==========================================================

st.divider()

st.caption(
    """
    Educational prototype only. Information may be incomplete
    or inaccurate. Always consult official government sources
    and qualified professionals for real-world decisions.
    """
)
