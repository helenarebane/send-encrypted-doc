# Setup for dummies

### Install Java (for CDOC)

Download and install the
JDK https://adoptium.net/en-GB/temurin/releases?os=any&version=21&package=jdk&mode=filter&arch=any.

### Install Python

Download from https://www.python.org/downloads/ (or the Microsoft Store on Windows).
**During the Windows installer, check the box that says "Add python.exe to PATH" at the very bottom before clicking
Install.**

### Naviate to script folder

Open your Terminal or Command Prompt and navigate to the script folder.

```bash
cd your/path/to/wherever/this/dir/is
```

### Run setup

```bash
# Windows
setup.bat

# Mac OS
chmod +x setup.sh
./setup.sh       
```

### Data

Put <asutus>.xslx (The file(s) you want to encrypt) and
your recipients CSV into a single folder. The files you're encrypting must be named <asutus>.xslx.

#### The CSV Format

Your data.csv file must have a header row and look exactly like this (save it with UTF-8 encoding if names have special
characters like õ, ä, ö, ü):

```text
asutus;kood;e-mail
Mari Maasikas;48201010001;mari@example.com
Jaan Tamm;38001010002;jaan@example.com
```

**Edit the email template (email-template.txt) in the script folder.**

### Run the script:

```bash
python3 script.py <your-file.csv> # Or leave file argument empty to open File Explorer/Finder
# You can use -s or --send-automatically to mail the encrypted file immediately instead of opening the draft in your mail client.
```

The files generated will end in .cdoc2. The recipients must have a recently updated version of the DigiDoc4 software
installed to open them, as older versions only support the legacy .cdoc standard.

The encrypted files will be saved in the same directory as the provided input files in results/.

# Debugging

### LDAP error (esteid.ldap.sk.ee:636)

If the encryption gives javax.naming.CommunicationException: simple bind failed: esteid.ldap.sk.ee:636 error, then in
the jdk/conf/security/java.security remove the TLS_RSA_* in the jdk.tls.disabledAlgorithms.

```bash
sed -i '' '/^jdk\.tls\.disabledAlgorithms=/{:loop
/\\$/{N
b loop
}
s/TLS_RSA_\*,[[:space:]]*//g
}' "$JAVA_HOME/conf/security/java.security"

# Verify
grep -A5 '^jdk.tls.disabledAlgorithms=' \
"$JAVA_HOME/conf/security/java.security"
```

### CLI tool info

```bash
java -jar cdoc2-cli-1.9.0.jar
```