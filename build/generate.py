#!/usr/bin/env python3
"""Generates the static KAPAMALQ manual website from the extracted PDF assets.

Usage: python3 build/generate.py <extracted_imgs_dir>
Copies referenced figure images into assets/figures/ and writes index.html.
"""
import hashlib
import html
import os
import re
import shutil
import sys
from collections import defaultdict

SRC_IMGS = sys.argv[1] if len(sys.argv) > 1 else "build/imgs"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FIG = os.path.join(ROOT, "assets", "figures")
os.makedirs(OUT_FIG, exist_ok=True)

# ---------------------------------------------------------------- image maps
files = sorted(os.listdir(SRC_IMGS))
by_page = defaultdict(list)
hashes = {}
for f in files:
    m = re.match(r"p-(\d+)-\d+\.(png|jpe?g)", f)
    if not m:
        continue
    page = int(m.group(1))
    by_page[page].append(f)
    with open(os.path.join(SRC_IMGS, f), "rb") as fh:
        hashes[f] = hashlib.md5(fh.read()).hexdigest()

hash_counts = defaultdict(int)
for h in hashes.values():
    hash_counts[h] += 1
REPEATED = {f for f, h in hashes.items() if hash_counts[h] >= 4}

# captions per page, in document order (parsed from pdftotext output)
CAPTIONS = {
    13: ["Figure 1.0 Log-in Page", "Figure 2.0 Main Page (Members' Section)"],
    14: ["Figure 2.1 Add Member Form", "Figure 3.0 Main Page (Members' Section)", "Figure 3.1 UPDATE MEMBER INFO Search Query"],
    15: ["Figure 3.1.1 UPDATE MEMBER INFO Form", "Figure 4.0 Main Page (Members' Section)", "Figure 4.1 UPDATE ACCOUNT NUMBER Search Query"],
    16: ["Figure 5.0 Main Page (Members' Section)", "Figure 5.1 MEMBER ACCOUNT DETAILS Search Query", "Figure 5.1.1 MEMBER ACCOUNT DETAILS Form"],
    17: ["Figure 6.0 Main Page (Members' Section)", "Figure 6.1 ACCOUNT MASTER LIST Search Query", "Figure 7.0 Main Page (Members' Section)"],
    18: ["Figure 7.1 ADD/UPDATE CO-MAKER Search Query", "Figure 7.1.1 ADD/UPDATE CO-MAKER Page", "Figure 8.0 Main Page (Members' Section)"],
    19: ["Figure 8.1 FIXED CAP CON Master List", "Figure 8.1.1 EXCESS CAP CON Master List"],
    20: ["Figure 9.0 Main Page (Members' Section)", "Figure 9.1 EX-MEMBER ACCOUNT Page", "Figure 9.1.1 EX-MEMBER ACCOUNT List"],
    21: ["Figure 10.0 Main Page (Members' Section)", "Figure 10.1 PASSBOOK PRINTING Page", "Figure 11.0 Main Page (Transactions Section)"],
    22: ["Figure 11.1 Loan Page", "Figure 12.0 Main Page (Transactions Section)", "Figure 12.1 WITHDRAWAL APPLICATION FORM Search Query"],
    23: ["Figure 12.1.1 WITHDRAWAL APPLICATION FORM", "Figure 12.1.2 WITHDRAWAL APPLICATION FORM"],
    24: ["Figure 13.0 Main Page (Transactions Section)", "Figure 13.1 WITHDRAWAL RELEASED Page", "Figure 14.0 Main Page (Transactions Section)", "Figure 14.1 VERIFY TRANSACTIONS Page"],
    25: ["Figure 15.0 Main Page (Transactions Section)", "Figure 15.1 UPDATE ERROR TRANSACTIONS Page", "Figure 16.0 Main Page (Transactions Section)", "Figure 16.1 PRINT VOUCHER Page"],
    26: ["Figure 17.0 Main Page (Transactions Section)", "Figure 17.1 POST AUDIT VERIFICATION Page", "Figure 18.0 Main Page (Transactions Section)", "Figure 18.1 APPROVE TRANSACTIONS Page"],
    27: ["Figure 19.0 Main Page (Transactions Section)", "Figure 19.1.1 TRANSACTIONS STATUS Page", "Figure 20.0 Main Page (Transactions Section)"],
    28: ["Figure 20.1 CHECKLIST Page", "Figure 21.0 Main Page (Transactions Section)", "Figure 21.1 LOAN SAMPLE COMPUTATION Query Page"],
    29: ["Figure 21.1.1 LOAN SAMPLE COMPUTATION Query Page", "Figure 21.1.2 LOAN SAMPLE COMPUTATION Query Page"],
    30: ["Figure 22.0 Main Page (Transactions Section)", "Figure 22.1 LOAN PRINT EIR Page", "Figure 22.1.1 LOAN PRINT EIR Page"],
    31: ["Figure 23.0 Main Page (Transactions Section)", "Figure 23.1 PRINT DECLARATION FORM Page", "Figure 23.1.1 PRINT DECLARATION FORM Page", "Figure 23.2.1 PRINT CONSENT SLIP Page"],
    32: ["Figure 23.2.2 PRINT CONSENT SLIP Page", "Figure 23.3 EDIT CONSENT SLIP LIST Page"],
    33: ["Figure 24.0 Main Page (Accounting System Section)", "Figure 24.1 UPDATE MEMBER'S REMITTANCE Page"],
    34: ["Figure 25.0 Main Page (Accounting System Section)", "Figure 25.1 CHECK REMITTANCE Page", "Figure 26.0 Main Page (Accounting System Section)"],
    35: ["Figure 26.1 DEATH BENEFIT PROGRAM Search Query", "Figure 26.1.1 DEATH BENEFIT PROGRAM Page", "Figure 27.0 Main Page (Accounting System Section)"],
    36: ["Figure 27.1 DEATH BENEFIT PROGRAM PRINTING Page", "Figure 28.0 Main Page (Accounting System Section)", "Figure 28.1 KAPAMALQ DIVIDEND Search Query Page"],
    37: ["Figure 28.1.1 KAPAMALQ DIVIDEND Printing Page", "Figure 29.0 Main Page (Accounting System Section)", "Figure 29.1 KAPAMALQ DIVIDEND Printing Page"],
    38: ["Figure 30.0 Main Page (Accounting System Section)", "Figure 30.1 CASH RECEIPT Page", "Figure 30.1.1 CASH RECEIPT Printing Section"],
    39: ["Figure 31.0 Main Page (Accounting System Section)", "Figure 31.1 EDIT CASH RECEIPT Search Query", "Figure 32.0 Main Page (Accounting System Section)"],
    40: ["Figure 32.1 CASH DISBURSEMENT Page", "Figure 32.1.1 CASH DISBURSEMENT Printing Section", "Figure 33.1 EDIT CASH DISBURSEMENT Search Query"],
    41: ["Figure 34.0 Main Page (Accounting System Section)", "Figure 34.1 ADJUSTMENTS Page"],
    42: ["Figure 34.1.1 ADJUSTMENTS Page", "Figure 35.0 Main Page (Accounting System Section)"],
    43: ["Figure 35.1 EDIT REQUEST Page", "Figure 36.0 Main Page (Accounting System Section)"],
    44: ["Figure 36.1 SOA SUMMARY Page", "Figure 37.0 Main Page (Accounting System Section)", "Figure 37.1 CC-SOA PER OFFICE Summary Page"],
    45: ["Figure 38.0 Main Page (Accounting System Section)", "Figure 38.1 REGULAR LOAN – SOA PER OFFICE Summary Page"],
    46: ["Figure 39.0 Main Page (Accounting System Section)", "Figure 39.1 CREATE / PRINT DISBURSEMENT VOUCHER Page"],
    47: ["Figure 39.1.1 CREATE / PRINT DISBURSEMENT VOUCHER Page (Cont.)", "Figure 40.0 Main Page (Accounting System Section)"],
    48: ["Figure 40.1 LIST / PRINT DISBURSEMENT VOUCHER Page", "Figure 41.0 Main Page (Reporting Section)", "Figure 41.1 REMITTANCE REPORTS Page"],
    49: ["Figure 42.0 Main Page (Reporting Section)", "Figure 42.1 LOAN PAST-DUE MASTER LIST Page", "Figure 43.0 Main Page (Reporting Section)"],
    50: ["Figure 43.1 TRIAL BALANCE Page", "Figure 44.0 Main Page (Reporting Section)", "Figure 44.1 SCHEDULE OF TB ACCOUNTS Page"],
    51: ["Figure 45.0 Main Page (Reporting Section)", "Figure 45.1 ADD ACCOUNT TITLE Page"],
    52: ["Figure 46.0 Main Page (Reporting Section)", "Figure 46.1 FINANCIAL STATEMENTS Page"],
    53: ["Figure 47.0 Main Page (Payroll Section)", "Figure 47.1 PAYROLL REPORTS Page", "Figure 48.0 Main Page (Payroll Section)", "Figure 48.1 STATEMENT OF DEDUCTIONS Page"],
    54: ["Figure 49.0 Main Page (Scanned Files Page)", "Figure 49.1 SCANNED FILES Directory Page", "Figure 50.0 Main Page (Bottom Right Section)"],
    55: ["Figure 50.1 RENEW LIST Viewing Page", "Figure 51.0 Main Page (Bottom Right Section)", "Figure 51.1 LOAN AMORT LIST Page", "Figure 52.0 Main Page (Bottom Right Section)"],
    56: ["Figure 52.1 MEMBERSHIP LIST Page", "Figure 53.0 Main Page (Bottom Right Section)", "Figure 53.1 KYC SUMMARY Page", "Figure 54.0 Main Page (Bottom Right Section)", "Figure 54.1 UPDATE BOARD MEMBERS Page"],
}

