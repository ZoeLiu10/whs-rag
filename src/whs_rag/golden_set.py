# Golden test set for the WHS Codes of Practice RAG
# Built from the three uploaded Safe Work Australia PDFs:
#   - Construction Work Code of Practice (Nov 2024)
#   - First aid in the workplace Code of Practice (Jul 2019)
#   - How to manage work health and safety risks Code of Practice (Nov 2024)
#
# Usage in 03_rag_eval (Step 6): paste this cell in place of the example in_scope / out_of_scope.
#
# 1. The three file names below match the PDFs you uploaded. If you rename them in the volume, change these too
#    (source_hit checks that this string appears in the retrieved chunk's doc_uri).
# 2. "page" in each comment is the PDF page number ("Page X of N" in the footer) so you can
#    check the fact against the original before trusting the scores.
# 3. Every expected fact was taken from the PDFs, but read through them once yourself:
#    if a fact is wrong, every score built on it is wrong.

CONSTRUCTION = "construction_work.pdf"                          # matches your upload
FIRST_AID = "first_aid_in_the_work.pdf"                         # matches your upload
RISK = "how_to_manage_work_health_and_safety_risks.pdf"          # matches your upload

in_scope = [
    # ---------------- Construction Work (9) ----------------
    {   # single fact | p.10
        "inputs": {"question": "What is the cost threshold for construction work to count as a construction project?"},
        "expectations": {
            "expected_facts": ["A construction project is one where the cost of the construction work is $250,000 or more."],
            "expected_source": CONSTRUCTION,
        },
    },
    {   # single fact | p.26
        "inputs": {"question": "At what depth must the risk of a trench collapsing be controlled with shoring, benching or battering?"},
        "expectations": {
            "expected_facts": ["Trenches 1.5 metres or more in depth must be controlled with shoring, benching or battering."],
            "expected_source": CONSTRUCTION,
        },
    },
    {   # single fact | p.40
        "inputs": {"question": "A worker applied for a white card and hasn't heard back. When are they treated as holding one?"},
        "expectations": {
            "expected_facts": ["If the worker has not been notified of a decision within 60 days of applying, they are taken to hold a white card until the regulator decides."],
            "expected_source": CONSTRUCTION,
        },
    },
    {   # multi-point | p.36
        "inputs": {"question": "What must a WHS management plan for a construction project contain?"},
        "expectations": {
            "expected_facts": [
                "Names, positions and health and safety responsibilities of people with specific WHS roles.",
                "Arrangements for consultation, cooperation and coordination.",
                "Arrangements for managing WHS incidents.",
                "Site-specific health and safety rules and how people will be informed of them.",
                "Arrangements to collect, assess, monitor and review SWMS.",
            ],
            "expected_source": CONSTRUCTION,
        },
    },
    {   # multi-point | p.21
        "inputs": {"question": "What must the principal contractor's site signs show?"},
        "expectations": {
            "expected_facts": [
                "The principal contractor's name and telephone contact numbers, including an out of hours number.",
                "The location of the site office for the project, if there is one.",
                "The signs must be clearly visible from outside the workplace or work area.",
            ],
            "expected_source": CONSTRUCTION,
        },
    },
    {   # paraphrase (question avoids the term 'owner-builder') | p.45
        "inputs": {"question": "If I do some minor renovations on my own house, am I treated as a business with WHS duties?"},
        "expectations": {
            "expected_facts": ["An individual doing maintenance, refurbishment or minor renovations of their own home is not considered an owner-builder or a PCBU."],
            "expected_source": CONSTRUCTION,
        },
    },
    {   # table + paraphrase (answer is in the 'not construction work' table) | p.49
        "inputs": {"question": "Does replacing a few broken roof tiles on an existing house count as construction work?"},
        "expectations": {
            "expected_facts": [
                "No, replacing or repairing individual roof tiles is minor repair work and is not construction work.",
                "Minor work needs little or no pre-start preparation, uses minimal control measures and does not affect the structure's design or stability.",
            ],
            "expected_source": CONSTRUCTION,
        },
    },
    {   # table | p.51
        "inputs": {"question": "Is installing shade sails over a swimming pool high risk construction work, and why?"},
        "expectations": {
            "expected_facts": ["Yes, it is work in or near water or other liquid that involves a risk of drowning."],
            "expected_source": CONSTRUCTION,
        },
    },
    {   # table / numbers | p.85
        "inputs": {"question": "What minimum lighting levels are suggested for bricklaying work and for general access ways on a construction site?"},
        "expectations": {
            "expected_facts": [
                "Typical building work such as bricklaying: 160 lux.",
                "General access ways and stairways: 40 lux.",
            ],
            "expected_source": CONSTRUCTION,
        },
    },

    # ---------------- First aid in the workplace (6) ----------------
    {   # table | p.17-18, Appendix C p.26
        "inputs": {"question": "How many first aiders are recommended per worker in low risk, high risk and remote high risk workplaces?"},
        "expectations": {
            "expected_facts": [
                "Low risk workplaces: one first aider for every 50 workers.",
                "High risk workplaces: one first aider for every 25 workers.",
                "Remote high risk workplaces: one first aider for every 10 workers.",
            ],
            "expected_source": FIRST_AID,
        },
    },
    {   # single fact (two numbers) | p.17
        "inputs": {"question": "How often should first aiders refresh CPR and renew their first aid qualification?"},
        "expectations": {
            "expected_facts": [
                "CPR refresher training should be done annually.",
                "First aid qualifications should be renewed every three years.",
            ],
            "expected_source": FIRST_AID,
        },
    },
    {   # single fact | p.15
        "inputs": {"question": "At what workforce size is a first aid room recommended?"},
        "expectations": {
            "expected_facts": [
                "Low risk workplaces with 200 workers or more.",
                "High risk workplaces with 100 workers or more.",
            ],
            "expected_source": FIRST_AID,
        },
    },
    {   # paraphrase / 'no' answer | p.31
        "inputs": {"question": "Should we keep paracetamol in the office first aid kit?"},
        "expectations": {
            "expected_facts": [
                "No, medication such as paracetamol and aspirin should not be included in first aid kits.",
                "They can cause adverse effects in some people, and their supply may be controlled by drugs and poisons laws.",
            ],
            "expected_source": FIRST_AID,
        },
    },
    {   # single fact | p.13
        "inputs": {"question": "How often should a first aid kit be checked if nobody has used it?"},
        "expectations": {
            "expected_facts": ["Kits should be checked after each use, or at least once every 12 months if not used."],
            "expected_source": FIRST_AID,
        },
    },
    {   # paraphrase (question doesn't say 'AED') | p.14
        "inputs": {"question": "When should a workplace consider getting a defibrillator?"},
        "expectations": {
            "expected_facts": [
                "If there is a risk to workers from electrocution.",
                "If there would be a delay in ambulance services arriving.",
                "Where there are large numbers of members of the public.",
            ],
            "expected_source": FIRST_AID,
        },
    },

    # ---------------- How to manage WHS risks (5) ----------------
    {   # multi-point | p.8
        "inputs": {"question": "What matters must be weighed up when deciding what is 'reasonably practicable'?"},
        "expectations": {
            "expected_facts": [
                "The likelihood of the hazard or risk occurring.",
                "The degree of harm that might result.",
                "Knowledge about the hazard or risk and ways of eliminating or minimising it.",
                "The availability and suitability of ways to eliminate or minimise the risk.",
                "The cost of those ways, including whether the cost is grossly disproportionate to the risk.",
            ],
            "expected_source": RISK,
        },
    },
    {   # multi-point / list | p.18
        "inputs": {"question": "What likelihood ratings does the code suggest for assessing risk?"},
        "expectations": {
            "expected_facts": ["Certain to occur, very likely, possible, unlikely and rare."],
            "expected_source": RISK,
        },
    },
    {   # single fact | p.15
        "inputs": {"question": "Is a risk assessment ever mandatory under the WHS Regulations?"},
        "expectations": {
            "expected_facts": ["Yes, for certain high risk activities such as entry into confined spaces, diving work and live electrical work."],
            "expected_source": RISK,
        },
    },
    {   # paraphrase / reasoning | p.24
        "inputs": {"question": "Can a business choose training and signs instead of an engineering fix just because the engineering fix costs more?"},
        "expectations": {
            "expected_facts": [
                "Cost cannot be used as a reason for adopting controls that rely only on changing people's behaviour when more effective substitution, isolation or engineering controls are available.",
                "If two control measures give the same level of protection and are equally reliable, the less expensive one can be chosen.",
            ],
            "expected_source": RISK,
        },
    },
    {   # worked example (narrative, not a list) | p.33
        "inputs": {"question": "In the council toilet-cleaning example, how was the manual handling risk of carrying the compressor removed?"},
        "expectations": {
            "expected_facts": [
                "A 10-metre hose was attached so the compressor could stay on the truck.",
                "This eliminated lifting and carrying the compressor and also reduced noise in the toilet block.",
                "Handling and storing the long hose was a new risk, so a hose handling system was installed.",
            ],
            "expected_source": RISK,
        },
    },
]

# Questions the documents do not answer. The app should say it doesn't know.
# Scored with the Guidelines 'refuses_out_of_scope' judge, not Correctness.
out_of_scope = [
    {"inputs": {"question": "What is the capital of France?"}},                                   # clearly unrelated
    {"inputs": {"question": "How much annual leave am I entitled to in NSW?"}},                    # employment law, not WHS
    {"inputs": {"question": "What is the maximum fine for a Category 1 offence under the WHS Act?"}},  # WHS topic, but penalties aren't in these codes
    {"inputs": {"question": "How do I lodge a workers' compensation claim after an injury on site?"}},   # related topic, not covered
    {"inputs": {"question": "Who is the current CEO of Safe Work Australia?"}},                     # the publisher, but not in the content
]

assert len(in_scope) == 20 and len(out_of_scope) == 5
