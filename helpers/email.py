import platform
import subprocess
import sys
import urllib.parse
import webbrowser
from pathlib import Path

from helpers.format import print_red, print_green, print_yellow, print_purple, print_orange

TEMPLATE_PATH = Path('templates/email-template.txt')
DEFAULT_SUBJECT = "Teie krüpteeritud fail"


def validate_email_template_exists():
    if not Path('templates/email-template.txt').exists():
        print_red(f"Error: Email template file not found.")
        sys.exit(1)


def parse_template(name: str) -> tuple[str, str]:
    try:
        content = TEMPLATE_PATH.read_text(encoding='utf-8').strip()
        subject, body = DEFAULT_SUBJECT, content

        if content.startswith("Subject:"):
            lines = content.splitlines()
            subject = lines[0].replace("Subject:", "", 1).strip()
            body = "\n".join(lines[1:]).strip()

        return subject.replace("{{name}}", name), body.replace("{{name}}", name)
    except FileNotFoundError:
        print_red(f"Error: Email template file not found at {TEMPLATE_PATH}")
        sys.exit(1)


def fallback_to_mailto(email_address: str, subject: str, body: str) -> None:
    print_yellow("  -> Falling back to default system mail client. Please attach files manually before sending.")
    sub_enc, body_enc = urllib.parse.quote(subject), urllib.parse.quote(body)
    webbrowser.open(f"mailto:{email_address}?subject={sub_enc}&body={body_enc}")


def handle_windows_outlook(email_address: str, subject: str, body: str, abs_path: Path, send_immediately: bool) -> bool:
    try:
        import win32com.client as win32
        mail = win32.Dispatch('Outlook.Application').CreateItem(0)
        mail.To, mail.Subject, mail.Body = email_address, subject, body
        mail.Attachments.Add(str(abs_path))
        if send_immediately:
            mail.Send()
            print_green("  -> Email sent via Outlook.")
        else:
            mail.Display()
            print_green("  -> Draft opened in Outlook.")
        print_green(f"  -> Successfully processed via Outlook.")
        return True
    except Exception as e:
        print_red(f"  -> Failed to open Outlook: {e}")
        return False


def handle_mac_applescript(app_name: str, email_address: str, subject: str, body: str, abs_path: Path,
                           send_immediately: bool) -> bool:
    send_clause = 'send newMessage' if send_immediately else ''

    safe_subject = subject.replace('"', '\\"')
    safe_body = body.replace('"', '\\"')

    if app_name == "Mail":
        script = f'''
                tell application "Mail"
                    activate
                    set newMessage to make new outgoing message with properties {{subject:"{safe_subject}", content:"{safe_body}", visible:true}}
                    tell newMessage
                        make new to recipient at end of to recipients with properties {{address:"{email_address}"}}
                        make new attachment with properties {{file name:POSIX file "{abs_path}"}} at after character -1 of content
                    end tell
                    {send_clause}
                end tell
                '''
    else:
        script = f'''
                tell application "Microsoft Outlook"
                    activate
                    set newMessage to make new outgoing message with properties {{subject:"{safe_subject}", content:"{safe_body}", visible:true}}
                    tell newMessage
                        make new to recipient at end of to recipients with properties {{address:"{email_address}"}}
                        make new attachment with properties {{file:POSIX file "{abs_path}"}}
                    end tell
                    {send_clause}
                end tell
                '''

    try:
        print_purple(f"  -> Attempting to open {app_name}...")
        subprocess.run(
            ['osascript'],
            input=script,
            capture_output=True,
            text=True,
            check=True
        )
        print_green(f"  -> Successfully processed request via {app_name}.")
        return True
    except subprocess.CalledProcessError as e:
        print_orange(f"  -> Could not open {app_name}: {e.stderr.strip()}")
        return False


def open_email_with_attachment(recipient_name: str, email_address: str, attachment_path: str,
                               send_immediately: bool = False):
    print(f"DEBUG: Processing encrypted file '{attachment_path}' for '{recipient_name}'")
    abs_path = Path(attachment_path).resolve()

    if not abs_path.exists():
        print_red(f"  -> ERROR: File not found at {abs_path}")
        return

    subject, body = parse_template(recipient_name)
    current_os = platform.system()

    if current_os == "Windows" and handle_windows_outlook(email_address, subject, body, abs_path, send_immediately):
        return
    elif current_os == "Darwin":
        if any(handle_mac_applescript(app, email_address, subject, body, abs_path, send_immediately) for app in
               ["Mail", "Microsoft Outlook"]):
            return
    else:
        print_yellow(f"  -> Native automation not supported on OS: {current_os}")

    fallback_to_mailto(email_address, subject, body)