# Pair captions with images in global document order. In the PDF every
# figure caption sits directly below its image, so the Nth caption belongs
# to the Nth image. The only images without captions are the installation
# screenshots on pages 7 and 10, which are excluded here.
UNCAPTIONED_PAGES = {7, 10}
ordered_caps = [cap for page in sorted(CAPTIONS) for cap in CAPTIONS[page]]
ordered_imgs = [f for page in sorted(by_page) if page not in UNCAPTIONED_PAGES
                for f in by_page[page] if page >= 13]
assert len(ordered_caps) == len(ordered_imgs), (len(ordered_caps), len(ordered_imgs))
FIG = dict(zip(ordered_caps, ordered_imgs))

def fig_html(cap):
    f = FIG.get(cap)
    if not f:
        return ""
    shutil.copy(os.path.join(SRC_IMGS, f), os.path.join(OUT_FIG, f))
    return (f'<figure><img src="assets/figures/{f}" loading="lazy" '
            f'alt="{html.escape(cap)}"><figcaption>{html.escape(cap)}</figcaption></figure>')

# ------------------------------------------------------------------ content
def sec(sid, title, body):
    return f'<section id="{sid}"><h2>{html.escape(title)}</h2>{body}</section>'

def sub(sid, title, body):
    return f'<div class="subsec" id="{sid}"><h3>{html.escape(title)}</h3>{body}</div>'

def ol(items):
    return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"

def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def defs(items):
    return "<ol>" + "".join(f"<li><strong>{t}:</strong> {d}</li>" for t, d in items) + "</ol>"

def guide(num, sid, title, steps, caps, note=None):
    body = ol(steps)
    if note:
        body += f'<p class="note"><strong>NOTE:</strong> {note}</p>'
    body += '<div class="figs">' + "".join(fig_html(c) for c in caps) + "</div>"
    return sub(sid, f"{num}. {title}", body)

C = "code"
def c(s):
    return f"<code>{html.escape(s)}</code>"

parts = []

parts.append(sec("introduction", "Introduction", (
    "<p>The Kapisanan sa Pag-Iimpok at Paghihiram ng mga Kawani ng Pamahalaang Lungsod Quezon "
    "(KAPAMALQ) System is designed to manage core functions such as facilitating member loan "
    "withdrawals, tracking savings details, updating transaction records, and maintaining an "
    "overview of the loan portfolio, among other essential operations.</p>")))

parts.append(sec("system-requirements", "System Requirements", ul([
    "<strong>Operating System:</strong> Windows 10 (64-bit) version 1909 or later, or Windows 11.",
    "<strong>CPU:</strong> Intel Core i5 (8th generation or newer) or AMD Ryzen 5 equivalent.",
    "<strong>Storage:</strong> 256GB total capacity (or higher) with 50GB free space recommended.",
    "<strong>RAM:</strong> 8GB minimum, 16GB recommended for optimal performance.",
    "<strong>Network:</strong> Local Area Network (LAN) with minimum 100 Mbps speed (1 Gbps recommended)."])))

install = []
install.append(sub("prerequisites", "Prerequisites", (
    "<p>Ensure the following network settings are configured on your system:</p>" + ol([
        f"IPv4 Address: {c('192.168.1.111')}",
        f"Subnet Mask: {c('255.255.255.0')}",
        f"Default Gateway: {c('192.168.1.1')}",
        f"Preferred DNS Server: {c('192.168.1.1')}"]) +
    "<p><strong>Steps to Configure Network Settings (if not already set):</strong></p>" + ol([
        "Open the <strong>Control Panel</strong>.",
        "Navigate to <strong>Network and Sharing Center &gt; Change adapter settings</strong>.",
        "Right-click your active network connection and select <strong>Properties</strong>.",
        "Select <strong>Internet Protocol Version 4 (TCP/IPv4)</strong> and click <strong>Properties</strong>.",
        "Manually input the settings above.",
        "Click <strong>OK</strong> to save and exit."]))))
install.append(sub("installing-wampserver", "Installing WampServer", ol([
    "<strong>Download WampServer:</strong> Visit the official WampServer website and download the latest version compatible with your operating system.",
    "<strong>Run the Installer:</strong> Double-click the downloaded executable file to start the installation process. Follow the on-screen instructions. Use the default installation directory (usually " + c(r"C:\wamp64") + ").",
    "<strong>Configure Apache Server:</strong> During installation, you may be prompted to select your default browser. Choose your preferred browser or skip this step to use the default. If required, allow Apache Server through the Windows Firewall: open <strong>Windows Security &gt; Firewall &amp; network protection</strong>, click <strong>Allow an app through the firewall</strong>, locate \"Apache HTTP Server\" in the list and ensure both \"Private\" and \"Public\" are checked.",
    "<strong>Set Up Apache Port:</strong> It is best practice to use a 4-digit port number, such as 1962. Open " + c(r"C:\wamp64\bin\apache\apache2.4.9\conf\httpd.conf") + " in a text editor, locate " + c("Listen 80") + " and replace it with " + c("Listen 0.0.0.0:1962") + " and " + c("Listen [::0]:1962") + ", then save and close the file. Additionally, open " + c(r"C:\wamp64\wampmanager.tpl") + " and " + c(r"C:\wamp64\wampmanager.ini") + " with Notepad/Notepad++, search for " + c("http://localhost/") + " (CTRL+F) and replace all occurrences with " + c("http://localhost:1962/") + ". Save and close the files.",
    "<strong>Make WAMP Accessible to Network:</strong> Open " + c(r"C:\wamp64\bin\apache\apache2.4.9\conf\httpd.conf") + " and ensure the following settings in the " + c("<Directory />") + " section:<pre>&lt;Directory /&gt;\nAllowOverride all\nRequire all granted\n&lt;/Directory&gt;</pre>Save and close the file.",
    "<strong>Complete Installation:</strong> Finish the setup and launch WampServer. The WampServer icon in the system tray should turn green, indicating all services are running."])))
install.append(sub("installing-mysql", "Installing MySQL", ol([
    "<strong>Download MySQL Installer:</strong> Visit the official MySQL website and download the \"MySQL Installer for Windows.\"",
    "<strong>Run the Installer:</strong> Start the installation process by running the downloaded installer. Select the \"Custom\" installation type and include \"MySQL Server\" and \"MySQL Workbench\" in your selection.",
    "<strong>Configure MySQL Server:</strong> Set up a new MySQL Server instance using <strong>Standalone MySQL Server</strong> as the configuration type. Choose the default port (3306). Set a strong root password and optionally create additional user accounts.",
    "<strong>Start MySQL Server:</strong> Complete the installation and start the MySQL Server. Test the connection using MySQL Workbench or the command line.",
    "<strong>Make MySQL Accessible to Network:</strong> Open " + c(r"C:\wamp64\alias\phpmyadmin.conf") + " in a text editor and update the configuration to:<pre>AllowOverride all\nRequire local\nOrder Deny,Allow\nDeny from all\nAllow from localhost ::1 127.0.0.1\nAllow from 112.200.0.0/16</pre>Save and close the file."])))
install.append(sub("installing-vcredist", "Installing Visual C++ Redistributable (vcredist_x64.exe)", ol([
    "<strong>Download Visual C++ Redistributable:</strong> Visit the Microsoft Download Center and download the latest version of " + c("vcredist_x64.exe") + ".",
    "<strong>Run the Installer:</strong> Double-click the downloaded executable file to start the installation. Accept the license agreement and click <strong>Install</strong>. Wait for the installation to complete."])))
install.append(sub("post-install", "Post-Installation Verification", ol([
    "<strong>Verify WampServer:</strong> Check the WampServer icon in the system tray — it should be green, indicating that all services are running. Open a web browser and navigate to " + c("http://localhost/") + ". The WampServer homepage should appear.",
    "<strong>Verify phpMyAdmin:</strong> Open a web browser and navigate to " + c("http://localhost/phpmyadmin/") + ". Log in using the MySQL root credentials set during the installation. Make sure that you can access and manage the MySQL databases."])))
install.append(sub("root-password", "Setting Root Password for MySQL", (
    "<p>By default, the WAMP bundle does not set a password for the MySQL root user. Follow these steps to set a root password:</p>" + ol([
        "<strong>Open MySQL Console:</strong> Click the WampServer icon in the system tray, select <strong>MySQL &gt; MySQL Console</strong>, and press <strong>Enter</strong> when prompted for a password (as none is set by default).",
        "<strong>Set Root Password:</strong> At the " + c("mysql>") + " prompt, type the following command and press Enter:<pre>SET PASSWORD FOR root@localhost = PASSWORD('EnterYourPasswordHere');</pre>Replace <em>EnterYourPasswordHere</em> with your desired password.",
        "<strong>Update phpMyAdmin Configuration:</strong> Navigate to the WampServer phpMyAdmin folder (e.g. " + c(r"C:\wamp64\apps\phpmyadmin\ ") + "), open " + c("config.inc.php") + " in a text editor, find the line <pre>$cfg['Servers'][$i]['password'] = '';</pre> and update it to include your root password. Ensure <strong>AllowNoPassword</strong> is set to false:<pre>$cfg['Servers'][$i]['AllowNoPassword'] = false;</pre>Save and close the file."]))))
install.append(sub("additional-config", "Additional Configurations", ol([
    "<strong>Edit my.ini:</strong> Open " + c(r"C:\wamp64\bin\mysql\mysql5.x.x\my.ini") + " and update the " + c("password") + " and " + c("lc-messages") + " lines with your root password and preferred locale (e.g. " + c("lc-messages=en_PH") + ").",
    "<strong>Enable Number Formatter (PHP intl):</strong> Copy files starting with " + c("icu*") + " from " + c("<wamp_installation_path>/bin/php/php5.4.3/") + " to " + c("<wamp_installation_path>/bin/apache/apache2.2.22/bin/") + ". Open " + c("php.ini") + " and enable the intl extension: <pre>extension=php_intl.dll</pre>Restart WampServer.",
    "<strong>Change Default Timezone in WAMP:</strong> Open " + c("php.ini") + ", search for " + c("date.timezone") + " and replace it with your preferred timezone, e.g. <pre>date.timezone = Asia/Singapore</pre>"])))
