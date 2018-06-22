import pytest
import babelfish

"""
@pytest.fixture
def babelfish(request):
    test_babelfish = app.test_babelfish()

    def teardown():
        pass  #  need to be freed later

    request.addfinalizer(teardown)
    return test_babelfish
"""
TEST_FILES = [
    "sample.txt",
    "https://raw.githubusercontent.com/unfetter-discover/unfetter-insight/develop/sample.txt",
    "https://www.f-secure.com/documents/996508/1030745/blackenergy_whitepaper.pdf",
    "https://blogs.technet.microsoft.com/srd/2014/05/13/ms14-025-an-update-for-group-policy-preferences/"
    "http://www.akyl.net/securing-bashhistory-file-make-sure-your-linux-system-users-won%E2%80%99t-hide-or-delete-their-bashhistory",
    "https://en.wikipedia.org/wiki/Command-line_interface",
    "https://www.fireeye.com/blog/threat-research/2014/11/operation_doubletap.html",
    "https://en.wikipedia.org/wiki/Code_signing",
    "https://securelist.com/operation-daybreak/75100/"
    "https://www.clearskysec.com/wp-content/uploads/2017/07/Operation_Wilted_Tulip.pdf",
    "https://en.wikipedia.org/wiki/Server_Message_Block",
    "https://www.cylance.com/content/dam/cylance/pdfs/white_papers/RedirectToSMB.pdf"
    "https://osandamalith.com/2017/03/24/places-of-interest-in-stealing-netntlm-hashes/",
    "https://researchcenter.paloaltonetworks.com/2018/02/unit42-sofacy-attacks-multiple-government-entities/",
    "https://www.f-secure.com/documents/996508/1030745/dukes_whitepaper.pdf",
    "http://www.symantec.com/content/en/us/enterprise/media/security_response/whitepapers/the-elderwood-project.pdf",
    "https://www.slideshare.net/MatthewDunwoody1/no-easy-breach-derby-con-2016",
    "https://www.rsaconference.com/writable/presentations/file_upload/hta-f02-detecting-and-responding-to-advanced-threats-within-exchange-environments.pdf",
    "https://www.brighttalk.com/webcast/10703/296317/apt34-new-targeted-attack-in-the-middle-east",
    "https://www2.fireeye.com/WBNR-Know-Your-Enemy-UNC622-Spear-Phishing.html",
    "https://www.fireeye.com/services.html",
    "https://www.trendmicro.de/cloud-content/us/pdfs/security-intelligence/white-papers/wp-finding-holes-operation-emmental.pdf",
    "https://en.wikipedia.org/wiki/Public-key_cryptography",
    "https://researchcenter.paloaltonetworks.com/2016/06/unit42-prince-of-persia-game-over/",
    "https://www.virusbulletin.com/uploads/pdf/conference/vb2014/VB2014-Wardle.pdf",
    "https://www.crowdstrike.com/blog/mo-shells-mo-problems-deep-panda-web-shells/",
    "https://www.us-cert.gov/ncas/alerts/TA17-293A"
]

VERIFY_RESULTS = [
    ("Test_files/sample.txt", "Bypass User Account Control"),
    ("Test_files/Virtual_Private_Keylogging.htm", "Input Capture"),
    ("Test_files/Microsoft_Security_Intelligence_Report.pdf", "Input Capture"),
    ("Test_files/Sowbug_Cyber_espionage.htm", "Input Capture"),
    ("Test_files/rpt_APT37.pdf", "Drive-by Compromise"),
    ("Test_files/The_Shadowserver_Foundation.htm", "Drive-by Compromise"),
    ("Test_files/Targeted_attacks_SouthAsia.pdf", "Drive-by Compromise"),
    ("Test_files/Elderwood_project.htm", "Drive-by Compromise"),
    ("Test_files/How_User_Account_Control_works.htm", "Bypass User Account Control"),
    ("Test_files/blackenergy_whitepaper.pdf", "Bypass User Account Control"),
    ("Test_files/csmanual38.pdf", "Bypass User Account Control"),
    ("Test_files/Public-key_cryptography.htm", "Private Keys"),
    ("Test_files/Prince_of_Persia.htm", "Private Keys"),
    ("Test_files/Cyber_Security_Services_FireEye.htm", "Two-factor Authentication Interception"),
    ("Test_files/JPCERT_CCBlog.htm", "Two-factor Authentication Interception"),
    ("Test_files/Password_cracking.htm", "Brute Force"),
    ("Test_files/APT3_Adversary_Emulation_Plan.pdf", "Brute Force"),
    ("Test_files/Advanced_Persistent_Threat_Activity.htm", "Brute Force"),
    ("Test_files/Command-line_interface.htm", "Command-Line Interface"),
    ("Test_files/mandiant-apt1-report.pdf", "Command-Line Interface"),
    ("Test_files/tacticstechniquesandprocedures.pdf", "Command-Line Interface")
]

"""
@pytest.mark.parametrize("test_input", TEST_FILES)
def test_classify_report(test_input):
    test_list = babelfish.classify_report(test_input)
    assert len(test_list) != 0

@pytest.mark.parametrize("test_input", TEST_FILES)
def test_tag_report(test_input):
    plot, text = babelfish.plot_report(test_input)
    x = babelfish.tag_report(text, test_input)
    assert len(x) != 0
"""

@pytest.mark.parametrize("files_input,files_output", VERIFY_RESULTS)
def test_classify_report(files_input,files_output):
    test_list = babelfish.classify_report(files_input)
    assert files_output in test_list
