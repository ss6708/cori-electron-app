# User Preference System Design for Cori RAG++ System

This document outlines the design of the User Preference System for Cori's RAG++ memory retrieval system, focusing on how user preferences for financial modeling tasks will be captured, stored, and applied.

## 1. Preference System Overview

The User Preference System enables Cori to adapt to individual user preferences across different financial modeling tasks through the following components:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Preference  │    │  Preference  │    │  Preference  │    │  Preference  │
│  Capture     │───►│  Storage     │───►│  Retrieval   │───►│  Application │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
        │                  ▲                   │                   ▲
        │                  │                   │                   │
        ▼                  │                   ▼                   │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Explicit    │    │  Preference  │    │  Context     │    │  Conflict    │
│  & Implicit  │    │  Database    │    │  Matching    │    │  Resolution  │
│  Collection  │    └──────────────┘    └──────────────┘    └──────────────┘
└──────────────┘
```

## 2. Preference Storage Schema

### 2.1 Core Preference Model

The system will use the following core preference model:

```python
{
    "id": "preference_unique_id",
    "user_id": "user_identifier",
    "preference_type": "modeling|analysis|visualization|workflow",
    "domain": "lbo|ma|debt|lending|general",
    "task_context": "specific_task_identifier",
    "preference_data": {
        # Flexible key-value pairs specific to the preference type
    },
    "source": "explicit|implicit|default",
    "confidence": 0.95,  # System confidence in preference (0.0-1.0)
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "last_used": "timestamp",
    "usage_count": 42,
    "priority": 5  # User-defined or system-assigned priority (1-10)
}
```

### 2.2 Preference Categories

The system will organize preferences into four main categories:

#### 2.2.1 Modeling Preferences

Preferences related to financial model structure and assumptions:

```python
{
    "preference_type": "modeling",
    "domain": "lbo",
    "task_context": "debt_sizing",
    "preference_data": {
        "default_senior_debt_multiple": 4.5,
        "default_subordinated_debt_multiple": 1.5,
        "minimum_interest_coverage_ratio": 2.0,
        "debt_amortization_schedule": "2% quarterly",
        "include_revolving_facility": true,
        "revolver_size_calculation": "15% of EBITDA"
    }
}
```

Other modeling preference examples:
- Exit multiple assumptions for different industries
- WACC calculation methodology
- Working capital assumptions
- Capex modeling approach
- Tax rate assumptions

#### 2.2.2 Analysis Preferences

Preferences related to financial analysis methodologies:

```python
{
    "preference_type": "analysis",
    "domain": "ma",
    "task_context": "accretion_dilution",
    "preference_data": {
        "eps_calculation_method": "fully_diluted",
        "synergy_phasing": [0.3, 0.7, 1.0],
        "include_transaction_costs": true,
        "financing_assumptions": {
            "debt_percentage": 60,
            "equity_percentage": 40
        },
        "sensitivity_variables": ["synergy_amount", "interest_rate", "exchange_ratio"],
        "sensitivity_ranges": {
            "synergy_amount": [-20, 20, 5],  # min%, max%, step%
            "interest_rate": [-1, 1, 0.25],  # min%, max%, step%
            "exchange_ratio": [-10, 10, 2.5]  # min%, max%, step%
        }
    }
}
```

Other analysis preference examples:
- Sensitivity analysis parameters
- Scenario definition templates
- Valuation methodology preferences
- Risk assessment frameworks
- Return metric priorities (IRR vs. MOIC vs. Cash-on-Cash)

#### 2.2.3 Visualization Preferences

Preferences related to financial data visualization:

```python
{
    "preference_type": "visualization",
    "domain": "general",
    "task_context": "returns_analysis",
    "preference_data": {
        "preferred_chart_type": "waterfall",
        "color_scheme": "blue_gradient",
        "include_benchmark_comparison": true,
        "benchmark_indices": ["S&P 500", "Industry Average"],
        "chart_elements": {
            "show_data_labels": true,
            "include_grid_lines": false,
            "show_title": true,
            "include_legend": true
        },
        "decimal_precision": 1,
        "percentage_format": "0.0%"
    }
}
```

Other visualization preference examples:
- Chart type preferences for different analyses
- Color schemes for different data types
- Data labeling conventions
- Axis scaling preferences
- Threshold highlighting rules

#### 2.2.4 Workflow Preferences

Preferences related to financial modeling process and workflow:

```python
{
    "preference_type": "workflow",
    "domain": "general",
    "task_context": "model_building",
    "preference_data": {
        "sheet_organization": [
            "cover", "contents", "inputs", "income_statement", 
            "balance_sheet", "cash_flow", "valuation", "sensitivity"
        ],
        "color_coding": {
            "inputs": "#D6E8F6",
            "calculations": "#FFFFFF",
            "outputs": "#EBF1DE"
        },
        "naming_conventions": {
            "input_cells": "inp_[descriptor]",
            "calculation_cells": "calc_[descriptor]",
            "output_cells": "out_[descriptor]"
        },
        "documentation_level": "detailed",  # minimal, standard, detailed
        "formula_complexity": "intermediate"  # simple, intermediate, complex
    }
}
```

Other workflow preference examples:
- Model review checklist items
- Error checking procedures
- Documentation standards
- Formatting conventions
- Modeling sequence preferences

### 2.3 Domain-Specific Preference Collections

The system will maintain specialized preference collections for each financial domain:

#### 2.3.1 LBO Preferences

```python
{
    "domain": "lbo",
    "task_context": "returns_modeling",
    "preference_data": {
        "preferred_exit_timing": [3, 5, 7],  # Years
        "exit_multiple_approach": "entry_multiple_expansion",
        "exit_multiple_expansion": 0.5,  # +0.5x
        "management_equity_percentage": 15,
        "preferred_debt_structure": ["term_loan_a", "term_loan_b", "senior_notes"],
        "minimum_irr_threshold": 20,
        "target_moic": 2.5
    }
}
```

#### 2.3.2 M&A Preferences

```python
{
    "domain": "ma",
    "task_context": "synergy_modeling",
    "preference_data": {
        "revenue_synergy_categories": ["cross_selling", "pricing_power", "market_expansion"],
        "cost_synergy_categories": ["headcount", "facilities", "procurement", "systems"],
        "synergy_realization_timeline": 3,  # Years
        "synergy_probability_factors": {
            "revenue_synergies": 0.7,
            "cost_synergies": 0.9
        },
        "include_one_time_costs": true,
        "one_time_cost_multiple": 1.5  # Multiple of annual synergies
    }
}
```

#### 2.3.3 Debt Modeling Preferences

```python
{
    "domain": "debt",
    "task_context": "covenant_modeling",
    "preference_data": {
        "standard_covenants": [
            "leverage_ratio", "interest_coverage_ratio", 
            "fixed_charge_coverage_ratio", "minimum_liquidity"
        ],
        "covenant_headroom": 30,  # Percentage
        "covenant_testing_frequency": "quarterly",
        "covenant_step_downs": {
            "leverage_ratio": {
                "initial": 6.0,
                "year_1": 5.5,
                "year_2": 5.0,
                "year_3": 4.5
            }
        },
        "default_covenant_actions": ["equity_cure", "waiver_request", "refinancing"]
    }
}
```

#### 2.3.4 Private Lending Preferences

```python
{
    "domain": "lending",
    "task_context": "credit_analysis",
    "preference_data": {
        "key_credit_metrics": [
            "debt_to_ebitda", "interest_coverage", "fixed_charge_coverage",
            "debt_service_coverage", "loan_to_value"
        ],
        "industry_risk_adjustments": {
            "cyclical_industries": 1.2,  # Multiplier for risk assessment
            "defensive_industries": 0.8
        },
        "collateral_haircuts": {
            "accounts_receivable": 20,  # Percentage
            "inventory": 30,
            "machinery_equipment": 50,
            "real_estate": 25
        },
        "default_probability_model": "z_score",  # z_score, kMV, internal_rating
        "recovery_rate_assumptions": {
            "senior_secured": 70,  # Percentage
            "senior_unsecured": 50,
            "subordinated": 30
        }
    }
}
```

## 3. Preference Capture Mechanisms

### 3.1 Explicit Preference Collection

The system will capture explicit preferences through:

#### 3.1.1 Direct Preference Statements

The system will parse natural language preference statements:

```
"Always use a WACC of 10% for retail companies"
"I prefer to use monthly compounding for IRR calculations"
"For LBO models, use 6.0x entry multiple and 7.0x exit multiple for software companies"
"When modeling debt, always include a revolving credit facility sized at 15% of EBITDA"
```

Implementation approach:
- Pattern matching for common preference expressions
- Structured extraction of preference parameters
- Domain and task classification
- Preference data formatting

#### 3.1.2 Preference Configuration Interface

A structured interface for setting preferences:

- Category-based preference organization
- Domain-specific preference templates
- Preset preference packages
- Preference import/export
- Priority assignment controls

#### 3.1.3 Guided Preference Collection

Interactive preference collection through:

- Preference questionnaires for new users
- Progressive preference refinement
- Task-specific preference prompts
- Preference validation dialogues

### 3.2 Implicit Preference Learning

The system will infer preferences from:

#### 3.2.1 Correction Analysis

Learning from user corrections:

```
User: "Update the model to use straight-line depreciation instead of accelerated depreciation"
System: [Makes the change]
[System infers preference: Use straight-line depreciation as default]
```

Implementation approach:
- Identify correction patterns
- Extract preference implications
- Assign confidence scores to inferred preferences
- Confirm high-impact preferences with user

#### 3.2.2 Usage Pattern Analysis

Learning from repeated behaviors:

- Track modeling patterns across sessions
- Identify consistent parameter choices
- Detect manual overrides of system defaults
- Analyze formula modification patterns

#### 3.2.3 Feedback Integration

Learning from explicit and implicit feedback:

- Analyze positive and negative feedback
- Correlate feedback with specific modeling approaches
- Extract preference signals from comparative feedback
- Incorporate satisfaction metrics

### 3.3 Preference Validation

The system will validate preferences through:

- Consistency checking with existing preferences
- Domain-specific validation rules
- Confirmation for high-impact preferences
- Periodic preference review prompts

## 4. Preference Retrieval and Application

### 4.1 Context-Based Preference Matching

The system will retrieve relevant preferences based on:

#### 4.1.1 Task Context Matching

Match preferences to the current financial task:

- Identify the specific financial task being performed
- Match task to relevant preference contexts
- Consider task hierarchy (general to specific)
- Apply task-specific preference filters

#### 4.1.2 Domain Context Matching

Match preferences to the financial domain:

- Identify the financial domain of the current task
- Retrieve domain-specific preferences
- Apply cross-domain preferences where appropriate
- Handle multi-domain scenarios

#### 4.1.3 Temporal Context Matching

Consider temporal factors in preference retrieval:

- Prioritize recently used preferences
- Consider preference recency for similar tasks
- Apply time-sensitive preferences (e.g., fiscal year conventions)
- Track preference evolution over time

### 4.2 Preference Ranking and Selection

The system will prioritize preferences using:

#### 4.2.1 Multi-Factor Ranking

Rank preferences based on multiple factors:

```python
def rank_preferences(preferences, context):
    ranked_preferences = []
    
    for pref in preferences:
        # Calculate base score
        score = 0
        
        # Priority factor (0-10 scale, weighted heavily)
        score += pref["priority"] * 10
        
        # Recency factor (days since last used, inverse relationship)
        days_since_used = (datetime.now() - pref["last_used"]).days
        recency_score = max(10 - (days_since_used / 30), 0)  # Max 10, decays over 300 days
        score += recency_score * 5
        
        # Usage count factor (normalized to 0-10 scale)
        usage_score = min(pref["usage_count"] / 10, 10)
        score += usage_score * 3
        
        # Confidence factor (0-1 scale)
        score += pref["confidence"] * 10
        
        # Context specificity bonus
        if pref["task_context"] == context["current_task"]:
            score += 30
        elif context["current_task"].startswith(pref["task_context"]):
            score += 15
        
        # Domain specificity bonus
        if pref["domain"] == context["current_domain"]:
            score += 20
        elif pref["domain"] == "general":
            score += 5
        
        # Source type bonus
        if pref["source"] == "explicit":
            score += 15
        elif pref["source"] == "implicit":
            score += 5
        
        ranked_preferences.append((pref, score))
    
    # Sort by score descending
    ranked_preferences.sort(key=lambda x: x[1], reverse=True)
    
    return [pref for pref, score in ranked_preferences]