install.append(sub("start-on-boot", "Start WAMP on Boot Up", (
    "<p>The best way to ensure WampServer starts automatically upon system boot is to schedule a task that runs at user logon:</p>" + ol([
        "<strong>Open Task Scheduler:</strong> Press <strong>Win + S</strong>, search for <strong>Task Scheduler</strong> and open it.",
        "<strong>Create a New Task:</strong> Click <strong>Create Task</strong> in the right-hand panel.",
        "<strong>Configure General Settings:</strong> Name the task <em>WampServer</em> and check <strong>Run with highest privileges</strong>.",
        "<strong>Set Trigger to Start Task at Logon:</strong> Go to the <strong>Triggers</strong> tab, click <strong>New</strong>, set the trigger to <strong>Begin the task: At log on</strong>, and click OK.",
        "<strong>Define the Action to Start WAMP:</strong> Go to the <strong>Actions</strong> tab, click <strong>New</strong>, select <strong>Start a program</strong>, browse to " + c(r"C:\wamp64\wampmanager.exe") + " and set the <strong>Start in</strong> field to " + c(r"C:\wamp64") + ". Click OK.",
        "<strong>Set Task Conditions:</strong> In the <strong>Conditions</strong> tab, uncheck <em>Start the task only if the computer is on AC power</em> and <em>Stop the task if it runs longer than [x hours/minutes]</em>.",
        "<strong>Finalize and Restart:</strong> Click OK to save the task, close Task Scheduler, and restart your computer to test the configuration."]) +
    "<h4>Alternative Method: Using Services</h4>" + ol([
        "Press <strong>Win + R</strong>, type " + c("services.msc") + " and press Enter to open the Services window.",
        "Locate the services " + c("wampapache64") + " (Apache) and " + c("wampmysqld64") + " (MySQL).",
        "For each service: right-click, select <strong>Properties</strong>, set the <strong>Startup type</strong> to <strong>Automatic</strong>, then click Apply and OK.",
        "Restart your computer to verify both services start automatically."]))))
parts.append(sec("installation", "Installation Instructions", "".join(install)))

ui = []
ui.append(sub("ui-credit", "I. Credit / Loaning System", (
    "<p>The Credit / Loaning System interface is divided into two primary sections for ease of use: "
    "<strong>Members</strong> and <strong>Transactions</strong>.</p>"
    "<h4>1. Members</h4><p>The Members section is focused on managing member information and related administrative tasks:</p>" + defs([
        ("Add New Member", "Enables the addition of a new member to the system."),
        ("Update Member", "Facilitates the modification of an existing member's details."),
        ("Edit Account Number", "Allows changes to a member's account number."),
        ("Edit Member Name", "Provides the option to update member names."),
        ("Edit Office Name", "Updates the office name linked to a member's account."),
        ("View Member Details", "Displays comprehensive details for a selected member."),
        ("Add/Update Co-Maker", "Adds or updates co-makers associated with a member's account."),
        ("Account Master List", "Shows a complete list of all accounts within the system."),
        ("Set to Inactive", "Deactivates a member's account while retaining their records."),
        ("Fixed Capital Contribution (CC) Office", "Determines the fixed Capital Contribution (CC) of the members per office."),
        ("Exceed Capital Contribution (CC) Buffer", "Monitors and highlights when a predefined Capital Contribution (CC) buffer is exceeded. The EXCEED COUNT is prominently displayed for quick reference."),
        ("Passbook Printing", "Enables the printing of a member's passbook for transaction tracking."),
        ("Ex-Member Account", "Manages the accounts of former members.")]) +
    "<h4>2. Transactions</h4><p>The Transactions section is dedicated to managing financial transactions and approvals:</p>" + defs([
        ("Loan", "Facilitates the processing and evaluation of loan applications, including assessing the borrower's capacity to repay for regular and emergency loans, as well as ensuring compliance with the single borrower's limit (SBL)."),
        ("Withdraw", "Facilitates fund withdrawal transactions."),
        ("Verification", "Ensures transaction details are accurate and complete. Flagged items, if any, are highlighted for attention."),
        ("Voucher", "Manages transaction vouchers, including generation and review."),
        ("Withdrawal List", "Displays a detailed list of withdrawal transactions."),
        ("Edit Transactions", "Allows authorized users to modify transaction details as needed."),
        ("Post Audit", "Displays audit-related items for review and action."),
        ("Approval", "Handles pending approvals for loans and other transactions."),
        ("Monitor Status", "Tracks the progress and status of loans, withdrawals, and other transactions."),
        ("Check List", "Provides a detailed checklist to verify transaction accuracy and compliance."),
        ("Regular Inquiry", "A general tool for accessing account and transaction information. Regular loans range from P5,000 – P250,000 (loan sample computation including the interest-of-loan, IOL)."),
        ("Emergency Inquiry", "Specialized for urgent account or transaction-related inquiries. Emergency loans range from P5,000 – P15,000 (loan sample computation including the interest-of-loan, IOL)."),
        ("Print EIR", "Prints the Effective Interest Rate (EIR) report for loans or transactions."),
        ("Declaration Form", "Generates a Membership Declaration Form (MDF) for fixed capital contribution."),
        ("Consent Slip", "Prints or updates standard consent slips. The consent slip signifies the member's agreement to have insurance payments for the regular loan deducted directly from their salary."),
        ("Emergency Consent Slip", "Prepares consent slips for emergency transactions. The consent slip signifies the member's agreement to have insurance payments for the emergency loan deducted directly from their salary."),
        ("Slip Print/Edit/Delete", "Manages printing, editing, or deleting various transaction slips."),
        ("Emergency Loan (EL) Slip Print/Edit/Delete", "Manages printing, editing, or deleting various emergency loan (EL) transaction slips.")]) +
    "<h4>Loan Summary</h4><p>The Loan Summary Section provides a consolidated view of loan activities for the year, categorized into Regular Loans and Emergency Loans. It highlights the total amounts disbursed and the corresponding net amounts collected, enabling efficient monitoring and analysis of loan performance.</p>" + defs([
        ("View Loan", "Displays detailed information about individual loans, including borrower details, loan type, repayment terms, and current status. These include the member's office, name, age, loan date, check no., maturity date, amortization, disbursement voucher (DV), promissory note (PN), capacity excess, loan amount and net amount (for both regular and emergency loans)."),
        ("View Loan Summary", "Presents an aggregated summary of all loans within a selected timeframe, broken down by month and loan type.")]) +
    "<h4>Loan Summary Table Overview</h4><p>The loan summary table provides a monthly breakdown of loan data with the following components:</p>" + defs([
        ("Month (Accountability)", "Indicates the specific month for which the loan transactions are recorded."),
        ("Regular Loans", "<em>Amount</em> — the total loan amount disbursed under regular loan programs during the month; <em>Net</em> — the actual net amount provided to members."),
        ("Emergency Loans", "<em>Amount</em> — the total loan amount disbursed under emergency loan programs during the month; <em>Net</em> — the actual net amount collected from repayments of emergency loans during the month."),
        ("Total Month", "Combines the total loan disbursement (amount) and actual amount (net) of loan provided from both regular and emergency loans for the respective month."),
        ("Annual Summary", "Regular Loans: total amount and total net for the year. Emergency Loans: total amount and total net for the year. Grand Total: aggregates the total disbursed loans (Amount) and total collections (Net) from both loan types for the entire year.")]))))
ui.append(sub("ui-accounting", "II. Accounting System", (
    "<p>The Accounting System interface is designed for efficient financial management. It is divided into two sections:</p>"
    "<h4>1. Transactions</h4>" + defs([
        ("Post Remittance", "Processes the posting of remittances into the system. This also posts the transaction in the member's ledger which includes the official receipt (OR), remittances, acknowledgement receipt and general adjustment."),
        ("Death Benefit (DB) Deduction", "Handles deductions related to death benefits."),
        ("Dividend (Cash/Check)", "Manages and calculates member dividends, including the master list for dividend computation."),
        ("Check Remittance", "Verifies and reviews remittance details per office."),
        ("Death Benefit List", "Displays and manages the list of members' beneficiary/ies, including the details and amount that the beneficiary will receive."),
        ("Print Dividend Check", "Prints the list of dividend checks of members for distribution."),
        ("Cash Receipt", "Records cash receipts into the system."),
        ("Edit/Delete Receipt", "Allows modifications or deletions of recorded receipts."),
        ("Cash Disbursement", "Handles cash disbursement transactions."),
        ("Edit/Delete Disbursement", "Enables editing or deletion of recorded disbursements."),
        ("Adjustments", "Processes financial adjustments on a monthly basis."),
        ("Edit Request", "Manages pending edit requests for transactions, with notifications for flagged items."),
        ("SOA Summary", "Displays a consolidated summary of the Statement of Accounts (SOA)."),
        ("Capital Contribution (CC) – SOA per Office", "Generates SOA reports specific to each Capital Contribution."),
        ("Regular Loan (RL) – SOA per Office", "Provides SOA reports for RL (Regular Loan) categorized by office."),
        ("Emergency Loan (EL) – SOA per Office", "Prepares SOA reports for EL (Emergency Loan) by office."),
        ("Create Voucher", "Enables the creation of vouchers for financial/disbursement transactions."),
        ("Voucher List", "Displays a list of all created vouchers for reference or review.")]) +
    "<h4>2. Reporting</h4>" + defs([
        ("Remittance Reports", "Generates detailed reports of remittances."),
        ("Past Due Reports", "Highlights accounts or transactions that are overdue."),
        ("Trial Balance", "Displays the trial balance for account reconciliation."),
        ("Financial Statements", "Prepares comprehensive financial statements."),
        ("SOA of TB Accounts", "Generates the Statement of Accounts for Trial Balance accounts."),
        ("Add Account Title", "Allows the addition of new account titles.")]))))
