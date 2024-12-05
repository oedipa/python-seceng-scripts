import firebase_admin
from firebase_admin import credentials, firestore
import json
import re

# Initialize the Firebase Admin SDK
cred = credentials.ApplicationDefault()  # Assumes the environment is set up for SSO or ADC
firebase_admin.initialize_app(cred)

# Reference to the Firestore collection and document
db = firestore.client()
doc_ref = db.collection('your-collection').document('doc-name').collection('another-collection')

# Define regex patterns for the PAN/CC formats
regex_patterns = {
    "Full 16-digit PANs": r'^\d{16}$',
    "Masked PANs (with Xs)": r'^\d{4}X{6}\d{4}$',
    "13-digit PANs": r'^\d{13}$',
    "4-digit PANs": r'^\d{4}$',
    "Masked PANs (with underscores)": r'^\d{6}[_]{6}\d{4}$'
}

# Initialize counters for each pattern
pattern_counts = {description: 0 for description in regex_patterns.keys()}
empty_pan_count = 0
no_match_count = 0

# Prepare the results list
results = []

# Fetch the documents from the collection
#docs = doc_ref.limit(1).stream()  # Limit to one document for testing
docs = doc_ref.stream()

# Process each document and check the 'pan' field inside the 'card' object
for doc in docs:
    doc_data = doc.to_dict()
    
    # Access the 'pan' field within the nested 'card' object
    pan = doc_data.get('another-collection', {}).get('pan', '').strip()

    if not pan:  # Check if the PAN is empty or missing
        empty_pan_count += 1
        continue
    
    matched = False
    for description, pattern in regex_patterns.items():
        if re.match(pattern, pan):
            #print(f"PAN matched pattern: {description}")
            pattern_counts[description] += 1
            matched = True
            break  # Stop after the first match
    
    if not matched:  # If no patterns matched
        no_match_count += 1

    #testing
   # results.append({
   #     "document_id": doc.id,
   #     "matched_pattern": description if matched else "No Match"
    #})

# Compile the final results including counts for each pattern
final_results = {
    "results": results,
    "summary": {
        "Full 16-digit PANs": pattern_counts["Full 16-digit PANs"],
        "Masked PANs (with Xs)": pattern_counts["Masked PANs (with Xs)"],
        "13-digit PANs": pattern_counts["13-digit PANs"],
        "4-digit PANs": pattern_counts["4-digit PANs"],
        "Masked PANs (with underscores)": pattern_counts["Masked PANs (with underscores)"],
        "empty_pan_count": empty_pan_count,
        "no_match_count": no_match_count,
        "total_processed": len(results) + empty_pan_count
    }
}

# Write the results to a JSON file
output_file = "pan_counts.json"
with open(output_file, 'w') as json_file:
    json.dump(final_results, json_file, indent=4)

print(f"Results and counts written to {output_file}")
print("Summary of counts:")
print(json.dumps(final_results['summary'], indent=4))