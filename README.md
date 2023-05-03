## How to run the main
The command that needs to be used has the following format:
+ `-pt` *"path of the table to anonymize"* 
+ `-qi` *"quasi_identifier_1" "qi_2" ... "qi_n"* 
+ `-dgh` *"generalization_table_of_qi_1" "gen_table_qi_2" ... "gen_table_qi_n"*
+ `-k` *"k (int) to use as anonymization criteria"*
+ `-o` *"path+name of the file where to save the anonymized table"*

Example:
`-pt "/Users/alessiadisanto/Desktop/data-protection-project/Database/db_20.csv" -qi "age" "sex" "zip_code" -dgh "/Users/alessiadisanto/Desktop/data-protection-project/Database/age_generalization.csv" "/Users/alessiadisanto/Desktop/data-protection-project/Database/sex_generalization.csv" "/Users/alessiadisanto/Desktop/data-protection-project/Database/zip_code_generalization.csv" -k 5 -o "db_20_5_incognito.csv"`