ui.append(sub("ui-payroll", "III. Payroll System", (
    "<p>The Payroll System focuses on managing employee payroll and related deductions:</p>" + defs([
        ("Payroll", "Processes employee payrolls, including salary calculations and distribution."),
        ("Statement of Deductions", "Generates detailed statements outlining all employee deductions: SSS Loan, SSS Contributions, Pag-ibig Loan, Pag-ibig Contribution, Philhealth Contribution, Due from Employees &amp; Officers, and KAPAMALQ deposit and loans (Regular/Emergency Loans if any).")]))))
ui.append(sub("ui-scanned", "IV. Scanned Files (Document Archival)", (
    "<p>The Scanned Files provides a centralized location for managing scanned documents:</p>" + defs([
        ("Scanned Files", "Stores, retrieves, and organizes scanned files for quick access and reference. For scanning are board resolutions, 201 files, individual vouchers, member's KYC, minutes of the meetings, office voucher and other transactions.")]))))
ui.append(sub("ui-remittance", "Remittance", (
    "<p>The Remittance Section provides tools to track and analyze remittance records obtained from the accounting department. Users can monitor remittance details such as:</p>" + defs([
        ("Month (Accountability)", "Displays the specific month tied to the remittance."),
        ("Date Remit", "Shows the date on which the remittance was transmitted."),
        ("OR Number", "Refers to the official receipt number associated with the transaction."),
        ("Amount", "Indicates the remitted amount for the corresponding month.")]) +
    "<p>These records, sourced from the accounting department, allow for accurate financial tracking and reconciliation.</p>" + defs([
        ("Renew List", "Enables users to view and manage accounts that are due for renewal. This feature is essential for maintaining updated records and ensuring account activity."),
        ("Loan Amort List", "Provides detailed information about loan amortizations, helping users keep track of repayments and balances for active loans."),
        ("Membership List", "Displays a comprehensive list of all active members, allowing for quick access to member details and statuses."),
        ("KYC Summary", "The KYC (Know Your Customer) Summary provides an overview of member verification and compliance status. This ensures adherence to regulatory requirements and enhances member data integrity."),
        ("Update Board Members", "Facilitates the management and modification of board member details, ensuring the system reflects the current governance structure.")]))))
parts.append(sec("ui-overview", "User Interface Overview", "".join(ui)))

g = []
g.append(guide("I", "logging-in", "Logging In to the System",
    ["To use the KAPAMALQ System, kindly enter the appropriate username and password. After that, click the <strong>SUBMIT</strong> button."],
    ["Figure 1.0 Log-in Page"]))
g.append(guide("II", "adding-members", "Adding Members to the System",
    ["To add a member's profile, go and click the <strong>ADD MEMBER</strong> button.",
     "The assigned personnel will input the necessary details prior to the member's information.",
     "Once done, click the <strong>SAVE AND ADD MEMBER</strong> button."],
    ["Figure 2.0 Main Page (Members' Section)", "Figure 2.1 Add Member Form"]))
g.append(guide("updating-member", "updating-member", "Updating Member's Profile",
    ["To update a member's profile, go and click the <strong>UPDATE MEMBER</strong> button.",
     "Click the <strong>MEMBER NAME</strong> dropdown menu to select the name of the member, then click the <strong>SEARCH</strong> button to proceed.",
     "The assigned personnel can now update the member's profile.",
     "Once done, click the <strong>SAVE AND ADD MEMBER</strong> button."],
    ["Figure 3.0 Main Page (Members' Section)", "Figure 3.1 UPDATE MEMBER INFO Search Query", "Figure 3.1.1 UPDATE MEMBER INFO Form"],
    note="Only authorized staff can modify/update the members' information.").replace(">updating-member. ", ">III. ", 1))
g.append(guide("IV", "edit-account", "Edit Account Number / Member Name / Office Name",
    ["To edit/update an account number, member's name or office name, click either the <strong>EDIT ACCOUNT NUMBER</strong>, <strong>EDIT MEMBER NAME</strong> or <strong>EDIT OFFICE NAME</strong> button.",
     "Click the <strong>MEMBER NAME</strong> dropdown menu to select the name of the member, then click the <strong>SEARCH</strong> button."],
    ["Figure 4.0 Main Page (Members' Section)", "Figure 4.1 UPDATE ACCOUNT NUMBER Search Query"],
    note="The EDIT ACCOUNT NUMBER, EDIT MEMBER NAME and EDIT OFFICE NAME have the same query page albeit different functions."))
g.append(guide("V", "view-member-details", "View Member Details",
    ["To view the members' details, go and click the <strong>VIEW MEMBER DETAILS</strong> button.",
     "Click the <strong>MEMBER NAME</strong> dropdown menu to select the name of the member, then click the <strong>SEARCH</strong> button to proceed.",
     "From here, the user can view the member's account details such as: (a) Capital Contributions, (b) Consumption Loans, (c) Emergency Loans, and (d) Adjustments."],
    ["Figure 5.0 Main Page (Members' Section)", "Figure 5.1 MEMBER ACCOUNT DETAILS Search Query", "Figure 5.1.1 MEMBER ACCOUNT DETAILS Form"]))
g.append(guide("VI", "account-master-list", "Account Master List",
    ["To view the Account Master List, go and click the <strong>ACCOUNT MASTER LIST</strong> button.",
     "To start, first select the desired <strong>OFFICE</strong>.",
     "Once done, click on the <strong>SEARCH</strong> button to view the master list of the selected office."],
    ["Figure 6.0 Main Page (Members' Section)", "Figure 6.1 ACCOUNT MASTER LIST Search Query"]))
g.append(guide("VII", "co-maker", "Add/Update Co-Maker",
    ["To add or update the Co-Makers, click on the <strong>ADD/UPDATE CO-MAKER</strong> button.",
     "Select the member's name, select the desired office, then click the <strong>SEARCH</strong> button to proceed.",
     "This will display the details of the member with their respective co-makers. The staff will then add or update the member's co-maker as per the request of the member. Once done, they can simply save afterwards."],
    ["Figure 7.0 Main Page (Members' Section)", "Figure 7.1 ADD/UPDATE CO-MAKER Search Query", "Figure 7.1.1 ADD/UPDATE CO-MAKER Page"]))
g.append(guide("VIII", "fixed-cc", "Fixed CC Office &amp; Exceed CC Buffer",
    ["To access the Fixed CC Office, click the <strong>FIXED CC OFFICE</strong> button; otherwise, to access the Exceed CC Buffer, click the <strong>EXCEED CC BUFFER</strong> button.",
     "First select the desired <strong>OFFICE</strong>, then click the <strong>SEARCH</strong> button to display the accounts of the designated office.",
     "Excess Cap Con displays all the members with excess capital contribution."],
    ["Figure 8.0 Main Page (Members' Section)", "Figure 8.1 FIXED CAP CON Master List", "Figure 8.1.1 EXCESS CAP CON Master List"]))
g.append(guide("IX", "ex-member", "Ex-Member Account",
    ["To view the Ex-Member Account List, go and click the <strong>EX-MEMBER ACCOUNT</strong> button.",
     "To view the list of Ex-Members' Accounts, go and click the <strong>LIST EX-MEMBER ACCOUNT</strong> button.",
     "A list will appear showing all of the ex-members of KAPAMALQ."],
    ["Figure 9.0 Main Page (Members' Section)", "Figure 9.1 EX-MEMBER ACCOUNT Page", "Figure 9.1.1 EX-MEMBER ACCOUNT List"]))
g.append(guide("X", "passbook-printing", "Passbook Printing",
    ["To access the Passbook Printing page, go and click the <strong>PASSBOOK PRINTING</strong> button.",
     "First, type in the name of the member and hit the <strong>SEARCH</strong> button.",
     "Once the details of the member appear, set the inclusive dates to proceed with the printing.",
     "Once done, click <strong>PRINT</strong> to proceed."],
    ["Figure 10.0 Main Page (Members' Section)", "Figure 10.1 PASSBOOK PRINTING Page"]))
g.append(guide("XI", "loan", "Loan",
    ["To access the Loan page, go and click the <strong>LOAN</strong> button.",
     "First, type in the name of the member and hit the <strong>SEARCH</strong> button.",
     "The details of the member will appear. The staff will encode the \"capacity to pay of the borrower\" first, in order to assess the financial capability of the employee to pay for their loan/s.",
     "Once done, click <strong>SAVE CAPACITY</strong>.",
     "After that, click the <strong>PRINT SBL/CTP</strong>.",
     "Finally, the staff will ask what kind of loan the member will avail: whether regular or emergency loan."],
    ["Figure 11.0 Main Page (Transactions Section)", "Figure 11.1 Loan Page"]))
g.append(guide("XII", "withdrawal-form", "Withdrawal Application Form",
    ["To access the Withdrawal Page, go and click the <strong>WITHDRAW</strong> button.",
     "To start, first select the <strong>MEMBER'S NAME</strong>, then click on the <strong>SEARCH</strong> button to open the <strong>WITHDRAWAL APPLICATION FORM</strong>.",
     "Once on the Withdrawal Application Form, the user can now calculate the member's withdrawal — either Partial or Full withdrawal.",
     "Once done, the user will select the proper individual that will verify the member's withdrawal computation.",
     "Click the <strong>SAVE / PROCESS</strong> button to proceed and print the computation.",
     "A printout will appear containing the breakdown of the member's allowable withdrawal amount."],
    ["Figure 12.0 Main Page (Transactions Section)", "Figure 12.1 WITHDRAWAL APPLICATION FORM Search Query", "Figure 12.1.1 WITHDRAWAL APPLICATION FORM", "Figure 12.1.2 WITHDRAWAL APPLICATION FORM"]))
