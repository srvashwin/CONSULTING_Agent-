# Core consulting frameworks database
# Each framework has: name, description, when to use, structure, example

FRAMEWORKS = [
    {
        "name": "Profitability Framework",
        "type": "strategy",
        "when_to_use": "Analyzing declining profits or identifying profit improvement opportunities",
        "structure": """
Profit = Revenue - Costs
Revenue = Price × Volume
  - Price: pricing power, discounting, mix
  - Volume: market size, market share, frequency
Costs = Fixed Costs + Variable Costs
  - Fixed: overhead, SG&A, depreciation
  - Variable: COGS, materials, labor
Always ask: Is this a revenue problem, cost problem, or both?
        """,
        "example_questions": [
            "Why are our profits declining?",
            "How can we improve margins?",
            "Should we cut costs or grow revenue?",
        ],
    },
    {
        "name": "Market Entry Framework",
        "type": "strategy",
        "when_to_use": "Evaluating whether to enter a new market or launch in a new geography",
        "structure": """
1. Market Attractiveness
   - Size, growth rate, profitability
   - Trends, seasonality, lifecycle stage
2. Competitive Landscape
   - Key players, market shares, concentration
   - Barriers to entry, substitutes
3. Company Capabilities
   - Core competencies, resources, brand
   - Strategic fit with existing business
4. Entry Strategy
   - Organic build vs. acquisition vs. partnership
   - Timing, investment required, expected ROI
        """,
        "example_questions": [
            "Should we enter the Brazilian market?",
            "What's the best way to launch in Southeast Asia?",
            "Should we build, buy, or partner?",
        ],
    },
    {
        "name": "M&A / Due Diligence Framework",
        "type": "m_and_a",
        "when_to_use": "Evaluating an acquisition target or merger opportunity",
        "structure": """
1. Strategic Rationale
   - Why acquire? (market access, capabilities, synergies, elimination)
   - Does this fit our strategy?
2. Target Assessment
   - Financial health: revenue quality, margins, cash flow
   - Market position: share, growth, moat
   - Management quality, culture, retention risk
3. Synergies
   - Cost synergies: headcount, facilities, procurement
   - Revenue synergies: cross-sell, geographic expansion
   - Timeline and feasibility
4. Risks
   - Integration risk, regulatory, cultural
   - Customer concentration, technology risk
   - Valuation risk: are we overpaying?
5. Valuation
   - DCF, comparable companies, precedent transactions
   - Sensitivity analysis
        """,
        "example_questions": [
            "Is Company X a good acquisition target?",
            "What synergies can we realize?",
            "What are the key risks in this deal?",
        ],
    },
    {
        "name": "Porter's Five Forces",
        "type": "strategy",
        "when_to_use": "Assessing industry attractiveness and competitive dynamics",
        "structure": """
1. Threat of New Entrants
   - Capital requirements, economies of scale, switching costs
   - Regulatory barriers, brand loyalty
2. Bargaining Power of Suppliers
   - Concentration, switching costs, uniqueness
   - Forward integration threat
3. Bargaining Power of Buyers
   - Concentration, price sensitivity, switching costs
   - Backward integration threat
4. Threat of Substitutes
   - Price-performance tradeoff, switching costs
   - Propensity to substitute
5. Industry Rivalry
   - Concentration, differentiation, exit barriers
   - Growth rate, fixed costs
        """,
        "example_questions": [
            "How attractive is this industry?",
            "What are the key competitive threats?",
            "Where does the power lie in this value chain?",
        ],
    },
    {
        "name": "Growth-Share Matrix (BCG Matrix)",
        "type": "strategy",
        "when_to_use": "Portfolio analysis and resource allocation across business units",
        "structure": """
Market Growth Rate (Y-axis) vs. Relative Market Share (X-axis)

High Growth + High Share = Stars
  - Invest to maintain/grow
  - May become cash cows

High Growth + Low Share = Question Marks
  - Selective investment or divest
  - Highest risk/reward

Low Growth + High Share = Cash Cows
  - Milk for cash
  - Minimize investment

Low Growth + Low Share = Dogs
  - Divest or liquidate
  - No future potential
        """,
        "example_questions": [
            "How should we allocate capital across business units?",
            "Which products should we invest in vs. divest?",
            "Is our portfolio balanced?",
        ],
    },
    {
        "name": "SWOT Analysis",
        "type": "strategy",
        "when_to_use": "Strategic position assessment at company or product level",
        "structure": """
Internal Factors:
  Strengths: What we do well, unique resources, capabilities
  Weaknesses: Gaps, areas to improve, resource constraints

External Factors:
  Opportunities: Market trends, unmet needs, technological shifts
  Threats: Competitors, regulation, economic headwinds

Strategy: Leverage S+O, mitigate W+O, use S+T, avoid W+T
        """,
        "example_questions": [
            "What is our competitive position?",
            "Where should we focus our strategy?",
            "What are our biggest risks and opportunities?",
        ],
    },
    {
        "name": "MECE Principle (Mutually Exclusive, Collectively Exhaustive)",
        "type": "general",
        "when_to_use": "Structuring any problem or analysis for clarity and completeness",
        "structure": """
Break down a problem into components that:
- MECE: No overlap (Mutually Exclusive)
- MECE: No gaps (Collectively Exhaustive)

Example - Revenue breakdown:
  MECE: Revenue = Product A + Product B + Product C
  (No product counted twice, all products included)

Example - Geography breakdown:
  MECE: Revenue = North America + Europe + APAC + RoW

Common MECE cuts:
  - By product/service line
  - By customer segment
  - By geography/region
  - By channel
  - By time period
        """,
        "example_questions": [
            "Can you structure this problem?",
            "Does this analysis cover everything?",
            "Are we double-counting anywhere?",
        ],
    },
    {
        "name": "3 Horizons of Growth",
        "type": "strategy",
        "when_to_use": "Growth strategy and innovation portfolio planning",
        "structure": """
Horizon 1 (0-12 months): Core Business
  - Defend and extend existing business
  - Incremental innovation, efficiency gains
  - Typically 70-80% of resources

Horizon 2 (1-3 years): Adjacent Growth
  - New products, new geographies, new channels
  - Build on existing capabilities
  - Typically 15-25% of resources

Horizon 3 (3-5+ years): Transformational
  - Disruptive innovation, new business models
  - High risk, high reward
  - Typically 5-10% of resources
        """,
        "example_questions": [
            "What's our growth strategy for the next 5 years?",
            "Are we investing enough in future growth?",
            "Is our innovation pipeline balanced?",
        ],
    },
    {
        "name": "Value Chain Analysis",
        "type": "operations",
        "when_to_use": "Identifying competitive advantage through operational activities",
        "structure": """
Primary Activities:
  1. Inbound Logistics - receiving, warehousing, inventory
  2. Operations - processing, assembly, production
  3. Outbound Logistics - distribution, delivery
  4. Marketing & Sales - pricing, promotion, channels
  5. Service - installation, support, maintenance

Support Activities:
  1. Firm Infrastructure - finance, legal, planning
  2. HR Management - recruiting, training, development
  3. Technology Development - R&D, IT, process improvement
  4. Procurement - purchasing, vendor management

Each activity: assess cost vs. value, identify competitive advantage
        """,
        "example_questions": [
            "Where is value created in our organization?",
            "Which activities should we outsource?",
            "Where can we gain cost advantage?",
        ],
    },
    {
        "name": "7S Framework (McKinsey)",
        "type": "operations",
        "when_to_use": "Organizational effectiveness and change management",
        "structure": """
Hard Elements (Easier to change):
  1. Strategy - plan to build competitive advantage
  2. Structure - reporting lines, hierarchy
  3. Systems - processes, procedures, IT systems

Soft Elements (Harder to change):
  4. Shared Values - core beliefs, culture (center)
  5. Style - management style, leadership approach
  6. Staff - people, demographics, attitudes
  7. Skills - organizational capabilities

All elements must align for effective organization
        """,
        "example_questions": [
            "What's blocking our organizational effectiveness?",
            "How should we restructure?",
            "Will our culture support this strategy?",
        ],
    },
    {
        "name": "Issue Tree / Hypothesis Tree",
        "type": "general",
        "when_to_use": "Breaking down complex problems into testable hypotheses",
        "structure": """
Start with: Key Question

Level 1: 3-5 sub-questions (MECE)
  H1: Hypothesis for sub-question 1
  H2: Hypothesis for sub-question 2
  H3: Hypothesis for sub-question 3

Level 2: Decompose each sub-question further
  H1a, H1b, H1c: Sub-hypotheses

Each hypothesis should be testable with data.
Work top-down: start with hypotheses, then gather data.
        """,
        "example_questions": [
            "How should we approach this ambiguous problem?",
            "What hypotheses should we test first?",
            "What data do we need to validate our thinking?",
        ],
    },
    {
        "name": "Cost-Benefit Analysis Framework",
        "type": "financial",
        "when_to_use": "Evaluating any investment or strategic decision quantitatively",
        "structure": """
1. Identify all costs
   - Upfront investment, ongoing operating costs
   - Opportunity costs, switching costs
   - Intangible costs (morale, brand impact)

2. Identify all benefits
   - Revenue increase, cost savings, efficiency
   - Strategic value, competitive positioning
   - Intangible benefits (brand, learning)

3. Quantify (NPV/IRR)
   - Discounted cash flow analysis
   - Sensitivity analysis on key assumptions
   - Breakeven timeline

4. Decision Rule
   - NPV > 0: proceed
   - Compare IRR to cost of capital
   - Consider non-quantifiable factors
        """,
        "example_questions": [
            "Should we make this investment?",
            "What's the ROI of this initiative?",
            "How long until we break even?",
        ],
    },
]


def get_frameworks_by_type(framework_type: str) -> list:
    return [f for f in FRAMEWORKS if f["type"] == framework_type]


def get_all_frameworks() -> list:
    return FRAMEWORKS


def search_frameworks(query: str) -> list:
    query = query.lower()
    results = []
    for f in FRAMEWORKS:
        searchable = (
            f["name"].lower()
            + f["description"].lower()
            + f["when_to_use"].lower()
            + " ".join(f["example_questions"]).lower()
        )
        if query in searchable:
            results.append(f)
    return results


FRAMEWORK_INDEX = {
    f["name"].lower().replace(" ", "_").replace("/", "_"): f for f in FRAMEWORKS
}
