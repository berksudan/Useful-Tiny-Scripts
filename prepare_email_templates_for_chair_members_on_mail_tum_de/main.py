"""
This module provides functionality to automate the process of 
preparing and sending draft emails to multiple recipients.

The module includes functions to type Unicode text, prepare draft email content, read 
CSV files with specific headers, prepare multiple draft emails from the CSV data, and 
send multiple draft emails automatically.

Tested with Firefox as the email client.
"""

import csv
from typing import List, Dict
import pyautogui
import pyperclip


# Helper Commands:
# **GET THE CURRENT MOUSE LOCATION:** sleep 5 && xdotool getmouselocation --shell

ATTACHMENTS_DIRPATH_FULL = "/home/iceking/Downloads/email_attachments/"

EMAIL_SUBJECT = "Inquiry about Supervising External Thesis at the {organization_name}"

CSV_FILEPATH = "chair_members.csv"

CSV_HEADER = [
    "organization_type",
    "organization_name",
    "person_name",
    "person_email_address",
    "taken_courses",
]

EMAIL_BODY = """
Dear {person_name},

I am studying "MSc. Data Engineering and Analytics" in the Computer Science department at TUM. Previously, I worked at Siemens AG as a "Data Scientist (Working Student)" for 18 months. I have worked as a Machine Learning Engineer Working Student at Vyoma GmbH since December 2023. I will write my industry thesis on Machine Learning and Computer Vision at Vyoma. The thesis project details from the company have been specified, and we have been working on preparing it for the last couple of months. I kindly require a supervisor and advisor(s) from your {organization_type} to realize the master's thesis project.

## About Me

   My previous full-time positions gave me a comprehensive understanding of machine learning and artificial intelligence. I have worked with various computer vision and machine learning libraries, such as OpenCV, PyTorch, TensorFlow, Scikit-Learn, and Spark MLlib. One can find some of my projects on my GitHub profile and read about my work in my Medium profile. I have completed numerous ML, DL, and AI courses, including "Introduction to Deep Learning," "Machine Learning and IT-Security," "Master's Practical Course (Machine Learning for Natural Language Processing Applications)," and "Business Analytics and Machine Learning."
{email_body_me_and_you_part}
## About the Project (more details in the attached "Project Proposal Draft")

   The purpose of this master's thesis is to explore keypoint regression applied to synthetic Resident Space Object (RSO) streaks in space-based images. Streaks refer to the trails left by fast-moving objects, such as space debris, in long-exposure images. In the context of space observation data, streaks represent the visual traces of these objects as they pass through the field of view of the observation system.

##  About Vyoma

   Vyoma (https://vyoma.space/), a startup specializing in satellite-based observation of space debris, has been recognized as one of the most exciting startups in 2024 and recently secured a significant investment of 8.5 million euros from esteemed investors Safran Corporate Ventures, Atlantic Labs, and Christian Stiebner. The company's commendable track record includes winning multiple awards from the German Aerospace Center (DLR) for its disruptive technology solutions in various categories of satellite competitions. As part of its commitment to delivering groundbreaking solutions and ensuring data sovereignty, Vyoma plans to open an office in the United States soon, expanding its international presence and providing exciting global opportunities.


The draft thesis project proposal, CV, and transcript are attached. I would like to start my master's thesis as soon as possible. Thank you very much for considering my inquiry.

Best Regards,
Berk Sudan
"""

EMAIL_BODY_ME_AND_YOU_PART = """
## About Me + Your {title_case_organization_type}

   I have completed the following courses from your {organization_type}:{taken_courses_str}
"""


def type_unicode(text: str, sleep_pause: float = 2) -> None:
    """
    Function to copy and type Unicode text with specified sleep_pause

    Args:
    text: A string representing the Unicode text to type
    sleep_pause: A float representing the time to pause after typing the text
    """

    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.sleep(sleep_pause)