g.append(guide("XIII", "withdrawal-list", "Withdrawal List",
    ["To access the withdrawal list, go and click the <strong>WITHDRAWAL LIST</strong> button.",
     "On the withdrawal list, the staff has the ability to view the withdrawal amount released for the particular MONTH and YEAR for all the departments."],
    ["Figure 13.0 Main Page (Transactions Section)", "Figure 13.1 WITHDRAWAL RELEASED Page"]))
g.append(guide("XIV", "verification", "Verification",
    ["To access the verification page, go and click the <strong>VERIFICATION</strong> button.",
     "The verification of transaction pertains to verifying if the transactions done are correct. If it is correct, click the <strong>VERIFY</strong> button; otherwise, click the <strong>CANCEL</strong> button."],
    ["Figure 14.0 Main Page (Transactions Section)", "Figure 14.1 VERIFY TRANSACTIONS Page"]))
g.append(guide("XV", "edit-transaction", "Edit Transaction",
    ["To access the edit transaction page, go and click the <strong>EDIT TRANSACTION</strong> button.",
     "Search for the member's name, then click the <strong>SEARCH</strong> button to proceed and modify the transaction/s."],
    ["Figure 15.0 Main Page (Transactions Section)", "Figure 15.1 UPDATE ERROR TRANSACTIONS Page"]))
g.append(guide("XVI", "voucher", "Voucher",
    ["To access the voucher page, go and click the <strong>VOUCHER</strong> button.",
     "Once the voucher has been verified, it can now be printed. It will be verified again before it can proceed to printing the voucher."],
    ["Figure 16.0 Main Page (Transactions Section)", "Figure 16.1 PRINT VOUCHER Page"]))
g.append(guide("XVII", "post-audit", "Post Audit",
    ["To access the post audit page, go and click the <strong>POST AUDIT</strong> button.",
     "Post Audit Verification is done by checking the account entries by the accountant."],
    ["Figure 17.0 Main Page (Transactions Section)", "Figure 17.1 POST AUDIT VERIFICATION Page"]))
g.append(guide("XVIII", "approval", "Approval",
    ["To access the approval page, go and click the <strong>APPROVAL</strong> button.",
     "Approval of transaction is done by verification and approval of loan by the manager. This is the final step to generate the voucher."],
    ["Figure 18.0 Main Page (Transactions Section)", "Figure 18.1 APPROVE TRANSACTIONS Page"]))
g.append(guide("XIX", "monitor-status", "Monitor Status",
    ["To access the monitor status page, go and click the <strong>MONITOR STATUS</strong> button.",
     "Monitoring the transaction status also refers to tracking the transaction. Once done, the voucher will then be printed by the cashier."],
    ["Figure 19.0 Main Page (Transactions Section)", "Figure 19.1.1 TRANSACTIONS STATUS Page"]))
g.append(guide("XX", "check-list", "Check List",
    ["To access the check list page, go and click the <strong>CHECK LIST</strong> button.",
     "To start, manually encode all the necessary details.",
     "Click the <strong>SAVE</strong> button to proceed. This will display all the transaction details.",
     "In order to print the report transactions, set the <strong>FROM</strong> &amp; <strong>TO</strong> fields and click the <strong>PRINT TRANSACTIONS</strong> button."],
    ["Figure 20.0 Main Page (Transactions Section)", "Figure 20.1 CHECKLIST Page"]))
g.append(guide("XXI", "inquiry", "Regular Inquiry &amp; Emergency Inquiry",
    ["To access the regular loan or emergency loan inquiry, go and click either the <strong>REGULAR INQUIRY</strong> or <strong>EMERGENCY INQUIRY</strong> button.",
     "Once inside the Regular Inquiry or Emergency Inquiry page, the \"LOAN SAMPLE COMPUTATION\" page will appear. Search for the name of the member and click the <strong>SEARCH</strong> button.",
     "Once done, click the <strong>CALCULATE LOAN</strong> button to display the member/applicant's qualification and capacity to borrow. Through this, the staff will assess the amount given to the member.",
     "A sample computation will then be displayed to see the breakdown of the sample loan that the member could avail."],
    ["Figure 21.0 Main Page (Transactions Section)", "Figure 21.1 LOAN SAMPLE COMPUTATION Query Page", "Figure 21.1.1 LOAN SAMPLE COMPUTATION Query Page", "Figure 21.1.2 LOAN SAMPLE COMPUTATION Query Page"]))
g.append(guide("XXII", "print-eir", "Print EIR",
    ["To access the print EIR page, go and click the <strong>PRINT EIR</strong> button.",
     "First, search for the member's name and provide the necessary details of their particular loan, then click the <strong>SEARCH</strong> button.",
     "A breakdown of the loan calculation will appear. Once verified, simply click the <strong>PRINT EIR</strong> button."],
    ["Figure 22.0 Main Page (Transactions Section)", "Figure 22.1 LOAN PRINT EIR Page", "Figure 22.1.1 LOAN PRINT EIR Page"]))
g.append(guide("XXIII", "slips", "Declaration Form, Consent Slip, Emergency Consent Slip and Editing of Slips",
    ["To access the declaration and consent slips page, use the corresponding buttons in the Transactions section.",
     "First, search the name of the member, then click the <strong>SEARCH</strong> button to start the search. The declaration form will appear and is ready for printing.",
     "The same process is also done in printing the <strong>CONSENT SLIP</strong> and the <strong>EMERGENCY CONSENT SLIP</strong>: search the name of the member and click the <strong>SEARCH</strong> button.",
     "A consent slip to deduct for the monthly loan amortization of the cooperative will be ready for printing afterwards. Click the <strong>SAVE</strong> button.",
     "Modifying and printing consent slips is done through either <strong>EL SLIP PRINT/EDIT/DEL</strong> for emergency loans or <strong>SLIP PRINT/EDIT/DEL</strong> for regular loans."],
    ["Figure 23.0 Main Page (Transactions Section)", "Figure 23.1 PRINT DECLARATION FORM Page", "Figure 23.1.1 PRINT DECLARATION FORM Page", "Figure 23.2.1 PRINT CONSENT SLIP Page", "Figure 23.2.2 PRINT CONSENT SLIP Page", "Figure 23.3 EDIT CONSENT SLIP LIST Page"],
    note="The same process is also done in the EMER CONSENT SLIP."))
g.append(guide("XXIV", "post-remittance", "Post Remittance",
    ["To access the post remittance page, click the <strong>POST REMITTANCE</strong> button.",
     "First, search for the member and click the <strong>SEARCH</strong> button to proceed.",
     "On this page, the staff can also add/update the Capital Contribution, Consumption Loan, Emergency Loan and Adjustments of the member."],
    ["Figure 24.0 Main Page (Accounting System Section)", "Figure 24.1 UPDATE MEMBER'S REMITTANCE Page"]))
g.append(guide("XXV", "check-remittance", "Check Remittance",
    ["To access the check remittance page, click the <strong>CHECK REMITTANCE</strong> button.",
     "Select the OR Number (month) and the desired office in the dropdown menus.",
     "Click the <strong>SEARCH</strong> button to view the details of remittances."],
    ["Figure 25.0 Main Page (Accounting System Section)", "Figure 25.1 CHECK REMITTANCE Page"]))
g.append(guide("XXVI", "db-deduction", "DB Deduction",
    ["To access the DB Deduction page, click the <strong>DB DEDUCTION</strong> button.",
     "Search for the <strong>MEMBER NAME</strong> and click the <strong>SEARCH</strong> button to proceed."],
    ["Figure 26.0 Main Page (Accounting System Section)", "Figure 26.1 DEATH BENEFIT PROGRAM Search Query", "Figure 26.1.1 DEATH BENEFIT PROGRAM Page"]))
g.append(guide("XXVII", "death-benefit-list", "Death Benefit List",
    ["To access the death benefit list, click on the <strong>DEATH BENEFIT LIST</strong> button.",
     "The death benefit list summarizes deceased members' details and their corresponding death benefits received."],
    ["Figure 27.0 Main Page (Accounting System Section)", "Figure 27.1 DEATH BENEFIT PROGRAM PRINTING Page"]))
g.append(guide("XXVIII", "dividend", "Dividend",
    ["To access the dividend page, click the <strong>DIVIDEND</strong> button.",
     "First select the year from the dropdown menu, then click the <strong>SHOW</strong> button in order to proceed.",
     "This page provides for the printing and computation of dividends of the members."],
    ["Figure 28.0 Main Page (Accounting System Section)", "Figure 28.1 KAPAMALQ DIVIDEND Search Query Page", "Figure 28.1.1 KAPAMALQ DIVIDEND Printing Page"]))
g.append(guide("XXIX", "print-dividend-check", "Print Dividend Check",
    ["To access the printing of dividend check page, click the <strong>PRINT DIVIDEND CHECK</strong> button.",
     "Select the YEAR and OFFICE from the dropdown menu.",
     "Click <strong>SHOW</strong> to show the list of members.",
     "Click the <strong>PRINT CHECK</strong> button to print the check of the members."],
    ["Figure 29.0 Main Page (Accounting System Section)", "Figure 29.1 KAPAMALQ DIVIDEND Printing Page"]))
g.append(guide("XXX", "cash-receipt", "Cash Receipt",
    ["To access the cash receipt page, click the <strong>CASH RECEIPT</strong> button.",
     "To start, manually encode all the fields for the cash receipt details.",
     "Once done, click the <strong>ADD CASH RECEIPT</strong> button.",
     "In order to view if the encoded information is correct, select the <strong>MONTH</strong> and <strong>YEAR</strong>, then click <strong>VIEW FULL/VERIFY</strong> to verify the cash receipt.",
     "To export the report, click the <strong>EXPORT</strong> button."],
    ["Figure 30.0 Main Page (Accounting System Section)", "Figure 30.1 CASH RECEIPT Page", "Figure 30.1.1 CASH RECEIPT Printing Section"]))