```

#### 4.2.2 Preference Filtering

Filter preferences based on applicability:

- Remove outdated preferences
- Filter out low-confidence preferences
- Exclude preferences with negative feedback
- Apply minimum relevance thresholds

### 4.3 Preference Application

The system will apply preferences through:

#### 4.3.1 Prompt Augmentation

Inject preferences into system prompts:

```python
def create_system_prompt_with_preferences(base_prompt, preferences):
    prompt_with_preferences = base_prompt + "\n\nPlease consider the following user preferences:\n"
    
    for pref in preferences:
        if pref["preference_type"] == "modeling":
            prompt_with_preferences += f"\n- For {pref['domain']} {pref['task_context']}, use these modeling parameters:\n"
            for key, value in pref["preference_data"].items():
                prompt_with_preferences += f"  - {key.replace('_', ' ').title()}: {value}\n"
        
        elif pref["preference_type"] == "analysis":
            prompt_with_preferences += f"\n- When performing {pref['task_context']} analysis, follow these guidelines:\n"
            for key, value in pref["preference_data"].items():
                prompt_with_preferences += f"  - {key.replace('_', ' ').title()}: {value}\n"
        
        # Add other preference types...
    
    return prompt_with_preferences
```

#### 4.3.2 Tool Parameter Configuration

Configure financial tools based on preferences:

- Set default parameters for financial calculations
- Configure visualization settings
- Adjust workflow sequences
- Set validation thresholds

#### 4.3.3 Response Filtering

Filter and adjust responses based on preferences:

- Format outputs according to preferences
- Adjust detail level based on preferences
- Prioritize information based on user interests
- Apply terminology preferences

## 5. Preference Conflict Resolution

### 5.1 Conflict Detection

The system will detect preference conflicts through:

- Direct contradiction identification
- Parameter range conflicts
- Methodology incompatibilities
- Cross-domain inconsistencies

### 5.2 Resolution Strategies

The system will resolve conflicts using:

#### 5.2.1 Priority-Based Resolution

Resolve conflicts based on preference priority:

- Use explicitly assigned priority levels
- Apply source-based priority (explicit > implicit > default)
- Consider recency as a priority factor
- Use confidence scores as tiebreakers

#### 5.2.2 Specificity-Based Resolution

Resolve conflicts based on specificity:

- Task-specific preferences override general preferences
- Domain-specific preferences override cross-domain preferences
- Concrete parameters override methodological preferences
- Detailed preferences override high-level preferences

#### 5.2.3 Hybrid Resolution

Combine multiple resolution strategies:

```python
def resolve_preference_conflicts(conflicting_preferences, context):
    # Group conflicts by parameter
    conflict_groups = {}
    
    for pref in conflicting_preferences:
        for key in pref["preference_data"].keys():
            if key not in conflict_groups:
                conflict_groups[key] = []
            conflict_groups[key].append(pref)
    
    # Resolve each conflict group
    resolved_preferences = {}
    
    for key, conflicts in conflict_groups.items():
        if len(conflicts) == 1:
            # No conflict for this parameter
            resolved_preferences[key] = conflicts[0]["preference_data"][key]
            continue
        
        # Calculate resolution score for each conflicting preference
        scored_conflicts = []
        
        for pref in conflicts:
            score = 0
            
            # Priority factor
            score += pref["priority"] * 10
            
            # Recency factor
            days_since_updated = (datetime.now() - pref["updated_at"]).days
            recency_score = max(10 - (days_since_updated / 30), 0)
            score += recency_score * 7
            
            # Specificity factor
            if pref["task_context"] == context["current_task"]:
                score += 30
            elif context["current_task"].startswith(pref["task_context"]):
                score += 15
            
            if pref["domain"] == context["current_domain"]:
                score += 20
            
            # Source factor
            if pref["source"] == "explicit":
                score += 25
            elif pref["source"] == "implicit":
                score += 10
            
            # Confidence factor
            score += pref["confidence"] * 15
            
            scored_conflicts.append((pref, score))
        
        # Select preference with highest score
        winner = max(scored_conflicts, key=lambda x: x[1])
        resolved_preferences[key] = winner[0]["preference_data"][key]
    
    return resolved_preferences
