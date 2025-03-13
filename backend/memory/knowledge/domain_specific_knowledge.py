"""
Domain-specific knowledge implementations for financial domains.
Contains default knowledge for LBO, M&A, Debt Modeling, and Private Lending.
"""

from typing import Dict, List, Any
import json

class LBOKnowledge:
    """Default knowledge for LBO domain."""
    
    @staticmethod
    def get_default_knowledge() -> List[Dict[str, Any]]:
        """
        Get default LBO knowledge items.
        
        Returns:
            List of knowledge items
        """
        return [
            {
                "title": "LBO Model Structure",
                "content": """
                Leveraged Buyout (LBO) Model Structure:
                
                1. Transaction Assumptions:
                - Purchase Price: Typically expressed as a multiple of EBITDA (e.g., 8-12x)
                - Transaction Fees: Usually 1-2% of enterprise value
                - Financing Fees: 2-4% of debt raised
                
                2. Debt Structure:
                - Senior Secured Debt: 3-4x EBITDA, lower interest rate (L+250-350bps)
                - Second Lien: 1-2x EBITDA, higher interest rate (L+550-750bps)
                - Mezzanine: 1-1.5x EBITDA, highest interest rate (10-12%)
                - Equity Contribution: 30-50% of total enterprise value
                
                3. Financial Projections:
                - Revenue Growth: Industry-specific, typically 3-7% annually
                - EBITDA Margin: Industry-specific, with potential expansion from operational improvements
                - Capital Expenditures: Maintenance (2-3% of revenue) and growth (project-specific)
                - Working Capital: Industry-specific, typically 10-15% of revenue change
                
                4. Exit Assumptions:
                - Exit Multiple: Often similar to entry multiple, sometimes with slight premium (0.5-1.0x)
                - Exit Year: Typically 5 years, range of 3-7 years
                - IRR Target: 20-25% for private equity investors
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "lbo",
                    "topic": "model_structure",
                    "subtopics": ["transaction", "debt", "projections", "exit"]
                }
            },
            {
                "title": "LBO Debt Sizing",
                "content": """
                LBO Debt Sizing Guidelines:
                
                1. Total Leverage Metrics:
                - Total Debt / EBITDA: Typically 5-7x for most industries
                - Higher for stable businesses (6-7x)
                - Lower for cyclical businesses (4-5x)
                
                2. Debt Tranches:
                - Senior Secured: 3-4x EBITDA
                - Second Lien: 1-2x EBITDA
                - Mezzanine/Subordinated: 1-1.5x EBITDA
                
                3. Coverage Ratios:
                - EBITDA / Interest Expense: Minimum 2.0x
                - EBITDA - CapEx / Interest Expense: Minimum 1.5x
                - EBITDA - CapEx / (Interest + Mandatory Amortization): Minimum 1.2x
                
                4. Industry Considerations:
                - Software/Tech: Higher leverage (6-7x) due to recurring revenue
                - Healthcare: Moderate leverage (5-6x) due to stable cash flows
                - Manufacturing: Lower leverage (4-5x) due to cyclicality
                - Retail: Lower leverage (3-4x) due to volatility
                
                5. Debt Repayment:
                - Senior Debt: 1-2% annual amortization plus cash sweep
                - Second Lien: Often bullet maturity (no amortization)
                - Mezzanine: PIK (Payment-in-Kind) interest option
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "lbo",
                    "topic": "debt_sizing",
                    "subtopics": ["leverage", "tranches", "coverage_ratios", "industry_specific"]
                }
            },
            {
                "title": "LBO Returns Analysis",
                "content": """
                LBO Returns Analysis Framework:
                
                1. Key Return Metrics:
                - Internal Rate of Return (IRR): Target 20-25%
                - Multiple of Money (MoM): Target 2.5-3.0x
                - Cash-on-Cash Return: Target 2.5-3.0x
                
                2. Return Drivers:
                - Entry Multiple: Lower entry multiple improves returns
                - Exit Multiple: Higher exit multiple improves returns
                - EBITDA Growth: Operational improvements and revenue growth
                - Debt Paydown: Deleveraging increases equity value
                - Dividend Recapitalization: Potential upside from refinancing
                
                3. Sensitivity Analysis:
                - Exit Multiple: Typically +/- 1.0-2.0x
                - EBITDA Growth: Typically +/- 2-5% annually
                - Debt Paydown: Typically +/- 0.5-1.0x EBITDA annually
                
                4. Investment Period:
                - Typical Hold Period: 5 years (range: 3-7 years)
                - Early Exit Scenario: 3 years
                - Extended Hold Scenario: 7 years
                
                5. Value Creation Breakdown:
                - Multiple Expansion: 20-30% of returns
                - EBITDA Growth: 40-50% of returns
                - Debt Paydown: 20-30% of returns
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "lbo",
                    "topic": "returns_analysis",
                    "subtopics": ["irr", "mom", "drivers", "sensitivity", "value_creation"]
                }
            }
        ]

class MAKnowledge:
    """Default knowledge for M&A domain."""
    
    @staticmethod
    def get_default_knowledge() -> List[Dict[str, Any]]:
        """
        Get default M&A knowledge items.
        
        Returns:
            List of knowledge items
        """
        return [
            {
                "title": "M&A Valuation Methodologies",
                "content": """
                Merger & Acquisition (M&A) Valuation Methodologies:
                
                1. Comparable Company Analysis:
                - Identify publicly traded peers with similar business models
                - Calculate valuation multiples (EV/EBITDA, P/E, EV/Revenue)
                - Apply appropriate discount/premium based on size, growth, and profitability
                
                2. Precedent Transaction Analysis:
                - Identify similar transactions in the industry
                - Calculate transaction multiples paid
                - Consider control premiums (typically 20-30%)
                
                3. Discounted Cash Flow (DCF) Analysis:
                - Project future cash flows (5-10 years)
                - Calculate terminal value (exit multiple or perpetuity growth method)
                - Discount at WACC (typically 8-12% depending on industry)
                
                4. Accretion/Dilution Analysis:
                - Calculate pro forma EPS impact
                - Consider synergies (cost and revenue)
                - Analyze breakeven period for EPS accretion
                
                5. Leveraged Buyout Analysis:
                - Determine maximum purchase price for financial sponsors
                - Calculate implied returns at various purchase prices
                - Assess debt capacity and financing structure
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "ma",
                    "topic": "valuation_methodologies",
                    "subtopics": ["comps", "precedents", "dcf", "accretion_dilution", "lbo"]
                }
            },
            {
                "title": "M&A Synergy Analysis",
                "content": """
                M&A Synergy Analysis Framework:
                
                1. Cost Synergies:
                - Headcount Reduction: Typically 10-30% of overlapping functions
                - Facility Consolidation: Closure of redundant locations
                - Procurement Savings: 1-3% of combined COGS through volume discounts
                - IT Systems: Consolidation of platforms and licenses
                
                2. Revenue Synergies:
                - Cross-Selling: Access to each other's customer base
                - Geographic Expansion: New market entry
                - Product Portfolio Expansion: Complementary offerings
                - Pricing Power: Reduced competition in certain segments
                
                3. Synergy Timing:
                - Cost Synergies: Typically realized within 1-2 years
                - Revenue Synergies: Typically realized within 2-4 years
                - Integration Costs: Typically 1.0-1.5x annual synergies
                
                4. Synergy Valuation:
                - Present Value of Synergies: Discounted at WACC
                - Synergy Sharing: Portion paid to target shareholders (25-50%)
                - Synergy Retention: Portion retained by acquirer (50-75%)
                
                5. Synergy Risks:
                - Execution Risk: Difficulty in achieving projected synergies
                - Cultural Integration: Employee retention and productivity
                - Customer Retention: Potential loss during transition
                - Regulatory Constraints: Antitrust limitations
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "ma",
                    "topic": "synergy_analysis",
                    "subtopics": ["cost_synergies", "revenue_synergies", "timing", "valuation", "risks"]
                }
            },
            {
                "title": "M&A Deal Structures",
                "content": """
                M&A Deal Structure Options:
                
                1. Cash Transaction:
                - Immediate and certain value for target shareholders
                - No continued ownership in combined entity
                - Acquirer bears all synergy risk
                - Tax implications: Capital gains tax for target shareholders
                
                2. Stock Transaction:
                - Target shareholders maintain ownership in combined entity
                - Shared synergy risk and upside
                - Potential tax advantages (tax-free exchange)
                - Relative valuation concerns
                
                3. Mixed Consideration:
                - Combination of cash and stock
                - Balances certainty and continued participation
                - Flexible tax planning opportunities
                - Customizable based on shareholder preferences
                
                4. Earnout Structures:
                - Contingent payments based on future performance
                - Bridges valuation gaps
                - Typically 15-30% of total consideration
                - Measurement period: 1-3 years
                
                5. Collar Arrangements:
                - Protects against stock price volatility
                - Fixed value, fixed exchange ratio, or floating exchange ratio
                - Typically includes upper and lower bounds
                - May include walk-away rights
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "ma",
                    "topic": "deal_structures",
                    "subtopics": ["cash", "stock", "mixed", "earnout", "collar"]
                }
            }
        ]