g.append(guide("XXXI", "edit-cash-receipt", "Edit Cash Receipt",
    ["To access the edit/delete receipt page, click the <strong>EDIT/DELETE RECEIPT</strong> button.",
     "To modify the cash receipt, type in the OR/AR NUMBER or NAME.",
     "Click the <strong>SEARCH</strong> button to proceed. Once there, the user can now modify the details of the Cash Receipt."],
    ["Figure 31.0 Main Page (Accounting System Section)", "Figure 31.1 EDIT CASH RECEIPT Search Query"]))
g.append(guide("XXXII", "cash-disbursement", "Cash Disbursement",
    ["To access the cash disbursement page, click the <strong>CASH DISBURSEMENT</strong> button.",
     "To start, manually encode all the fields for the cash disbursement details.",
     "Once done, click the <strong>ADD DISBURSEMENT</strong> button.",
     "In order to view if the encoded information is correct, select the <strong>MONTH</strong> and <strong>YEAR</strong>, then click <strong>VIEW FULL/VERIFY</strong> to verify the cash disbursement.",
     "To export the report, click the <strong>EXPORT</strong> button."],
    ["Figure 32.0 Main Page (Accounting System Section)", "Figure 32.1 CASH DISBURSEMENT Page", "Figure 32.1.1 CASH DISBURSEMENT Printing Section"]))
g.append(guide("XXXIII", "edit-cash-disbursement", "Edit Cash Disbursement",
    ["To modify the disbursement voucher, type in the DIV NUMBER.",
     "Click the <strong>SEARCH</strong> button to proceed. Once there, the user can now modify the details of the Disbursement Voucher."],
    ["Figure 33.1 EDIT CASH DISBURSEMENT Search Query"]))
g.append(guide("XXXIV", "adjustments", "Adjustments",
    ["To access the adjustments page, click the <strong>ADJUSTMENTS</strong> button.",
     "Select the <strong>MONTH</strong> then <strong>YEAR</strong> from the dropdown menu, then click the <strong>SEARCH</strong> button to continue.",
     "In order to add new other adjustments, manually encode the details then click the <strong>ADD ADJUSTMENT</strong> button. Entries can also be modified by clicking the <strong>EDIT/DELETE</strong> button.",
     "The adjustments will appear at the bottom of the page categorized in three tabs, namely <strong>MEMBERS ADJUSTMENT</strong>, <strong>OFFICE ADJUSTMENT</strong> and <strong>ACCOUNTING ENTRIES</strong>."],
    ["Figure 34.0 Main Page (Accounting System Section)", "Figure 34.1 ADJUSTMENTS Page", "Figure 34.1.1 ADJUSTMENTS Page"]))
g.append(guide("XXXV", "edit-request", "Edit Request",
    ["To access the edit request page, click the <strong>EDIT REQUEST</strong> button.",
     "Select the particulars from the dropdown menu. Encode the remarks for the said particulars.",
     "Click the <strong>SUBMIT REQUEST</strong> button to proceed.",
     "Once done, the accountant will approve the edit request.",
     "After approval, click <strong>DONE</strong>.",
     "For the reporting, select the date covered and then click the <strong>PRINT</strong> button."],
    ["Figure 35.0 Main Page (Accounting System Section)", "Figure 35.1 EDIT REQUEST Page"]))
g.append(guide("XXXVI", "soa-summary", "SOA Summary",
    ["To access the SOA summary page, click the <strong>SOA SUMMARY</strong> button.",
     "Select the <strong>MONTH</strong>, <strong>YEAR</strong> and <strong>SOA TYPE</strong> from the dropdown menu.",
     "Click the <strong>SEARCH</strong> button to continue. This will display the Statement of Accounts of the offices."],
    ["Figure 36.0 Main Page (Accounting System Section)", "Figure 36.1 SOA SUMMARY Page"]))
g.append(guide("XXXVII", "cc-soa", "CC – SOA per Office",
    ["To access the CC SOA per Office page, click the <strong>CC-SOA PER OFFICE</strong> button.",
     "Select the <strong>OFFICE</strong>, <strong>MONTH</strong> and <strong>YEAR</strong> from the dropdown menu.",
     "Click the <strong>SEARCH</strong> button to continue. This will display the Capital Contribution of the members per office."],
    ["Figure 37.0 Main Page (Accounting System Section)", "Figure 37.1 CC-SOA PER OFFICE Summary Page"]))
g.append(guide("XXXVIII", "cl-el-soa", "CL – SOA per Office &amp; EL – SOA per Office",
    ["To access either the CL or EL SOA per Office, click either the <strong>CL</strong> or <strong>EL SOA PER OFFICE</strong> button.",
     "Select the <strong>OFFICE</strong>, <strong>MONTH</strong> and <strong>YEAR</strong> from the dropdown menu.",
     "Click the <strong>SEARCH</strong> button to continue. This will display the details of the members per office that availed the regular loan."],
    ["Figure 38.0 Main Page (Accounting System Section)", "Figure 38.1 REGULAR LOAN – SOA PER OFFICE Summary Page"],
    note="The same process is done in the EL-SOA PER OFFICE page."))
g.append(guide("XXXIX", "create-voucher", "Create Voucher",
    ["To access the create voucher page, click the <strong>CREATE VOUCHER</strong> button.",
     "To create the disbursement voucher, account entries must be encoded manually.",
     "Once done, click the <strong>CALCULATE</strong> button to compute the account entries.",
     "After getting the computation, click the <strong>SAVE</strong> button."],
    ["Figure 39.0 Main Page (Accounting System Section)", "Figure 39.1 CREATE / PRINT DISBURSEMENT VOUCHER Page", "Figure 39.1.1 CREATE / PRINT DISBURSEMENT VOUCHER Page (Cont.)"]))
g.append(guide("XL", "voucher-list", "Voucher List",
    ["To access the voucher list page, click the <strong>VOUCHER LIST</strong> button.",
     "The list/print disbursement voucher page displays and prints the current disbursement vouchers."],
    ["Figure 40.0 Main Page (Accounting System Section)", "Figure 40.1 LIST / PRINT DISBURSEMENT VOUCHER Page"]))
g.append(guide("XLI", "remittance-reports", "Remittance Reports",
    ["To access the remittance reports page, click the <strong>REMITTANCE REPORTS</strong> button.",
     "To display the report for the particular month, click the <strong>SELECT OR NUMBER</strong> dropdown menu. Each OR number represents a particular month.",
     "To add a new remittance, select the desired month, year and OR number. Once done, click the <strong>ADD NEW REMITTANCE</strong> button."],
    ["Figure 41.0 Main Page (Reporting Section)", "Figure 41.1 REMITTANCE REPORTS Page"]))
g.append(guide("XLII", "past-due-reports", "Past Due Reports",
    ["To access the past due reports page, click the <strong>PAST DUE REPORTS</strong> button.",
     "The loan past-due master list shows all the members with their loan past their due dates."],
    ["Figure 42.0 Main Page (Reporting Section)", "Figure 42.1 LOAN PAST-DUE MASTER LIST Page"]))
g.append(guide("XLIII", "trial-balance", "Trial Balance",
    ["To access the trial balance page, click the <strong>TRIAL BALANCE</strong> button.",
     "Select the MONTH and YEAR and click the <strong>SEARCH</strong> button."],
    ["Figure 43.0 Main Page (Reporting Section)", "Figure 43.1 TRIAL BALANCE Page"],
    note="The trial balance displays a summary of all financial transactions per account. The system generates a trial balance that summarizes all recorded financial transactions, including cash receipts, cash disbursements, and journal entries, with corresponding account balances."))
g.append(guide("XLIV", "soa-tb", "SOA of TB Accounts",
    ["To access the SOA of TB Accounts page, click the <strong>SOA of TB ACCOUNTS</strong> button.",
     "The schedule of Trial Balance accounts serves as the reports of the statement of accounts. To view the annual reports, select the desired year and click the <strong>SEARCH</strong> button to proceed."],
    ["Figure 44.0 Main Page (Reporting Section)", "Figure 44.1 SCHEDULE OF TB ACCOUNTS Page"]))
g.append(guide("XLV", "add-account-title", "Add Account Title",
    ["To access the Add Account Title page, click the <strong>ADD ACCOUNT TITLE</strong> button.",
     "To add a new account title, fill out the field manually.",
     "Once done, click the <strong>SAVE</strong> button.",
     "To edit the account title, manually edit the fields and click the <strong>SAVE</strong> button in the update column."],
    ["Figure 45.0 Main Page (Reporting Section)", "Figure 45.1 ADD ACCOUNT TITLE Page"]))
g.append(guide("XLVI", "financial-statements", "Financial Statements",
    ["To access the financial statements page, click the <strong>FINANCIAL STATEMENTS</strong> button.",
     "Select the <strong>MONTH</strong> and <strong>YEAR</strong> from the dropdown menu, then click the <strong>SEARCH</strong> button.",
     "Select from the Consolidated Statement of Condition and print the desired choice."],
    ["Figure 46.0 Main Page (Reporting Section)", "Figure 46.1 FINANCIAL STATEMENTS Page"]))
g.append(guide("XLVII", "payroll", "Payroll",
    ["To access the payroll page, click the <strong>PAYROLL</strong> button.",
     "Select first the period and then the year.",
     "Click the <strong>SEARCH</strong> button to continue."],
    ["Figure 47.0 Main Page (Payroll Section)", "Figure 47.1 PAYROLL REPORTS Page"],
    note="The payroll report is used in order to view the payroll of KAPAMALQ staff."))
