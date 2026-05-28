import csv
import datetime
import os
import subprocess

from helpers.email import open_email_with_attachment
from helpers.file import *
from helpers.format import *

CLI_JAR = 'cdoc2-cli-1.9.0.jar'

def main():
    if not os.path.exists(CLI_JAR):
        print(f"Error: Cannot find '{CLI_JAR}'.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Encrypt and email documents.")
    parser.add_argument("input_file", nargs='?', help="Path to the file")
    parser.add_argument("-s", '--send-automatically',
                        action='store_true', help="Send email automatically.")
    args = parser.parse_args()

    file_path = get_valid_file_path(args.input_file, ['.csv'])

    file_dir = os.path.dirname(os.path.abspath(file_path))
    result_file_dir = f"{file_dir}/results"
    os.makedirs(result_file_dir, exist_ok=True)

    print_bright_purple("Starting batch encryption...\n")

    encryption_failed_entities = []
    entity_row_count = 0

    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file, delimiter=';')

        print(f"DEBUG: CSV Headers found: {reader.fieldnames}")

        for row_number, row in enumerate(reader, start=2):
            print_bright_purple(f"--- Processing row {row_number - 1} ---")
            clean_row = {k.strip(): v for k, v in row.items()}
            entity_row_count += 1

            name = clean_row.get('asutus', '')
            id_code = clean_row.get('kood', '')
            email = clean_row.get('e-mail', '')

            try:
                print(f"DEBUG: Read name: '{name}', ID: '{id_code}'")

                file_to_encrypt = f"{file_dir}/{name}.xlsx"

                print(f"DEBUG: Encrypting file {file_to_encrypt}")

                if not name or not id_code or not email:
                    print_yellow(
                        f"  -> Skipping Row {row_number}: Missing data. Check .csv delimiter is ';' if no data is read from input file.")
                    continue

                output_file = f"{result_file_dir}/{name.replace(' ', '_')}.cdoc2"
                print_purple(f"  -> Encrypting for {name} ({id_code})...")

                command = [
                    "java",
                    "-jar", CLI_JAR,
                    "create",
                    f"--file={output_file}",
                    f"--recipient={id_code}",
                    file_to_encrypt
                ]

                result = subprocess.run(command, capture_output=True, text=True)

                if result.returncode == 0:
                    print_green(f"  -> Success: {output_file}")
                    open_email_with_attachment(name, email, output_file, args.send_automatically)
                    ##if result.stdout:
                    ##print(f"     Tool Output: {result.stdout.strip()}")
                else:
                    print_orange(f"   -> FAILED (Return Code: {result.returncode})")
                    error_info_lines = [line for line in result.stderr.split('\n') if "[main] INFO" in line]
                    if len(error_info_lines) > 0:
                        print_orange(
                            f"   -> Tool Error:\n      {'\n      '.join(str(err_line) for err_line in error_info_lines)}")
                    else:
                        print_orange(f" -> Tool Error:      {result.stderr}")
                    encryption_failed_entities.append({name, id_code, email})
            except Exception as e:
                print_orange(f" -> Error at row {row_number}: {name}, {id_code}")
                print(e)
                encryption_failed_entities.append({name, id_code, email})

    if len(encryption_failed_entities) == 0:
        print_green(" -> All files encrypted successfully.")
    else:
        if len(encryption_failed_entities) == entity_row_count:
            print_red(
                f"  -> Encryption failed for all entities.")
        elif len(encryption_failed_entities) > 0:
            print_red(
                f"  -> Encryption failed for \n     {'\n      '.join(str(entity).strip('{').strip('}') for entity in encryption_failed_entities)}")

            tz = datetime.timezone(datetime.timedelta(hours=3))
            failed_entities_filename = "{write_dir}/failed-{date:%Y-%m-%d_%H:%M:%S}.csv".format(
                write_dir=result_file_dir, date=datetime.datetime.now(tz=tz))

            with open(failed_entities_filename, 'w') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["asutus", "kood", "e-mail"])
                writer.writerows(encryption_failed_entities)
                print(f"  -> Failed rows written to new document {failed_entities_filename}.")


if __name__ == "__main__":
    main()
