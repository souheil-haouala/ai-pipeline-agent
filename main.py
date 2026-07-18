import json # Make sure to import json at the top of your main.py

def clean_and_validate_yaml(raw_text):
    """
    Cleans the forced JSON response text payload from Google Gemini, 
    validates its structural schema, and outputs perfectly clean, 
    production-ready YAML configuration text onto disk.
    """
    clean_text = raw_text.strip()
    
    # Remove markdown code formatting blocks if present
    clean_text = clean_text.replace("```json", "")
    clean_text = clean_text.replace("```yaml", "")
    clean_text = clean_text.replace("```", "")
    clean_text = clean_text.strip()
        
    try:
        # 1. Parse the forced JSON response data block from the API
        parsed_json_data = json.loads(clean_text)
        
        # 2. Validation structurelle stricte contre le schema GitHub Actions
        validate(instance=parsed_json_data, schema=GITHUB_ACTIONS_SCHEMA)
        
        # 3. TRANSITION: Convert the safe validated dictionary into a clean YAML text string 
        # (sort_keys=False preserves the natural logical sequence order of jobs)
        final_yaml_text = yaml.safe_dump(parsed_json_data, sort_keys=False, default_flow_style=False)
        
        return final_yaml_text
        
    except json.JSONDecodeError as e:
        print(f"\n[SYNTAX ERROR] Failed to parse forced JSON API payload structure: {e}")
        return None
    except ValidationError as e:
        print(f"\n[SCHEMA ERROR] The AI generated an invalid GitHub Actions structure: {e.message}")
        return None
