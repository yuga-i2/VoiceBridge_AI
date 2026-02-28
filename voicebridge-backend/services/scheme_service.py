"""
VoiceBridge AI — Scheme Service
Matches farmer profiles and messages to eligible welfare schemes.
Data source: local JSON (mock) or DynamoDB (AWS).
"""

import json
import re
from config.settings import USE_MOCK, DYNAMODB_TABLE_NAME, AWS_REGION
from models.farmer import FarmerProfile

if not USE_MOCK:
    import boto3


def get_all_schemes() -> list[dict]:
    """
    Returns all 10 welfare schemes as list of dicts.
    Mock: reads data/schemes.json
    AWS: scans DynamoDB welfare_schemes table
    """
    if USE_MOCK:
        # Load from local JSON file
        try:
            with open("data/schemes.json", "r", encoding="utf-8") as f:
                schemes = json.load(f)
            return schemes if schemes else []
        except FileNotFoundError:
            raise Exception("data/schemes.json not found. Create schemes.json first.")
        except json.JSONDecodeError:
            raise Exception("data/schemes.json is not valid JSON.")
    else:
        # Load from DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        response = table.scan()
        return response.get("Items", [])


def get_scheme_by_id(scheme_id: str) -> dict | None:
    """
    Returns single scheme dict or None if not found.
    """
    if USE_MOCK:
        with open("data/schemes.json", "r", encoding="utf-8") as f:
            schemes = json.load(f)
        for scheme in schemes:
            if scheme["scheme_id"] == scheme_id:
                return scheme
        return None
    else:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        response = table.get_item(Key={"scheme_id": scheme_id})
        return response.get("Item", None)


def match_schemes_to_message(message: str) -> list[str]:
    """
    Match user message to relevant scheme IDs.
    Comprehensive keyword matching for all 8 schemes in English and Hindi.
    Returns list of matching scheme_ids, always includes at least one match.
    """
    if not message:
        return []
    
    msg = message.lower().strip()
    matched = []
    
    # Comprehensive scheme keywords in English and Hindi
    scheme_keywords = {
        'PM_KISAN': [
            'pm kisan', 'pmkisan', 'pm-kisan', 'kisan samman',
            'pradhan mantri kisan', 'kisaan samman', 'pm kisaan',
            '6000', '₹6000', 'kisan yojana', 'छः हजार',
            'पीएम किसान', 'किसान सम्मान', 'पीएम-किसान', 
            'pradhan mantri kisan samman', 'dbt kisan', 'सम्मान निधि'
        ],
        'KCC': [
            'kcc', 'kisan credit', 'credit card', 'kisan card',
            'crop loan', '4 percent', '4%', 'kharif loan',
            'kisan credit card', 'किसान क्रेडिट', 'केसीसी',
            'क्रेडिट कार्ड', 'loan card', 'kisan loan', 'तीन लाख',
            'fasal loan', 'agricultural loan'
        ],
        'PMFBY': [
            'pmfby', 'fasal bima', 'crop insurance', 'fasal bima yojana',
            'pradhan mantri fasal', 'crop loss', 'bima yojana',
            'fasal insurance', 'फसल बीमा', 'पीएमएफबीवाई',
            'फसल बीमा योजना', 'fasal barbaad', 'crop damage', 
            'kharif bima', 'rabi bima', 'खरीफ बीमा'
        ],
        'MGNREGS': [
            'mgnrega', 'mnrega', 'manrega', 'nrega', '100 days',
            'job card', 'rozgar', 'employment guarantee', 'din kaam',
            'मनरेगा', 'रोजगार', 'जॉब कार्ड', 'sou din', '100 din',
            'काम देना', 'employment scheme', 'rural employment'
        ],
        'AYUSHMAN_BHARAT': [
            'ayushman', 'pmjay', 'health insurance', '5 lakh health',
            'ayushman bharat', 'hospital free', 'free treatment',
            'आयुष्मान', 'स्वास्थ्य बीमा', 'free hospital',
            'आयुष्मान भारत', 'health scheme', 'medical insurance'
        ],
        'PM_AWAS_GRAMIN': [
            'pm awas', 'pmay', 'gramin awas', 'pucca house',
            'house scheme', 'awas yojana', 'housing scheme',
            'ghar yojana', 'आवास योजना', 'पक्का घर',
            'housing', 'home scheme', 'pradhan mantri awas'
        ],
        'SOIL_HEALTH_CARD': [
            'soil health', 'soil card', 'mitti jaanch',
            'fertilizer test', 'soil test', 'मृदा स्वास्थ्य',
            'mitti card', 'krishi card', 'soil fertility'
        ],
        'NFSA_RATION': [
            'ration', 'nfsa', 'public distribution', 'pds',
            'aadhaar ration', 'food grain', 'राशन',
            'खाद्य सुरक्षा', 'distribution scheme'
        ]
    }
    
    # Match keywords in message
    for scheme_id, keywords in scheme_keywords.items():
        for keyword in keywords:
            if keyword in msg:
                if scheme_id not in matched:
                    matched.append(scheme_id)
                break
    
    return matched


