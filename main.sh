#bash pull.sh
curl -L "https://docs.google.com/spreadsheets/export?id=11iBubDlDrAGGvd3FkuSlBQxRvhoF4__BD32fS4AwsVE&exportFormat=tsv" --output test.tsv
pollstring="$(python3 parse.py)"
echo "{"text":\"${pollstring}\"}"
curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"${pollstring}\"}" https://hooks.slack.com/services/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