```

### 5.3 User Involvement

The system will involve users in conflict resolution when:

- High-impact conflicts are detected
- Multiple high-priority preferences conflict
- Confidence in automated resolution is low
- New preference would override frequently used preference

Implementation approach:
- Present conflict explanation
- Offer resolution options
- Allow temporary or permanent resolution
- Provide impact assessment of each option

## 6. Preference Management

### 6.1 Preference Lifecycle Management

The system will manage preferences throughout their lifecycle:

#### 6.1.1 Creation and Validation

Process for adding new preferences:

- Preference extraction and formatting
- Validation against domain rules
- Conflict checking with existing preferences
- Initial confidence and priority assignment

#### 6.1.2 Update and Evolution

Process for updating preferences:

- Incremental confidence adjustment
- Usage statistics tracking
- Periodic relevance assessment
- Version history maintenance

#### 6.1.3 Archiving and Pruning

Process for removing outdated preferences:

- Automatic archiving of unused preferences
- Consolidation of similar preferences
- Removal of consistently overridden preferences
- Preference backup before removal

### 6.2 Preference Portability

The system will support preference portability through:

- Preference export in standard formats
- Preference import from external sources
- Preference sharing between users
- Preference templates for common scenarios

### 6.3 Preference Analytics

The system will provide insights through:

- Preference usage statistics
- Preference effectiveness metrics
- Preference conflict reports
- Preference gap analysis

## 7. Implementation Considerations

### 7.1 Required Dependencies

```python
# Python dependencies for preference system
chromadb==0.4.18
pydantic==2.5.2
python-dotenv==1.0.0
sqlalchemy==2.0.23  # For structured preference storage
redis==5.0.1  # For preference caching
```

### 7.2 Directory Structure

```
backend/
├── preference_system/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── preference.py
│   ├── capture/
│   │   ├── __init__.py
│   │   ├── explicit_collector.py
│   │   ├── implicit_collector.py
│   │   └── preference_validator.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── preference_store.py
│   │   └── preference_cache.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── context_matcher.py
│   │   ├── preference_ranker.py
│   │   └── conflict_resolver.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── prompt_enhancer.py
│   │   ├── tool_configurator.py
│   │   └── response_filter.py
│   └── management/
│       ├── __init__.py
│       ├── lifecycle_manager.py
│       ├── preference_exporter.py
│       └── preference_analytics.py
```

## 8. Integration with Existing Codebase

### 8.1 OpenAI Handler Integration

The preference system will integrate with the existing OpenAI handler:

```python
# Pseudocode for integration with OpenAI handler
def enhanced_get_completion_with_preferences(self, messages: List[Message], model: Optional[str] = None) -> Message:
    # Extract the latest user query
    user_query = messages[-1].content if messages[-1].role == "user" else None
    
    if user_query:
        # Get conversation context
        conversation_context = self._extract_conversation_context(messages)
        
        # Get Excel context if available
        excel_context = self._get_excel_context()
        
        # Determine current task and domain context
        context = {
            "current_task": self._detect_financial_task(user_query, conversation_context),
            "current_domain": self._detect_financial_domain(user_query, conversation_context, excel_context)
        }
        
        # Retrieve relevant preferences
        preferences = self.preference_system.retrieve_preferences(
            user_id=self.user_id,
            context=context
        )
        
        # Resolve any preference conflicts
        resolved_preferences = self.preference_system.resolve_conflicts(
            preferences=preferences,
            context=context
        )
        
        # Create system message with preferences
        system_message = self._create_system_message_with_preferences(
            base_prompt=self.base_system_prompt,
            preferences=resolved_preferences
        )
        
        # Add system message to the beginning of the messages
        augmented_messages = [system_message] + messages
    else:
        augmented_messages = messages
    
    # Call the original method with augmented messages
    response = self.client.chat.completions.create(
        model=model or self.model,
        messages=[msg.to_openai_format() for msg in augmented_messages],
        temperature=0.7,
        max_tokens=1024
    )
    
    # Capture implicit preferences from the interaction
    self.preference_system.capture_implicit_preferences(
        user_query=user_query,
        response=response,
        context=context
    )
    
    return Message.from_openai_response(response)
