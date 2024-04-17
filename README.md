# booking-email-sender

This is used for sending emails to book gigs.

[[_TOC_]]

## Run the tool

Command line to execute and checks what will be done:

```shell
./send-email.py \
  --csv "path_to_my_csv_file" \
  --template "my_template_name"
```

To actually send email, add the `--send` parameter:

```shell
./send-email.py \
  --csv "path_to_my_csv_file" \
  --template "my_template_name" \
  --send
```

## Supported environment variables

| Variable Name   | Default            |
|-----------------|--------------------|
| LOG_LEVEL       | `logging.info` [1] |
| SMTP_HOST       | `smtp.gmail.com`   |
| SMTP_PORT       | `465`              |
| SMTP_USER       | `None`             |
| SMTP_PASSWORD   | `None`             |

Notes:

- [1] See level numerical values here from the Python [logging](
  https://docs.python.org/3/library/logging.html#logging-levels) module

## Format of CSV file

The CSV file should be of the following format at minimal:

```csv
email,name
text@example.com,Test User
```

Those attributes could then be used in templates directly.

## Create a new template

Create a new directory in the `templates` directory. Let's assume it is called
`template_test`

Create the required files in that new directory:

- `templates/template_test/email.html`
- `templates/template_test/email.txt`
- `templates/metadata.json`

In the template files, you can use any CSV field by using the following
syntax: `{{csv_field_name}}`. The tool will automatically replace this tag
by the right values from the corresponding CSV field found in the CSV 
file.

## Convert EML file to HTML for creating a new template

Use the following tool:
https://pypi.org/project/eml-to-html/
