import os
import platform
import subprocess
import sys

from helpers.format import print_red, print_green, print_yellow, print_purple


def validate_email_template_exists():
    if not os.path.exists('templates/email-template.txt'):
        print_red(f"Error: Email template file not found.")
        sys.exit(1)


def get_email_body(name):
    try:
        with open('templates/email-template.txt', 'r', encoding='utf-8') as f:
            template = f.read()
            return template.replace("{{name}}", name)
    except FileNotFoundError:
        return ''


def open_email_with_attachment(recipient_name, email_address, attachment_path, send_immediately=False):
    print(f"DEBUG: Sending encrypted file '{attachment_path}' to '{recipient_name}', email: '{email_address}'")

    abs_path = os.path.abspath(attachment_path)
    if not os.path.exists(abs_path):
        print(f"  -> ERROR: File not found at {abs_path}")
        return

    subject = "Teie krüpteeritud fail"
    body = get_email_body(recipient_name)
    safe_body = body.replace('"', '\\"')

    if platform.system() == "Windows":
        try:
            import win32com.client as win32
            outlook = win32.Dispatch('Outlook.Application')
            mail = outlook.CreateItem(0)
            mail.To = email_address
            mail.Subject = subject
            mail.Body = body
            mail.Attachments.Add(abs_path)
            if send_immediately:
                mail.Send()
                print_green("  -> Email sent via Outlook (Windows).")
            else:
                mail.Display()
                print_green("  -> Draft opened in Outlook.")
        except Exception as e:
            print_red(f"  -> Failed to open Outlook: {e}")

    elif platform.system() == "Darwin":

        applescript_action = "send newMessage" if send_immediately else ""

        scripts = {
            "Mail": f'''
                    tell application "Mail"
                        set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{safe_body}", visible:true}}
                        tell newMessage
                            make new to recipient at end of to recipients with properties {{address:"{email_address}"}}
                            tell content
                                make new attachment with properties {{file name:(POSIX file "{abs_path}")}} at after last paragraph
                            end tell
                        end tell
                        activate
                        {applescript_action}
                    end tell
                ''',

            "Microsoft Outlook": f'''
                    tell application "Microsoft Outlook"
                        set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{safe_body}", visible:true}}
                        tell newMessage
                            make new to recipient at end of to recipients with properties {{address:"{email_address}"}}
                            make new attachment with properties {{file name:(POSIX file "{abs_path}")}}
                        end tell
                        activate
                        {applescript_action}
                    end tell
                '''

        }

        success = False

        for app_name, script in scripts.items():
            try:
                print_purple(f"  -> Attempting to open {app_name}...")

                subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)

                print_green(f"  -> Successfully processed request via {app_name}.")
                success = True
                break

            except subprocess.CalledProcessError as e:
                print_yellow(f"  -> Could not open {app_name}: {e.stderr.strip()}")

            except Exception as e:
                print_yellow(f"  -> Failed to communicate with {app_name}: {e}")

            if not success:
                print_red("  -> ERROR: Could not open either Mail or Microsoft Outlook.")
    else:
        print_red(f"  -> OS {platform.system()} not supported.")
