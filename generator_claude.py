import os
import json
import random
import logging
import anthropic

# Set up logging
logging.basicConfig(filename='script.log', level=logging.INFO)

# Initialize the Anthropics client
client = anthropic.Anthropic(
    api_key="",
)

# Function to make objects hashable
def make_hashable(obj):
    if isinstance(obj, dict):
        return frozenset((k, make_hashable(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        return tuple(make_hashable(e) for e in obj)
    else:
        return obj

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Construct the full path to the JSON file
json_file_path = os.path.join(script_dir, "business_variables.json")

# Load business variables from the JSON file
with open(json_file_path, "r") as f:
    business_variables = json.load(f)

def generate_unique_combination(used_combinations):
    while True:
        company_profile = {
            "industry": random.choice(business_variables["company_profile"]["industry"]),
            "size": random.choice(business_variables["company_profile"]["size"]),
            "age": random.choice(business_variables["company_profile"]["age"]),
            "ownership_structure": random.choice(business_variables["company_profile"]["ownership_structure"]),
            "geographic_scope": random.choice(business_variables["company_profile"]["geographic_scope"])
        }

        financial_situation = {
            "profitability": random.choice(business_variables["financial_situation"]["profitability"]),
            "revenue_growth": random.choice(business_variables["financial_situation"]["revenue_growth"]),
            "funding_stage": random.choice(business_variables["financial_situation"]["funding_stage"])
        }

        market_environment = {
            "growth_stage": random.choice(business_variables["market_environment"]["growth_stage"]),
            "competitive_landscape": random.choice(business_variables["market_environment"]["competitive_landscape"]),
            "regulatory_environment": random.choice(business_variables["market_environment"]["regulatory_environment"])
        }

        strategic_focus = {
            "key_strategic_assets": random.choice(business_variables["strategic_focus"]["key_strategic_assets"]),
            "innovation_focus": random.choice(business_variables["strategic_focus"]["innovation_focus"]),
            "main_strategic_challenges": random.sample(business_variables["strategic_focus"]["main_strategic_challenges"], 3)
        }

        leadership_and_culture = {
            "management_team_experience": random.choice(business_variables["leadership_and_culture"]["management_team_experience"]),
            "board_composition": random.choice(business_variables["leadership_and_culture"]["board_composition"]),
            "corporate_culture": random.choice(business_variables["leadership_and_culture"]["corporate_culture"])
        }

        risk_factors = random.sample(business_variables["risk_factors"], 3)

        # Conditional logic to avoid illogical combinations
        if company_profile["ownership_structure"] in ["public", "IPO"]:
            financial_situation["funding_stage"] = "IPO"
        elif company_profile["ownership_structure"] == "private":
            financial_situation["funding_stage"] = random.choice(["pre-seed", "seed", "series A", "series B", "series C+"])

        if company_profile["age"] in ["startup (0-5 years)", "growth (6-10 years)"]:
            company_profile["size"] = random.choice(["small (1-50 employees)", "medium (51-500 employees)"])
        
        if company_profile["size"] in ["enterprise (5000+ employees)"]:
            company_profile["age"] = random.choice(["mature (11-30 years)", "legacy (30+ years)"])

        if financial_situation["profitability"] == "loss-making":
            financial_situation["revenue_growth"] = random.choice(["negative", "stagnant (0-5%)"])

        if market_environment["competitive_landscape"] in ["monopolistic", "duopolistic"]:
            market_environment["growth_stage"] = random.choice(["mature", "declining"])

        combination = {
            "company_profile": company_profile,
            "financial_situation": financial_situation,
            "market_environment": market_environment,
            "strategic_focus": strategic_focus,
            "leadership_and_culture": leadership_and_culture,
            "risk_factors": risk_factors
        }

        combination_frozenset = make_hashable(combination)

        if combination_frozenset not in used_combinations:
            return combination

def generate_question(variables):
    prompt = f"""
You are an experienced business consultant crafting a strategic comprehensive business scenario question based on the following context.  Write the business scenario like a comprehensive, multi-part, longform graduate-level scenario for class discussion and debate:

Company Profile:
- Industry: {variables["company_profile"]["industry"]}
- Size: {variables["company_profile"]["size"]}
- Age: {variables["company_profile"]["age"]}
- Ownership Structure: {variables["company_profile"]["ownership_structure"]}
- Geographic Scope: {variables["company_profile"]["geographic_scope"]}

Financial Situation:
- Profitability: {variables["financial_situation"]["profitability"]}
- Revenue Growth: {variables["financial_situation"]["revenue_growth"]}
- Funding Stage: {variables["financial_situation"]["funding_stage"]}

Market Environment:
- Growth Stage: {variables["market_environment"]["growth_stage"]}
- Competitive Landscape: {variables["market_environment"]["competitive_landscape"]}
- Regulatory Environment: {variables["market_environment"]["regulatory_environment"]}

Strategic Focus:
- Key Strategic Assets: {variables["strategic_focus"]["key_strategic_assets"]}
- Innovation Focus: {variables["strategic_focus"]["innovation_focus"]}
- Main Strategic Challenges: {variables["strategic_focus"]["main_strategic_challenges"]}

Leadership and Culture:
- Management Team Experience: {variables["leadership_and_culture"]["management_team_experience"]}
- Board Composition: {variables["leadership_and_culture"]["board_composition"]}
- Corporate Culture: {variables["leadership_and_culture"]["corporate_culture"]}

Risk Factors:
- {variables["risk_factors"]}

Given the company's unique context and challenges, generate a thought-provoking question that requires the CEO to apply strategic thinking and business judgment.
The question should be focused, relevant, and open-ended to elicit a comprehensive strategic response.
"""
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Debug print to inspect the response structure
    logging.info(f"Response Content (Question): {response.content}")

    # Handle response content based on its structure
    if isinstance(response.content, list):
        if len(response.content) > 0:
            # Extract the 'text' attribute from each TextBlock and join them
            question = ''.join([block.text for block in response.content])
    elif hasattr(response.content, 'text'):
        question = response.content.text
    else:
        question = response.content

    # Ensure question is a string before calling strip
    if isinstance(question, str):
        return question.strip()
    else:
        raise TypeError(f"The response content is not in an expected format: {type(response.content)}")

def generate_answer(question):
    prompt = f"""
Question: {question}
As an experienced CEO, provide a comprehensive, strategic response to the question above, considering the following:
Analyze the key aspects of the situation, including:

- The company's current position, challenges, and objectives
- Relevant industry and market factors, supported by data and benchmarks
- Stakeholder needs and concerns
- Strategic options and tradeoffs, drawing on real-life examples and modern business concepts

For each key aspect, conduct deep analysis:
- Identify pertinent facts and data points
- Contextualize information to surface insights and implications, taking into account the company's unique culture, resources, and constraints
- Evaluate strategic options using established frameworks and criteria, as well as relevant case studies and industry best practices
- Develop actionable recommendations grounded in business principles and adapted to the company's specific context

Synthesize recommendations into a coherent, resilient overall strategy:
- Ensure alignment with company mission and values
- Define priorities balancing short-term and long-term considerations
- Identify risks, dependencies and contingencies, using scenario planning and sensitivity analysis
- Propose a clear execution roadmap and governance model, supported by metrics and milestones

Present the recommendation in a compelling, multilayered narrative:
- Summarize core challenges, decisions and recommendations
- Detail reasoning, linking to overall strategy and supported by data, examples, and visualizations
- Reinforce with relevant case studies, industry benchmarks, and thought leadership insights
- Provide an inspiring vision and pragmatic call-to-action, tailored to the company's unique culture and stakeholder expectations

Be sure to expertly weave between listed points and compelling written clear advice. Prioritize long and detailed written paragraphs, filled with highly relevant wisdom and strategic advice from traditional and modern concepts as well as real-life examples that are similar.
Your answers must be very long-form.
Ground your guidance in the company's unique context, balancing analytical rigor and creative problem-solving to provide unbiased, expert counsel.
"""
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Debug print to inspect the response structure
    logging.info(f"Response Content (Answer): {response.content}")

    # Handle response content based on its structure
    if isinstance(response.content, list):
        if len(response.content) > 0:
            # Extract the 'text' attribute from each TextBlock and join them
            answer = ''.join([block.text for block in response.content])
    elif hasattr(response.content, 'text'):
        answer = response.content.text
    else:
        answer = response.content

    # Ensure answer is a string before calling strip
    if isinstance(answer, str):
        return answer.strip()
    else:
        raise TypeError(f"The response content is not in an expected format: {type(response.content)}")

if __name__ == "__main__":
    num_questions = 20
    generated_questions = []
    qa_pairs = []
    used_combinations = set()

    while len(qa_pairs) < num_questions:
        variable_combination = generate_unique_combination(used_combinations)
        used_combinations.add(make_hashable(variable_combination))

        question = generate_question(variable_combination)
        logging.info(f"Generated Question: {question}")
        
        answer = generate_answer(question)
        logging.info(f"Generated Answer: {answer}")
        
        qa_pairs.append({"question": question, "answer": answer})
        generated_questions.append(question)

    # Append new Q&A pairs to the existing log if it exists
    log_file = "ceo_qa_data.json"

    # Check if the log file exists and load existing data
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Append new Q&A pairs to existing data
    existing_data.extend(qa_pairs)

    # Write the updated data back to the log file
    with open(log_file, "w") as f:
        json.dump(existing_data, f, indent=2)
