# Import Necessary Dependencies
import pandas as pd
from PIL import Image

def extract_from_csv(raw_data, merchant_tags, industry_tags):
  raw_df = pd.read_csv(raw_data)
  merchant_tags_df = pd.read_csv(merchant_tags)
  industry_tags_df = pd.read_csv(industry_tags)
  return raw_df, merchant_tags_df, industry_tags_df

def transform(main_df, brand_keyword_df, industry_tags_df):
    # Create a dictionary to store the mapping from keywords to brands
    brand_keyword_dict = brand_keyword_df.set_index('KEYWORDS ').OUTPUT_BRAND_TAGGING.to_dict()

    # Function to detect brands and industries
    def check_key_partner(merchant_name):
        matches = set()
        parts = merchant_name.split()
        for keyword, brand in brand_keyword_dict.items():
            padded_keyword = ' ' + keyword + ' '
            if padded_keyword in ' ' + merchant_name + ' ':
                matches.add(brand)
        if matches:
            return ', '.join(sorted(matches)), True  # True indicates a brand match was found
        else:
            return ' '.join(parts[:2]) if len(parts) > 1 else parts[0] if parts else "", False

    # Create industry keyword dictionary (this should be done outside the function in a real application)
    keyword_industry_dict = {}

    for _, row in industry_tags_df.iterrows():
        keywords = row['Keywords'].split(',')  # Split the keywords by comma
        for keyword in keywords:
            keyword_upper = keyword.strip().upper()  # Convert to uppercase and strip any whitespace
            keyword_industry_dict[keyword_upper] = row['INDUSTRY']  # Map keyword to industry

    # Function to find industry and keyword from merchant_name
    def find_industry_and_keyword(merchant_name):
        for keyword, industry in keyword_industry_dict.items():
            if keyword in merchant_name:  # Check if the keyword is in the merchant_name
                return industry, keyword
        return "Undefined", "No Keyword Found"  # No match found

    # Standardize the merchant_name entries
    main_df['merchant_name'] = main_df['merchant_name'].astype(str).str.upper().str.strip()
    main_df['merchant_name'] = main_df['merchant_name'].str.replace('-',' ')

    # Apply the function to the merchant_name column and handle the results for brand tagging
    result = main_df['merchant_name'].apply(check_key_partner)
    main_df['Brand Tagging'] = result.apply(lambda x: x[0])
    main_df['Partner Keyword Matched'] = result.apply(lambda x: 'YES' if x[1] else 'NO')

    # Apply the industry keyword detection
    industry_results = main_df['merchant_name'].apply(find_industry_and_keyword)
    main_df['Industry'] = industry_results.apply(lambda x: x[0])
    main_df['Keyword Basis for Industry'] = industry_results.apply(lambda x: x[1])

    return main_df

def load_to_csv(transformed_df, file_name):
  transformed_df.to_csv(file_name, index=False)
  
  