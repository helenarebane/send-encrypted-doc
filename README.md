# Setup for Dummies

### Install Java (Required for CDOC)

Download and install JDK 21
from [Adoptium](https://adoptium.net/en-GB/temurin/releases?os=any&version=21&package=jdk&mode=filter&arch=any).

### Install Python

Download Python from the [official website](https://www.python.org/downloads/) (or the Microsoft Store on Windows).

> ⚠️ **Important (Windows):** During installation, check the box that says "Add python.exe to PATH" at the bottom of the
> window before clicking Install.

### Navigate to script folder

Open your Terminal or Command Prompt and navigate to your script folder:

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

### Email Template

Edit the email template in the script folder (`email-template.txt`).

---

### Data

Put [asutus].xslx (the file(s) you want to encrypt) and your recipients CSV into a single folder. The files you're encrypting
must be named [asutus].xslx.

> ⚠️ **Important Your recipients.csv file must have a header row and look exactly like this (use UTF-8 encoding if names have special
characters like õ, ä, ö, ü):
> ```
> asutus;kood;e-mail
> Mari Maasikas;48201010001;mari@example.com
> Jaan Tamm;38001010002;jaan@example.com
>```


---

## Running the Script

Run the script by pointing it to your CSV file:

```bash
python3 script.py recipients.csv # leave file argument empty to open File Explorer/Finder

# You can use -s or --send-automatically to mail the encrypted 
# file immediately instead of opening the draft in your mail client.
```

The files generated will end in .cdoc2. The recipients must have a recently updated version of the DigiDoc4 software
installed to open them, as older versions only support the legacy .cdoc standard.
The encrypted files will be saved in a new `/results` folder inside your data directory.

---

# Debugging

### LDAP error (esteid.ldap.sk.ee:636)

If encryption throws javax.naming.CommunicationException: simple bind failed: esteid.ldap.sk.ee:636 error, remove
TLS_RSA_* in the jdk.tls.disabledAlgorithms in jdk/conf/security/java.security.

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