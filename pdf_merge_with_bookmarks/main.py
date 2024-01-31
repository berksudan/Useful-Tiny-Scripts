from PyPDF2 import PdfMerger, PdfReader

OUTPUT_NAME = 'merged_with_bookmarks.pdf'

files = [
  {'file_path':'pdfs/1.00: Soft Skills & Hard Skills.pdf', 'bookmark_name':'1. SOFT SKILLS & HARD SKILLS'},
  {'file_path':'pdfs/1.01: Discover your skills.pdf', 'bookmark_name':'1.01: Discover Your Skills'},
  {'file_path':'pdfs/1.02: Set up your skills profile.pdf', 'bookmark_name':'1.02: Set Up Your Skills Profile'},
  {'file_path':'pdfs/1.03: What are your skills good for.pdf', 'bookmark_name':'1.03: What are Your Skills Good For'},
  {'file_path':'pdfs/1.04: Know your strengths.pdf', 'bookmark_name':'1.04: Know Your Strengths'},
  {'file_path':'pdfs/1.05: Bachelor and now Master.pdf', 'bookmark_name':'1.05: Bachelor and Now Master'},
  {'file_path':'pdfs/1.06: The crowning glory a PhD.pdf', 'bookmark_name':'1.06: The Crowning Glory a PhD'},
  {'file_path':'pdfs/1.07: Start your own business.pdf', 'bookmark_name':'1.07: Start Your Own Business'},
  {'file_path':'pdfs/1.08: Start your own business An entrepreneur tells her story.pdf', 'bookmark_name':'1.08: Start Your Own Business an Entrepreneur Tells Her Story'},
  {'file_path':'pdfs/1.09: Your first job is no one way street.pdf', 'bookmark_name':'1.09: Your First Job is No One Way Street'},
  {'file_path':'pdfs/1.10: This is where I fit in.pdf', 'bookmark_name':'1.10: This is Where I Fit In'},
  {'file_path':'pdfs/2.00: German Job Market.pdf', 'bookmark_name':'2. GERMAN JOB MARKET'},
  {'file_path':'pdfs/2.01: Draw up a plan.pdf', 'bookmark_name':'2.01: Draw Up a Plan'},
  {'file_path':'pdfs/2.02: Where to go in industry.pdf', 'bookmark_name':'2.02: Where to Go in Industry'},
  {'file_path':'pdfs/2.03: Large and powerful or small and innovative.pdf', 'bookmark_name':'2.03: Large and Powerful or Small and Innovative'},
  {'file_path':'pdfs/2.04: From internship to full time finding the job that suits you.pdf', 'bookmark_name':'2.04: From Internship to Full Time Finding the Job That Suits You'},
  {'file_path':'pdfs/2.05: Heres what you should look for an employer.pdf', 'bookmark_name':'2.05: Here\'s What You Should Look for an Employer'},
  {'file_path':'pdfs/2.06: The best channel for your application.pdf', 'bookmark_name':'2.06: The Best Channel for Your Application'},
  {'file_path':'pdfs/2.07: Never lunch alone.pdf', 'bookmark_name':'2.07: Never Lunch Alone'},
  {'file_path':'pdfs/2.08: Getting to know people the easy way.pdf', 'bookmark_name':'2.08: Getting to Know People the Easy Way'},
  {'file_path':'pdfs/2.09: Where the most stimulating jobs are to be found.pdf', 'bookmark_name':'2.09: Where the Most Stimulating Jobs are to be Found'},
  {'file_path':'pdfs/2.10: Online profiles for your job search.pdf', 'bookmark_name':'2.10: Online Profiles for Your Job Search'},
  {'file_path':'pdfs/2.11: Digital trends on the job market.pdf', 'bookmark_name':'2.11: Digital Trends on the Job Market'},
  {'file_path':'pdfs/2.12: Starting a career abroad.pdf', 'bookmark_name':'2.12: Starting a Career Abroad'},
  {'file_path':'pdfs/3.00: CV and Cover Letter.pdf', 'bookmark_name':'3. CV AND COVER LETTER'},
  {'file_path':'pdfs/3.01: The application process.pdf', 'bookmark_name':'3.01: The Application Process'},
  {'file_path':'pdfs/3.02: How to read a job ad.pdf', 'bookmark_name':'3.02: How to Read a Job Ad'},
  {'file_path':'pdfs/3.03: Analyzing the job ad.pdf', 'bookmark_name':'3.03: Analyzing the Job Ad'},
  {'file_path':'pdfs/3.04: What goes into your application.pdf', 'bookmark_name':'3.04: What Goes into Your Application'},
  {'file_path':'pdfs/3.05: Perfect in form and function.pdf', 'bookmark_name':'3.05: Perfect in Form and Function'},
  {'file_path':'pdfs/3.06: Your CV at a glance.pdf', 'bookmark_name':'3.06: Your CV: At a Glance'},
  {'file_path':'pdfs/3.07: Your CV what to put in.pdf', 'bookmark_name':'3.07: Your CV: What to Put In'},
  {'file_path':'pdfs/3.08: Your CV Three sample CVs.pdf', 'bookmark_name':'3.08: Your CV: Three Sample CVS'},
  {'file_path':'pdfs/3.09: Your CV How a recruiter reads it.pdf', 'bookmark_name':'3.09: Your CV: How a Recruiter Reads It'},
  {'file_path':'pdfs/3.10: Your CV good to know.pdf', 'bookmark_name':'3.10: Your CV: Good to Know'},
  {'file_path':'pdfs/3.11: Your CV a crooked one.pdf', 'bookmark_name':'3.11: Your CV: A Crooked One'},
  {'file_path':'pdfs/3.12: Disability or chronic illness.pdf', 'bookmark_name':'3.12: Disability or Chronic Illness'},
  {'file_path':'pdfs/3.13: Starting work with a disability.pdf', 'bookmark_name':'3.13: Starting Work With a Disability'},
  {'file_path':'pdfs/3.14: Your cover letter Three reasons why it is so important.pdf', 'bookmark_name':'3.14: Your Cover Letter: Three Reasons Why it is So Important'},
  {'file_path':'pdfs/3.15: Your cover letter Structuring things logically.pdf', 'bookmark_name':'3.15: Your Cover Letter: Structuring Things Logically'},
  {'file_path':'pdfs/3.16: Your cover letter Not like this.pdf', 'bookmark_name':'3.16: Your Cover Letter: Not Like This'},
  {'file_path':'pdfs/3.17: What to keep in mind when applying by email.pdf', 'bookmark_name':'3.17: What to Keep in Mind When Applying by Email'},
  {'file_path':'pdfs/3.18: Applying by the way of an online form.pdf', 'bookmark_name':'3.18: Applying by the Way of an Online Form'},
  {'file_path':'pdfs/3.19: Seizing the initiative the unsolicited application.pdf', 'bookmark_name':'3.19: Seizing the Initiative the Unsolicited Application'},
  {'file_path':'pdfs/3.20: Your PhD This is why PhD graduates are in such demand.pdf', 'bookmark_name':'3.20: Your PhD: This is Why PhD Graduates are in Such Demand'},
  {'file_path':'pdfs/3.21: Your PhD CVs for PhDs.pdf', 'bookmark_name':'3.21: Your PhD: CVs for PhDs'},
  {'file_path':'pdfs/3.22: Your PhD Starting a job after my PhD.pdf', 'bookmark_name':'3.22: Your PhD: Starting a Job After My PhD'},
  {'file_path':'pdfs/4.00: Job Interview.pdf', 'bookmark_name':'4. JOB INTERVIEW'},
  {'file_path':'pdfs/4.01: Getting to know each other at eye level.pdf', 'bookmark_name':'4.01: Getting to Know Each Other at Eye Level'},
  {'file_path':'pdfs/4.02: Know your way through your interview.pdf', 'bookmark_name':'4.02: Know Your Way Through Your Interview'},
  {'file_path':'pdfs/4.03: Well prepared and ready for the interview.pdf', 'bookmark_name':'4.03: Well Prepared and Ready for the Interview'},
  {'file_path':'pdfs/4.04: How to impress at the job interview and what to avoid at all costs.pdf', 'bookmark_name':'4.04: How to Impress at the Job Interview and What to Avoid at All Costs'},
  {'file_path':'pdfs/4.05: What am I going to say now.pdf', 'bookmark_name':'4.05: What am I Going to Say Now'},
  {'file_path':'pdfs/4.06: Questions and more questions.pdf', 'bookmark_name':'4.06: Questions and More Questions'},
  {'file_path':'pdfs/4.07: Now its all about being spontaneous.pdf', 'bookmark_name':'4.07: Now It\'s All About Being Spontaneous'},
  {'file_path':'pdfs/4.08: What do I ask now.pdf', 'bookmark_name':'4.08: What Do I Ask Now'},
  {'file_path':'pdfs/4.09: Negotiationg my salary for the very first time.pdf', 'bookmark_name':'4.09: Negotiationg My Salary for the Very First Time'},
  {'file_path':'pdfs/4.10: Online interviews.pdf', 'bookmark_name':'4.10: Online Interviews'},
  {'file_path':'pdfs/4.11: The assessment center.pdf', 'bookmark_name':'4.11: The Assessment Center'},
  {'file_path':'pdfs/5.00: Job Entry.pdf', 'bookmark_name':'5. JOB ENTRY'},
  {'file_path':'pdfs/5.01: Employment contracts.pdf', 'bookmark_name':'5.01: Employment Contracts'},
  {'file_path':'pdfs/5.02: Starting a career in Germany.pdf', 'bookmark_name':'5.02: Starting a Career in Germany'},
  {'file_path':'pdfs/5.03: A good start.pdf', 'bookmark_name':'5.03: A Good Start'},
  {'file_path':'pdfs/5.04: Relaxed through the probation period.pdf', 'bookmark_name':'5.04: Relaxed through the Probation Period'},
  {'file_path':'pdfs/5.05: Stay open to opportunities diversions and turnarounds.pdf', 'bookmark_name':'5.05: Stay Open to Opportunities Diversions and Turnarounds'},
  {'file_path':'pdfs/5.06: From engineer to supervisory board member.pdf', 'bookmark_name':'5.06: From Engineer to Supervisory Board Member'},
  {'file_path':'pdfs/6.00: Lifelong Career.pdf', 'bookmark_name':'6. LIFELONG CAREER'},
  {'file_path':'pdfs/6.01: Professional training why is it important.pdf', 'bookmark_name':'6.01: Professional Training: Why is it Important'},
  {'file_path':'pdfs/6.02: Time well spent.pdf', 'bookmark_name':'6.02: Time Well Spent'},
  {'file_path':'pdfs/6.03: Becoming a Manager.pdf', 'bookmark_name':'6.03: Becoming a Manager'},
  {'file_path':'pdfs/6.04: What makes a good manager.pdf', 'bookmark_name':'6.04: What Makes a Good Manager'},
  {'file_path':'pdfs/6.05: Salary negotiation for professionals.pdf', 'bookmark_name':'6.05: Salary Negotiation for Professionals'},
  {'file_path':'pdfs/6.06: Employment references.pdf', 'bookmark_name':'6.06: Employment References'},
  {'file_path':'pdfs/6.07: In word and deed.pdf', 'bookmark_name':'6.07: In Word and Deed'},
]

def get_number_of_pages(pdf_file):
    with open(pdf_file, 'rb') as file:
        pdf_reader = PdfReader(file)
        return len(pdf_reader.pages)

merger = PdfMerger()

current_page_num = 0
for file in files:
  merger.append(file['file_path'])
  merger.add_outline_item(title=str(file['bookmark_name']),pagenum=current_page_num)
  current_page_num += get_number_of_pages(file['file_path'])
merger.write(OUTPUT_NAME)
merger.close()