def check_eligibility(farmer: FarmerProfile) -> list[dict]:
    """
    Checks ALL 10 schemes against farmer's profile.
    Returns list of eligible scheme dicts with reason_eligible field added.
    """
    schemes = get_all_schemes()
    eligible = []
    
    for scheme in schemes:
        scheme_id = scheme["scheme_id"]
        reason = None
        
        # Eligibility rules per scheme
        if scheme_id == "PM_KISAN":
            if farmer.has_bank_account:
                reason = "You have a bank account, which is required for PM-KISAN direct benefit transfers."
        
        elif scheme_id == "KCC":
            if farmer.has_bank_account:
                reason = "You have a bank account, which is required for KCC loan account operations."
        
        elif scheme_id == "PMFBY":
            if farmer.has_bank_account:
                reason = "You have a bank account, which is required for crop insurance premium deduction."
        
        elif scheme_id == "AYUSHMAN_BHARAT":
            reason = "Ayushman Bharat provides health insurance to all eligible household members."
        
        elif scheme_id == "MGNREGS":
            reason = "MGNREGS provides guaranteed employment to all rural adults seeking work."
        
        elif scheme_id == "SOIL_HEALTH_CARD":
            reason = "All farmers are eligible for free soil testing and crop recommendations."
        
        elif scheme_id == "PM_AWAS_GRAMIN":
            reason = "PM Awas Gramin provides housing subsidy for rural households."
        
        elif scheme_id == "NFSA_RATION":
            reason = "NFSA provides subsidized food grains to priority households."
        
        elif scheme_id == "ATAL_PENSION":
            # APY enrollment closes at age 40
            if farmer.has_bank_account and farmer.age < 40:
                reason = f"You are {farmer.age} years old and have a bank account. APY enrollment must happen before age 40."
            elif farmer.has_bank_account:
                reason = "Your age exceeds the APY enrollment limit (40 years). Consider other pension schemes."
            else:
                continue  # Not eligible
        
        elif scheme_id == "SUKANYA_SAMRIDDHI":
            reason = "Sukanya Samriddhi is available for girl children. Share this with parents who have young daughters."
        
        # Add to eligible list with reason
        if reason:
            scheme_copy = scheme.copy()
            scheme_copy["reason_eligible"] = reason
            eligible.append(scheme_copy)
    
    return eligible


def format_scheme_for_sms(scheme_ids: list[str]) -> str:
    """
    Formats a list of scheme_ids as SMS text.
    Returns formatted SMS with scheme names, documents, apply location, helpline.
    Keeps total under 320 characters where possible.
    """
    schemes = get_all_schemes()
    scheme_dict = {s["scheme_id"]: s for s in schemes}
    
    sms_lines = ["**VoiceBridge - सहायक**"]
    
    for scheme_id in scheme_ids[:3]:  # Limit to 3 schemes per SMS
        if scheme_id in scheme_dict:
            scheme = scheme_dict[scheme_id]
            name_hi = scheme.get("name_hi", "")
            docs = scheme.get("documents", [])
            
            sms_lines.append(f"\n{name_hi}:")
            for i, doc in enumerate(docs[:3], 1):  # Limit to 3 docs
                sms_lines.append(f"{i}. {doc}")
    
    sms_lines.append("\n✓ Sahaya helpline: 1800-123-SAHAYA")
    
    sms_text = "".join(sms_lines)
    
    # Truncate if too long
    if len(sms_text) > 320:
        sms_text = sms_text[:315] + "..."
    
    return sms_text