def prepare_draft_email(
    organization_type: str,
    organization_name: str,
    person_name: str,
    person_email_address: str,
    taken_courses: List[str] | None = None,
) -> None:
    """
    Function to prepare a draft email with specified parameters

    Args:
    organization_type: A string representing the type of organization
    organization_name: A string representing the name of the organization
    person_name: A string representing the name of the person
    person_email_address: A string representing the email address of the person
    taken_courses: A list of strings representing the courses taken by the person (optional)
    """

    attachments_dirpath_full = ATTACHMENTS_DIRPATH_FULL

    email_subject = EMAIL_SUBJECT.format(organization_name=organization_name)

    if taken_courses:  # `taken_courses` is optional, and separated with `;`
        email_body_me_and_you_part = EMAIL_BODY_ME_AND_YOU_PART.format_map(
            {
                "organization_type": organization_type.lower(),
                "title_case_organization_type": organization_type.title(),
                "taken_courses_str": "\n"
                + "\n".join([f"      * {course}" for course in taken_courses]),
            }
        )
    else:
        email_body_me_and_you_part = ""

    email_body = EMAIL_BODY[1:-1].format_map(
        {
            "person_name": person_name,
            "organization_type": organization_type.lower(),
            "email_body_me_and_you_part": email_body_me_and_you_part,
        }
    )

    # Go to Firefox
    pyautogui.press("win")
    pyautogui.sleep(4)
    type_unicode("firefox")
    pyautogui.sleep(4)
    pyautogui.press("enter")
    pyautogui.sleep(3)

    # Open a new tab in Firefox
    pyautogui.hotkey("ctrl", "t")
    pyautogui.sleep(5)

    # Go to "mail.tum.de"
    pyautogui.hotkey("ctrl", "l")
    pyautogui.sleep(5)
    type_unicode("mail.tum.de")
    pyautogui.sleep(5)
    pyautogui.press("enter")
    pyautogui.sleep(5)

    # Create new email
    pyautogui.press("n")
    pyautogui.sleep(4)

    # Attach files
    pyautogui.moveTo(792, 819)
    pyautogui.sleep(2)
    pyautogui.click()
    pyautogui.sleep(4)
    pyautogui.hotkey("ctrl", "l")
    pyautogui.sleep(6)
    type_unicode(attachments_dirpath_full)
    pyautogui.sleep(4)
    pyautogui.press("enter")
    pyautogui.sleep(2)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.sleep(2)
    pyautogui.press("enter")
    pyautogui.sleep(2)

    # Enter recipient email address
    pyautogui.moveTo(777, 335)
    pyautogui.click()
    type_unicode(person_email_address)
    pyautogui.sleep(2)
    pyautogui.press("enter")
    pyautogui.sleep(5)

    # # Enter subject
    pyautogui.moveTo(669, 491)
    pyautogui.click()
    type_unicode(email_subject)
    pyautogui.sleep(5)

    # Enter email body
    pyautogui.moveTo(854, 777)
    pyautogui.click()
    pyautogui.sleep(2)
    type_unicode(email_body)
    pyautogui.sleep(2)

    # Save the email draft
    pyautogui.hotkey("ctrl", "s")


def read_csv(csv_filepath: str, real_csv_header: List[str]) -> List[Dict[str, str]]:
    """
    Function to read a CSV file and validate its content

    Args:
    csv_filepath: A string representing the file path of the CSV
    real_csv_header: A list of strings representing the expected CSV header

    Returns:
    A list of dictionaries, where each dictionary represents a row of the CSV
    """

    # Read CSV
    with open(csv_filepath, newline="", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=",")
        csv_content: List[Dict[str, str]] = list(csv_reader)

    # Validate CSV content
    csv_header = list(csv_content[0].keys())
    assert (
        csv_header == real_csv_header
    ), f"The header should be: {CSV_HEADER}, given: {csv_header}."

    for i, row in enumerate(csv_content):
        assert all(s.strip() != "" for s in row.values()), (
            f"All strings in the csv values must be non-empty, "
            f"however in row #{i+2} given: {row}"
        )

    return csv_content


def prepare_multiple_draft_emails(csv_filepath: str) -> None:
    """
    Function to prepare multiple draft emails from a CSV file

    Args:
    csv_filepath: A string representing the file path of the CSV
    """
    csv_content = read_csv(csv_filepath, real_csv_header=CSV_HEADER)

    for csv_row in csv_content:
        prepare_draft_email(
            organization_type=csv_row["organization_type"],
            organization_name=csv_row["organization_name"],
            person_name=csv_row["person_name"],
            person_email_address=csv_row["person_email_address"],
            taken_courses=(
                None
                if csv_row["taken_courses"] == "None"
                else csv_row["taken_courses"].split(";")
            ),
        )


def send_multiple_draft_emails() -> None:
    """
    Function to send multiple draft emails

    Note: This function interacts with the UI to send the emails,
          so make sure it's setup properly before calling
    """
    print("[INFO] Go to the drafts page, you have 5 seconds!")
    pyautogui.sleep(5)
    while True:
        pyautogui.moveTo(854, 777)
        pyautogui.click()
        pyautogui.hotkey("ctrl", "return")
        pyautogui.sleep(5)


def main():
    """Main function to initiate the process of preparing and sending multiple draft emails"""
    prepare_multiple_draft_emails(csv_filepath=CSV_FILEPATH)
    # send_multiple_draft_emails()


if __name__ == "__main__":
    main()
