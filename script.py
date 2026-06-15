import csv
import datetime
import subprocess

from helpers.email import open_email_with_attachment, validate_email_template_exists
from helpers.file import *
from helpers.format import *

CLI_JAR = Path('cdoc2-cli-1.9.0.jar')


def main():
    if not CLI_JAR.exists():
        print(f"Error: Cannot find '{CLI_JAR}'.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Encrypt and email documents.")
    parser.add_argument("input_file", nargs='?', help="Path to the file")
    parser.add_argument("-s", '--send-automatically',
                        action='store_true', help="Send email automatically.")
    args = parser.parse_args()

    if args.send_automatically:
        validate_email_template_exists()

    file_path = Path(get_valid_file_path(args.input_file, ['.csv']))

    file_dir = file_path.resolve().parent
    result_file_dir = file_dir / "results"
    result_file_dir.mkdir(parents=True, exist_ok=True)

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

                file_to_encrypt = file_dir / f"{name}.xlsx"

                print(f"DEBUG: Encrypting file {file_to_encrypt}")

                if not name or not id_code or not email:
                    print_yellow(
                        f"  -> Skipping Row {row_number}: Missing data. Check .csv delimiter is ';' if no data is read from input file.")
                    continue

                output_file = result_file_dir / f"{name.replace(' ', '_')}.cdoc2"
                print_purple(f"  -> Encrypting for {name} ({id_code})...")

                try:
                    output_file.unlink(missing_ok=True)
                except FileNotFoundError:
                    pass

                command = [
                    "java",
                    "-jar", str(CLI_JAR),
                    "create",
                    f"--file={output_file}",
                    f"--recipient={id_code}",
                    str(file_to_encrypt)
                ]

                result = subprocess.run(command, capture_output=True, text=True)

                if result.returncode == 0:
                    print_green(f"  -> Success: {output_file}")
                    open_email_with_attachment(name, email, str(output_file), args.send_automatically)
                    # if result.stdout:
                    # print(f"     Tool Output: {result.stdout.strip()}")
                else:
                    if result.stdout:
                        print(f"     Tool Output: {result.stdout.strip()}")
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
        print_green("All files encrypted successfully.")
        return

    if len(encryption_failed_entities) == entity_row_count:
        print_red("Encryption failed for all entities.")
    else:
        print_red(
            f"  -> Encryption failed for \n     {'\n      '.join(str(entity).strip('{').strip('}') for entity in encryption_failed_entities)}")

        tz = datetime.timezone(datetime.timedelta(hours=3))
        failed_entities_filename = result_file_dir / "failed-{date:%Y-%m-%d_%H-%M-%S}.csv".format(
            date=datetime.datetime.now(tz=tz))

        with open(failed_entities_filename, 'w') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(["asutus", "kood", "e-mail"])
            writer.writerows(encryption_failed_entities)
            print(f"  -> Failed rows written to new document {failed_entities_filename}.")


if __name__ == "__main__":
    main()