g.append(guide("XLVIII", "statement-deductions", "Statement of Deductions",
    ["To access the statement of deductions page, click the <strong>STATEMENT OF DEDUCTIONS</strong> button.",
     "The statement of deductions displays the KAPAMALQ staff and their deductions. To access it, select the period and the year from the dropdown menu.",
     "Click the <strong>SEARCH</strong> button to continue."],
    ["Figure 48.0 Main Page (Payroll Section)", "Figure 48.1 STATEMENT OF DEDUCTIONS Page"]))
g.append(guide("XLIX", "scanned-files", "Scanned Files",
    ["To access the scanned files, click the <strong>SCANNED FILES</strong> button.",
     "The scanned files serve as the digital archive of different documents."],
    ["Figure 49.0 Main Page (Scanned Files Page)", "Figure 49.1 SCANNED FILES Directory Page"]))
g.append(guide("L", "renew-list", "Renew List",
    ["To access the Renew List page, simply click the <strong>RENEW LIST</strong> button.",
     "The renew list displays all the names of members who are planning to renew their existing loans."],
    ["Figure 50.0 Main Page (Bottom Right Section)", "Figure 50.1 RENEW LIST Viewing Page"]))
g.append(guide("LI", "amort-list", "Amort List",
    ["To access the Loan Amort List page, simply click the <strong>LOAN AMORT LIST</strong> button.",
     "To start, select the office and click the <strong>SEARCH</strong> button. The loan amort list will display all the members that have availed either the REGULAR LOAN or EMERGENCY LOAN."],
    ["Figure 51.0 Main Page (Bottom Right Section)", "Figure 51.1 LOAN AMORT LIST Page"]))
g.append(guide("LII", "membership-list", "Membership List",
    ["To access the Membership List page, simply click the <strong>MEMBERSHIP LIST</strong> button.",
     "The membership list page displays all registered members starting from the most recent ones."],
    ["Figure 52.0 Main Page (Bottom Right Section)", "Figure 52.1 MEMBERSHIP LIST Page"]))
g.append(guide("LIII", "kyc-summary", "KYC Summary",
    ["To access the KYC Summary page, simply click the <strong>KYC SUMMARY</strong> button.",
     "The KYC or Know Your Customer Summary is the list of all the members of KAPAMALQ with their respective details."],
    ["Figure 53.0 Main Page (Bottom Right Section)", "Figure 53.1 KYC SUMMARY Page"]))
g.append(guide("LIV", "update-board", "Update Board Members",
    ["To access the update board members page, simply click the <strong>UPDATE BOARD MEMBERS</strong> button.",
     "The UPDATE BOARD MEMBERS page shall be used if there are newly appointed board members. If there are new members, the staff can simply select the position and replace the name. Once done, click the <strong>SAVE</strong> button."],
    ["Figure 54.0 Main Page (Bottom Right Section)", "Figure 54.1 UPDATE BOARD MEMBERS Page"]))
parts.append(sec("using-the-system", "Using the KAPAMALQ System", "".join(g)))

def qa(pairs):
    out = ""
    for q, a in pairs:
        out += f'<div class="qa"><p class="q">Q: {q}</p><div class="a">{a}</div></div>'
    return out

faq = []
faq.append(sub("faq-general", "General Questions", qa([
    ("What is the KAPAMALQ System?", "<p>The KAPAMALQ System is designed to manage core functions such as member loan withdrawals, savings tracking, transaction records, archival of records and loan portfolio oversight. It streamlines administrative and financial tasks for the association.</p>"),
    ("What are the system requirements for installing the KAPAMALQ System?", ul([
        "Operating System: Windows 10 (64-bit) version 1909 or later, or Windows 11",
        "CPU: Intel Core i5 (8th generation or newer) or AMD Ryzen 5 equivalent",
        "Storage: 256GB total capacity (50GB free space recommended)",
        "RAM: 8GB minimum, 16GB recommended",
        "Network: Local Area Network (LAN) with 100 Mbps minimum speed (1 Gbps recommended)"]))])))
faq.append(sub("faq-install", "Installation and Setup", qa([
    ("How do I set up the KAPAMALQ System?", "<p>Refer to the <a href='#installation'>Installation Instructions</a> section in this manual. It includes steps for configuring network settings, installing WampServer, MySQL, and Visual C++ Redistributable, and verifying the setup.</p>"),
    ("What should I do if the WampServer doesn't start?", ol([
        "Check for port conflicts. Ensure no other applications are using the designated port (e.g., 1962).",
        "Verify Apache configuration and make sure all dependencies, like Visual C++ Redistributable, are installed."])),
    ("How do I access the system for the first time?", "<p>After installation, open a web browser and navigate to " + c("http://localhost:1962/") + ". Log in using the credentials provided by your administrator.</p>")])))
faq.append(sub("faq-using", "Using the System", qa([
    ("How do I add a new member?", "<p>Navigate to the \"Members\" section in the system interface and click \"Add Member.\" Fill in the required details and save the entry.</p>"),
    ("How can I process a loan application?", "<p>Go to the \"Transactions\" section and select \"Loan.\" Enter the member details, loan amount, and repayment terms, and then submit for approval.</p>"),
    ("Where can I view all active accounts?", "<p>Use the \"Account Master List\" under the \"Members\" section to access a list of all active accounts.</p>"),
    ("What if an erroneous entry has been made?", "<p>To rectify an erroneous entry, submit an edit request to the system administrator or designated personnel.</p>")])))
faq.append(sub("faq-troubleshooting", "Troubleshooting", qa([
    ("What should I do if I forget my admin password?", "<p>Use the MySQL console to reset the password:</p><pre>UPDATE users SET password=PASSWORD('new_password') WHERE username='admin';</pre><p>Replace <em>new_password</em> with your desired password.</p>"),
    ("I see a \"Database connection failed\" error. How do I fix it?", ol([
        "Ensure the MySQL server is running.",
        "Check that the database credentials in the system configuration match your MySQL setup."])),
    ("My reports are not generating properly. What should I check?", ol([
        "Ensure all required fields are filled before generating reports.",
        "Verify that the system server is operational and error-free."]))])))
faq.append(sub("faq-printing", "Printing and Reporting", qa([
    ("How can I print a member's passbook?", "<p>Navigate to the \"Passbook Printing\" option under the \"Members\" section, select the member's account, and proceed with printing.</p>"),
    ("Why are my reports missing data?", "<p>Incomplete reports often result from missing information in required fields. Verify all inputs before generating the report.</p>")])))
faq.append(sub("faq-performance", "Performance and Optimization", qa([
    ("The system is running slowly. What can I do to improve performance?", ol([
        "Upgrade your hardware to meet the recommended specifications (16GB RAM and 1 Gbps network speed).",
        "Close unnecessary background applications to free system resources."])),
    ("How do I prevent frequent crashes or freezes?", "<p>Regularly clear system logs and backups to free up storage. Ensure your operating system and hardware are up-to-date.</p>")])))
faq.append(sub("faq-maintenance", "Maintenance and Updates", qa([
    ("How do I start WampServer automatically after a system reboot?", "<p>Configure WampServer to run at startup via Task Scheduler or set the Apache and MySQL services to \"Automatic\" in the Services management console.</p>"),
    ("What should I do if data inconsistencies occur after a system update?", ol([
        "Run a database integrity check using MySQL Workbench.",
        "Use the \"Edit Request\" section to review flagged transactions and correct inconsistencies."]))])))
parts.append(sec("faq", "Frequently Asked Questions (FAQ)", "".join(faq)))

def problem(title, cause, solution):
    body = ""
    if cause:
        body += f"<p><strong>Cause:</strong></p>{cause}"
    body += f"<p><strong>Solution:</strong></p>{solution}"
    return f'<div class="qa"><p class="q">Problem: {title}</p><div class="a">{body}</div></div>'

ts = ["<p>This section provides solutions to common issues users may encounter while using the KAPAMALQ System. Follow the steps below to resolve problems effectively.</p>"]
ts.append(sub("ts-install", "1. Common Installation Issues",
    problem("WampServer or MySQL Not Starting",
        ul(["Port conflict with another service.", "Missing dependencies like Visual C++ Redistributable.", "Incorrect configuration."]),
        ol(["Verify that no other service is using the selected port (e.g., 1962): open Command Prompt and run " + c('netstat -a -n -o | find "1962"') + ". If another process is using the port, terminate it or select a different port in the WampServer configuration.",
            "Ensure Visual C++ Redistributable is installed by downloading it from the Microsoft Download Center.",
            "Recheck configuration files — Apache: ensure correct " + c("Listen") + " directives; MySQL: validate database access credentials."])) +
    problem("Unable to Access http://localhost/",
        ul(["Firewall blocking the application.", "Misconfigured network settings."]),
        ol(["Allow Apache Server through the firewall: go to <strong>Windows Security &gt; Firewall &amp; network protection</strong>, click <strong>Allow an app through the firewall</strong> and enable Apache for both Private and Public networks.",
            "Verify network settings: IPv4 Address " + c("192.168.1.111") + ", Subnet Mask " + c("255.255.255.0") + ", Default Gateway " + c("192.168.1.1") + "."]))))
ts.append(sub("ts-login", "2. Login and Account Access Issues",
    problem("Forgot Admin Credentials", None,
        ol(["Open MySQL Console via WampServer.",
            "Run the following command to reset the password:<pre>UPDATE users SET password=PASSWORD('new_password') WHERE username='admin';</pre>",
            "Replace <em>new_password</em> with the desired new password."])) +
    problem("Regular Users Unable to Log In",
        "<p>Inactive user accounts or incorrect credentials.</p>",
        ol(["Log in as an administrator.",
            "Navigate to the \"Members\" section and ensure the user account is active.",
            "Reset user passwords if necessary."]))))