class DebtKnowledge:
    """Default knowledge for debt modeling domain."""
    
    @staticmethod
    def get_default_knowledge() -> List[Dict[str, Any]]:
        """
        Get default debt modeling knowledge items.
        
        Returns:
            List of knowledge items
        """
        return [
            {
                "title": "Debt Modeling Fundamentals",
                "content": """
                Debt Modeling Fundamentals:
                
                1. Debt Types:
                - Term Loan A: Amortizing bank debt (5-7 year maturity)
                - Term Loan B: Institutional term loan with minimal amortization (7-8 year maturity)
                - Revolving Credit Facility: Flexible borrowing capacity
                - Senior Notes: Unsecured bonds (8-10 year maturity)
                - High Yield Bonds: Below investment grade bonds (8-10 year maturity)
                
                2. Pricing Components:
                - Base Rate: SOFR, EURIBOR, etc.
                - Credit Spread: Based on credit rating and market conditions
                - OID (Original Issue Discount): Upfront discount to par
                - Call Protection: Non-call period and call premiums
                
                3. Amortization Schedules:
                - Term Loan A: 5-10% annual amortization
                - Term Loan B: 1% annual amortization
                - Bonds: Typically bullet maturity (no amortization)
                - Mandatory Prepayments: Excess cash flow sweep, asset sales
                
                4. Covenant Types:
                - Maintenance Covenants: Tested regularly (bank debt)
                - Incurrence Covenants: Tested only when taking specific actions (bonds)
                - Financial Covenants: Leverage ratio, interest coverage, fixed charge coverage
                - Negative Covenants: Restrictions on additional debt, dividends, asset sales
                
                5. Debt Capacity Analysis:
                - Industry Leverage Norms: Varies by sector stability
                - Rating Agency Metrics: Debt/EBITDA, EBITDA/Interest, FCF/Debt
                - Coverage Ratios: EBITDA/Interest, EBITDA-CapEx/Interest
                - Debt Service Capability: FCF/Debt Service
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "debt",
                    "topic": "fundamentals",
                    "subtopics": ["debt_types", "pricing", "amortization", "covenants", "capacity"]
                }
            },
            {
                "title": "Debt Covenant Analysis",
                "content": """
                Debt Covenant Analysis Framework:
                
                1. Leverage Ratio Covenant:
                - Definition: Total Debt / EBITDA
                - Typical Threshold: 3.5-5.5x depending on industry
                - Cushion Analysis: 15-25% headroom to forecast
                - EBITDA Adjustments: Add-backs for non-recurring items
                
                2. Interest Coverage Covenant:
                - Definition: EBITDA / Interest Expense
                - Typical Threshold: 2.0-3.0x
                - Cushion Analysis: 15-25% headroom to forecast
                - Interest Calculation: Cash interest vs. total interest
                
                3. Fixed Charge Coverage Covenant:
                - Definition: EBITDA / (Interest + CapEx + Taxes + Dividends)
                - Typical Threshold: 1.1-1.25x
                - Cushion Analysis: 10-20% headroom to forecast
                - Fixed Charge Definition: Varies by credit agreement
                
                4. Covenant Testing:
                - Testing Frequency: Quarterly for maintenance covenants
                - Cure Rights: Equity cure provisions (typically limited to 2-3 times)
                - Default Scenarios: Technical default vs. payment default
                - Covenant Amendments: Fees and pricing step-ups
                
                5. Covenant-Lite Structures:
                - No Maintenance Covenants: Only incurrence covenants
                - Springing Covenants: Triggered by revolver draw above threshold
                - Covenant Flexibility: EBITDA adjustments, restricted payment baskets
                - Documentation Trends: Increasingly borrower-friendly terms
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "debt",
                    "topic": "covenant_analysis",
                    "subtopics": ["leverage_ratio", "interest_coverage", "fixed_charge", "testing", "covenant_lite"]
                }
            },
            {
                "title": "Debt Refinancing Analysis",
                "content": """
                Debt Refinancing Analysis Framework:
                
                1. Refinancing Economics:
                - Interest Rate Savings: Reduction in weighted average cost of debt
                - Extension of Maturity: Pushing out debt maturities
                - Covenant Relief: Obtaining more flexible covenants
                - Call Premium Consideration: Cost of early redemption
                
                2. Refinancing Methods:
                - Full Refinancing: Replace entire debt structure
                - Partial Refinancing: Replace specific tranches
                - Amendment and Extension: Modify existing facilities
                - Exchange Offer: Swap existing debt for new securities
                
                3. Refinancing Timing:
                - Market Conditions: Interest rate environment
                - Call Protection: End of non-call period
                - Maturity Wall: Approaching maturities
                - Covenant Pressure: Risk of covenant breach
                
                4. Refinancing Analysis:
                - NPV of Interest Savings: Discounted at WACC
                - Transaction Costs: Underwriting fees, legal fees, call premiums
                - Credit Rating Impact: Potential for ratings upgrade/downgrade
                - Covenant Flexibility: Value of covenant relief
                
                5. Refinancing Risks:
                - Market Access Risk: Ability to access capital markets
                - Execution Risk: Pricing and terms uncertainty
                - Investor Appetite: Demand for new issuance
                - Regulatory Considerations: Potential limitations
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "debt",
                    "topic": "refinancing_analysis",
                    "subtopics": ["economics", "methods", "timing", "analysis", "risks"]
                }
            }
        ]

class PrivateLendingKnowledge:
    """Default knowledge for private lending domain."""
    
    @staticmethod
    def get_default_knowledge() -> List[Dict[str, Any]]:
        """
        Get default private lending knowledge items.
        
        Returns:
            List of knowledge items
        """
        return [
            {
                "title": "Private Lending Fundamentals",
                "content": """
                Private Lending Fundamentals:
                
                1. Private Debt Categories:
                - Direct Lending: First-lien senior secured loans to middle market companies
                - Mezzanine Financing: Subordinated debt with equity-like features
                - Distressed Debt: Purchasing debt of troubled companies at a discount
                - Specialty Finance: Asset-based lending, factoring, equipment leasing
                
                2. Key Terms and Structures:
                - Interest Rate: Typically L+400-700bps for senior secured
                - Fees: Origination fee (1-2%), commitment fee, prepayment fee
                - Maturity: 3-7 years for term loans
                - Amortization: Typically 1-5% annually plus cash sweep
                
                3. Security and Collateral:
                - First-Lien: Senior secured against all assets
                - Second-Lien: Junior secured against all assets
                - Asset-Based: Secured against specific assets (inventory, receivables)
                - Unsecured: No specific collateral
                
                4. Covenant Package:
                - Financial Covenants: Leverage ratio, interest coverage, fixed charge coverage
                - Affirmative Covenants: Reporting requirements, compliance certificates
                - Negative Covenants: Limitations on additional debt, dividends, asset sales
                - MAC Clause: Material adverse change provisions
                
                5. Return Expectations:
                - Senior Secured: 6-10% gross returns
                - Unitranche: 8-12% gross returns
                - Mezzanine: 12-18% gross returns
                - Distressed: 15-25% gross returns
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "private_lending",
                    "topic": "fundamentals",
                    "subtopics": ["categories", "terms", "security", "covenants", "returns"]
                }
            },
            {
                "title": "Private Lending Risk Assessment",
                "content": """
                Private Lending Risk Assessment Framework:
                
                1. Credit Risk Analysis:
                - Business Risk: Industry dynamics, competitive position, growth prospects
                - Financial Risk: Leverage, interest coverage, cash flow generation
                - Management Risk: Experience, track record, succession planning
                - Ownership Risk: Sponsor quality, alignment of interests
                
                2. Structural Risk Mitigants:
                - Collateral Coverage: Loan-to-value ratio, collateral quality
                - Covenant Package: Financial covenants, reporting requirements
                - Guarantees: Corporate or personal guarantees
                - Intercreditor Agreements: Rights and remedies among creditors
                
                3. Portfolio Risk Management:
                - Diversification: Industry, geography, borrower concentration
                - Correlation Analysis: Exposure to common risk factors
                - Vintage Analysis: Performance by origination year
                - Stress Testing: Downside scenarios and impact on portfolio
                
                4. Monitoring Framework:
                - Financial Reporting: Quarterly financials, compliance certificates
                - Covenant Compliance: Regular testing of financial covenants
                - Site Visits: Annual management meetings
                - Watch List: Early warning system for troubled credits
                
                5. Workout and Recovery:
                - Early Intervention: Proactive engagement with borrowers
                - Amendment Strategies: Covenant relief, maturity extension
                - Restructuring Options: Debt-for-equity swaps, discounted payoffs
                - Enforcement Actions: Collateral seizure, bankruptcy proceedings
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "private_lending",
                    "topic": "risk_assessment",
                    "subtopics": ["credit_risk", "structural_mitigants", "portfolio_risk", "monitoring", "workout"]
                }
            },
            {
                "title": "Private Lending Returns Calculation",
                "content": """
                Private Lending Returns Calculation Methodology:
                
                1. Yield Metrics:
                - Gross Yield: Contractual interest rate + amortized fees
                - Net Yield: Gross yield - management fees - fund expenses
                - Current Yield: Cash interest / investment amount
                - Yield to Maturity: IRR assuming holding to maturity
                
                2. Fee Components:
                - Origination Fee: Upfront fee at closing (1-2%)
                - Commitment Fee: Fee on undrawn portion (0.5-1.0%)
                - Prepayment Fee: Fee for early repayment (1-3%, declining over time)
                - Amendment Fee: Fee for covenant amendments (0.25-0.5%)
                
                3. Return Calculation Methods:
                - Internal Rate of Return (IRR): Time-weighted return
                - Multiple on Invested Capital (MOIC): Total proceeds / investment
                - Distributed to Paid-In (DPI): Distributions / paid-in capital
                - Residual Value to Paid-In (RVPI): NAV / paid-in capital
                
                4. Loss-Adjusted Returns:
                - Expected Loss Rate: Historical loss experience by credit quality
                - Probability of Default: Based on rating or internal scoring
                - Loss Given Default: Recovery assumptions by collateral type
                - Risk-Adjusted Return: Yield - (probability of default * loss given default)
                
                5. Fund-Level Returns:
                - Gross Fund Return: Asset-level returns before fees
                - Management Fee: Typically 1-2% of invested capital
                - Incentive Fee: Typically 15-20% over hurdle rate
                - Hurdle Rate: Preferred return to investors (6-8%)
                """,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "private_lending",
                    "topic": "returns_calculation",
                    "subtopics": ["yield_metrics", "fees", "calculation_methods", "loss_adjustment", "fund_returns"]
                }
            }
        ]