```

### 8.2 API Endpoints

New API endpoints will be added to the Flask server:

```python
# Pseudocode for new API endpoints

@app.route('/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences."""
    try:
        user_id = request.args.get('user_id')
        domain = request.args.get('domain')
        task_context = request.args.get('task_context')
        
        if not user_id:
            return jsonify({"error": "User ID is required."}), 400
        
        # Get preferences
        preferences = preference_system.get_preferences(
            user_id=user_id,
            domain=domain,
            task_context=task_context
        )
        
        return jsonify({"preferences": [pref.to_dict() for pref in preferences]})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/preferences', methods=['POST'])
def add_preference():
    """Add a new user preference."""
    try:
        data = request.json
        
        if not data or 'user_id' not in data or 'preference_data' not in data:
            return jsonify({"error": "Invalid request. 'user_id' and 'preference_data' fields are required."}), 400
        
        # Add preference
        preference = preference_system.add_preference(
            user_id=data['user_id'],
            preference_type=data.get('preference_type', 'general'),
            domain=data.get('domain', 'general'),
            task_context=data.get('task_context', 'general'),
            preference_data=data['preference_data'],
            source=data.get('source', 'explicit'),
            priority=data.get('priority', 5)
        )
        
        return jsonify({"message": "Preference added successfully", "preference": preference.to_dict()})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/preferences/<preference_id>', methods=['PUT'])
def update_preference(preference_id):
    """Update an existing user preference."""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Invalid request. Request body is required."}), 400
        
        # Update preference
        preference = preference_system.update_preference(
            preference_id=preference_id,
            updates=data
        )
        
        return jsonify({"message": "Preference updated successfully", "preference": preference.to_dict()})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/preferences/<preference_id>', methods=['DELETE'])
def delete_preference(preference_id):
    """Delete a user preference."""
    try:
        # Delete preference
        preference_system.delete_preference(preference_id=preference_id)
        
        return jsonify({"message": "Preference deleted successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/preferences/extract', methods=['POST'])
def extract_preferences():
    """Extract preferences from natural language statement."""
    try:
        data = request.json
        
        if not data or 'statement' not in data or 'user_id' not in data:
            return jsonify({"error": "Invalid request. 'statement' and 'user_id' fields are required."}), 400
        
        # Extract preferences
        preferences = preference_system.extract_preferences_from_statement(
            user_id=data['user_id'],
            statement=data['statement'],
            context=data.get('context', {})
        )
        
        return jsonify({
            "message": "Preferences extracted successfully", 
            "preferences": [pref.to_dict() for pref in preferences]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## 9. Conclusion

This user preference system design provides a comprehensive framework for capturing, storing, retrieving, and applying user preferences in Cori's RAG++ system. By understanding and adapting to individual user preferences across different financial domains and tasks, Cori will be able to provide a more personalized and effective financial modeling experience.