ts.append(sub("ts-system", "3. System Errors",
    problem("PHP Errors or Blank Pages",
        ul(["PHP errors not displayed.", "Configuration issues."]),
        ol(["Enable error reporting in the " + c("php.ini") + " file:<pre>display_errors = On</pre>",
            "Restart WampServer.",
            "Reload the webpage to view error logs and fix issues as indicated."])) +
    problem("\"Database Connection Failed\" Error",
        ul(["MySQL server not running.", "Incorrect database credentials."]),
        ol(["Start MySQL via WampServer.",
            "Confirm credentials in the application configuration file match the MySQL setup."]))))
ts.append(sub("ts-loan", "4. Loan and Transaction Issues",
    problem("Loan Application Details Not Saving",
        ul(["Insufficient user permissions.", "Database configuration issues."]),
        ol(["Verify user roles and permissions in the \"Members\" section.",
            "Check the database table for corruption using MySQL Workbench."])) +
    problem("Incorrect Totals in Loan Summaries", None,
        ol(["Use the \"Post Audit\" functionality to recalculate totals.",
            "Manually verify transaction records for discrepancies."]))))
ts.append(sub("ts-reporting", "5. Reporting and Printing Issues",
    problem("Reports Not Generating or Incomplete", None,
        ol(["Ensure all required fields are completed before submission.",
            "Check server logs for missing data errors."])) +
    problem("Printing Errors in Passbook or Declaration Form", None,
        ol(["Confirm printer settings are correct.",
            "Use the \"Slip Print/Edit/Delete\" functionality to reprint the document."]))))
ts.append(sub("ts-performance", "6. Performance and Optimization",
    problem("System Running Slowly",
        ul(["Insufficient hardware resources."]),
        ol(["Upgrade to recommended specifications: 16GB RAM, 1 Gbps network speed.",
            "Close unnecessary applications to free up resources."])) +
    problem("Frequent Crashes or Freezes", None,
        ol(["Clear unnecessary logs and backups to free up storage space.",
            "Verify that the database server has adequate disk space."]))))
ts.append(sub("ts-maintenance", "7. System Maintenance",
    problem("Unable to Start Services after a Reboot", None,
        ol(["Open Services (" + c("services.msc") + ").",
            "Locate " + c("wampapache64") + " and " + c("wampmysqld64") + ".",
            "Set both services to <strong>Automatic</strong> startup type."])) +
    problem("Data Inconsistency after Updates", None,
        ol(["Run database integrity checks using MySQL Workbench.",
            "Review the \"Edit Request\" section for flagged issues."]))))
ts.append(sub("ts-special-chars", "8. Special Character Issues",
    problem("Special characters cause errors or unexpected behavior",
        "<p>The system may not handle or sanitize certain special characters (e.g., @, #, ', or &amp;) in user inputs or data fields.</p>",
        ol(["Avoid using special characters in input fields unless explicitly allowed (e.g., passwords or specific text fields). Report the specific character causing the issue to the administrator.",
            "Temporary workaround: replace special characters with alternatives or omit them when entering data."]))))
ts.append(sub("ts-contribution", "9. Contribution Adjustment Issue",
    problem("Salary increase affects the contribution, retroactively altering previous salaries and their respective contributions",
        "<p>The system automatically adjusts contributions based on the new salary, even for historical records.</p>",
        ol(["Manually check and verify contributions via the payroll system.",
            "Correct any discrepancies in historical records manually to ensure accurate reporting.",
            "Escalate to the administrator if automated adjustments persist to review and potentially fix system logic."]))))
parts.append(sec("troubleshooting", "Troubleshooting", "".join(ts)))

# --------------------------------------------------------------------- nav
NAV = [
    ("Introduction", "introduction", []),
    ("System Requirements", "system-requirements", []),
    ("Installation Instructions", "installation", [
        ("Prerequisites", "prerequisites"),
        ("Installing WampServer", "installing-wampserver"),
        ("Installing MySQL", "installing-mysql"),
        ("Visual C++ Redistributable", "installing-vcredist"),
        ("Post-Installation Verification", "post-install"),
        ("MySQL Root Password", "root-password"),
        ("Additional Configurations", "additional-config"),
        ("Start WAMP on Boot Up", "start-on-boot")]),
    ("User Interface Overview", "ui-overview", [
        ("Credit / Loaning System", "ui-credit"),
        ("Accounting System", "ui-accounting"),
        ("Payroll System", "ui-payroll"),
        ("Scanned Files", "ui-scanned"),
        ("Remittance", "ui-remittance")]),
    ("Using the System", "using-the-system", [
        ("I. Logging In", "logging-in"),
        ("II. Adding Members", "adding-members"),
        ("III. Updating Member's Profile", "updating-member"),
        ("IV. Edit Account/Name/Office", "edit-account"),
        ("V. View Member Details", "view-member-details"),
        ("VI. Account Master List", "account-master-list"),
        ("VII. Add/Update Co-Maker", "co-maker"),
        ("VIII. Fixed CC & Exceed CC Buffer", "fixed-cc"),
        ("IX. Ex-Member Account", "ex-member"),
        ("X. Passbook Printing", "passbook-printing"),
        ("XI. Loan", "loan"),
        ("XII. Withdrawal Application Form", "withdrawal-form"),
        ("XIII. Withdrawal List", "withdrawal-list"),
        ("XIV. Verification", "verification"),
        ("XV. Edit Transaction", "edit-transaction"),
        ("XVI. Voucher", "voucher"),
        ("XVII. Post Audit", "post-audit"),
        ("XVIII. Approval", "approval"),
        ("XIX. Monitor Status", "monitor-status"),
        ("XX. Check List", "check-list"),
        ("XXI. Regular & Emergency Inquiry", "inquiry"),
        ("XXII. Print EIR", "print-eir"),
        ("XXIII. Declaration Form & Consent Slips", "slips"),
        ("XXIV. Post Remittance", "post-remittance"),
        ("XXV. Check Remittance", "check-remittance"),
        ("XXVI. DB Deduction", "db-deduction"),
        ("XXVII. Death Benefit List", "death-benefit-list"),
        ("XXVIII. Dividend", "dividend"),
        ("XXIX. Print Dividend Check", "print-dividend-check"),
        ("XXX. Cash Receipt", "cash-receipt"),
        ("XXXI. Edit Cash Receipt", "edit-cash-receipt"),
        ("XXXII. Cash Disbursement", "cash-disbursement"),
        ("XXXIII. Edit Cash Disbursement", "edit-cash-disbursement"),
        ("XXXIV. Adjustments", "adjustments"),
        ("XXXV. Edit Request", "edit-request"),
        ("XXXVI. SOA Summary", "soa-summary"),
        ("XXXVII. CC – SOA per Office", "cc-soa"),
        ("XXXVIII. CL & EL – SOA per Office", "cl-el-soa"),
        ("XXXIX. Create Voucher", "create-voucher"),
        ("XL. Voucher List", "voucher-list"),
        ("XLI. Remittance Reports", "remittance-reports"),
        ("XLII. Past Due Reports", "past-due-reports"),
        ("XLIII. Trial Balance", "trial-balance"),
        ("XLIV. SOA of TB Accounts", "soa-tb"),
        ("XLV. Add Account Title", "add-account-title"),
        ("XLVI. Financial Statements", "financial-statements"),
        ("XLVII. Payroll", "payroll"),
        ("XLVIII. Statement of Deductions", "statement-deductions"),
        ("XLIX. Scanned Files", "scanned-files"),
        ("L. Renew List", "renew-list"),
        ("LI. Amort List", "amort-list"),
        ("LII. Membership List", "membership-list"),
        ("LIII. KYC Summary", "kyc-summary"),
        ("LIV. Update Board Members", "update-board")]),
    ("FAQ", "faq", [
        ("General Questions", "faq-general"),
        ("Installation and Setup", "faq-install"),
        ("Using the System", "faq-using"),
        ("Troubleshooting", "faq-troubleshooting"),
        ("Printing and Reporting", "faq-printing"),
        ("Performance", "faq-performance"),
        ("Maintenance and Updates", "faq-maintenance")]),
    ("Troubleshooting", "troubleshooting", [
        ("Installation Issues", "ts-install"),
        ("Login and Account Access", "ts-login"),
        ("System Errors", "ts-system"),
        ("Loan and Transaction Issues", "ts-loan"),
        ("Reporting and Printing", "ts-reporting"),
        ("Performance", "ts-performance"),
        ("System Maintenance", "ts-maintenance"),
        ("Special Characters", "ts-special-chars"),
        ("Contribution Adjustment", "ts-contribution")]),
]

nav_html = ""
for title, sid, subs in NAV:
    nav_html += f'<div class="nav-group"><a class="nav-top" href="#{sid}">{html.escape(title)}</a>'
    if subs:
        nav_html += '<div class="nav-subs">'
        for st, ssid in subs:
            nav_html += f'<a href="#{ssid}">{html.escape(st)}</a>'
        nav_html += "</div>"
    nav_html += "</div>"

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KAPAMALQ System User Manual</title>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<header class="topbar">
  <button id="menu-btn" aria-label="Toggle navigation">&#9776;</button>
  <div class="brand">
    <span class="brand-title">KAPAMALQ System User Manual</span>
    <span class="brand-sub">Kapisanan sa Pag-Iimpok at Paghihiram ng mga Kawani ng Pamahalaang Lungsod Quezon</span>
  </div>
  <input id="search" type="search" placeholder="Search the manual&hellip;" autocomplete="off">
</header>
<div class="layout">
  <nav id="sidebar">{nav_html}</nav>
  <main id="content">
    <div id="search-results" hidden></div>
    {''.join(parts)}
    <footer><p>KAPAMALQ System User Manual &mdash; web edition. Available anywhere, on any device.</p></footer>
  </main>
</div>
<div id="lightbox" hidden><img alt=""><span id="lightbox-close">&times;</span></div>
<script src="assets/app.js"></script>
</body>
</html>
"""

with open(os.path.join(ROOT, "index.html"), "w") as f:
    f.write(page)
print("index.html written,", len(os.listdir(OUT_FIG)), "figures copied")
