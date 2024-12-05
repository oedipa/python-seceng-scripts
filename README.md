# python-seceng-scripts
A collection of scripts I've written over time to help with tooling or tasks

Scripts:

1. pan-scan.py - This is a script I wrote to scan Firestore DBs in GCP for finding Credit Cards or PAN numbers.  I saw a few variations in a DB and based the regexes off of those. Adjust the regexes for your patterns.
   
2. gcp_users_groups_report.py - This scans all Projects in GCP for Groups and Users and Service Accounts.  The info is flattened.  Helpful for audits.

3. semgrep_github.py - This will take the open sourse standalone Semgrep and run a rule set against all repos in a GH Org.

4. gcp_iam_policies.py -  Scan GCP organization for policies

5. cert_alert.py - alert on a domain with expiring certs

6. cert_details - get details on certs in a domain
