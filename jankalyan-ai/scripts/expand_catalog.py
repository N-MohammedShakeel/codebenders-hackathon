import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_NAMES = {
    "ka-ssp-postmatric",
    "yuva-nidhi",
    "in-pm-kisan",
    "ka-ganga-kalyana",
    "ka-gruha-lakshmi",
    "ap-ntr-bharosa-pension",
    "kl-egrantz-30",
    "tn-pudhumai-penn",
    "tn-tamil-pudhalvan",
    "tn-women-free-bus-travel",
    "ts-cheyutha",
    "ts-maha-lakshmi",
    "ts-gruha-jyothi",
}

SCHEMES = [
("in-nsp-post-matric-sc", "National Scholarship Portal - Post Matric Scholarship for SC", "All India", "EDUCATION", "Department of Social Justice and Empowerment", "https://scholarships.gov.in/", "Post-matric financial assistance for eligible Scheduled Caste students.", ["Scheduled Caste applicant", "Studying post-matric or post-secondary course", "Family income limit applies; verify category-wise current ceiling", "Admission in an eligible institution"]),
("in-nsp-pre-matric-sc", "National Scholarship Portal - Pre-Matric Scholarship for SC", "All India", "EDUCATION", "Department of Social Justice and Empowerment", "https://scholarships.gov.in/", "Pre-matric support for eligible Scheduled Caste school students.", ["Scheduled Caste applicant", "Studying in a prescribed pre-matric class", "Family income ceiling applies", "Enrolled in a recognized school"]),
("in-nsp-post-matric-obc", "National Scholarship Portal - Post-Matric Scholarship for OBC", "All India", "EDUCATION", "Ministry of Social Justice and Empowerment", "https://scholarships.gov.in/", "Scholarship assistance for eligible OBC students enrolled in post-matric studies.", ["OBC applicant", "Post-matric or post-secondary enrollment", "Income limit applies", "Eligible recognized institution"]),
("in-nsp-pre-matric-obc", "National Scholarship Portal - Pre-Matric Scholarship for OBC", "All India", "EDUCATION", "Ministry of Social Justice and Empowerment", "https://scholarships.gov.in/", "Pre-matric support for eligible OBC students.", ["OBC applicant", "Eligible pre-matric class", "Family income ceiling applies", "Recognized school enrollment"]),
("in-nsp-minority-pre-matric", "Pre-Matric Scholarship for Minorities", "All India", "EDUCATION", "Ministry of Minority Affairs", "https://scholarships.gov.in/", "Scholarship for eligible minority students studying in pre-matric classes.", ["Muslim, Christian, Sikh, Buddhist, Jain or Parsi applicant", "Prescribed pre-matric class", "Family income limit applies"]),
("in-nsp-minority-post-matric", "Post-Matric Scholarship for Minorities", "All India", "EDUCATION", "Ministry of Minority Affairs", "https://scholarships.gov.in/", "Scholarship for eligible minority students pursuing post-matric studies.", ["Minority-community applicant", "Post-matric enrollment", "Family income ceiling applies", "Eligible recognized institution"]),
("in-nsp-means-merit-minority", "Merit-cum-Means Scholarship for Minorities", "All India", "EDUCATION", "Ministry of Minority Affairs", "https://scholarships.gov.in/", "Support for eligible minority students in technical and professional courses.", ["Minority-community applicant", "Technical or professional course", "Income and merit conditions apply", "Eligible institution"]),
("in-pragati-scholarship", "AICTE Pragati Scholarship for Girls", "All India", "EDUCATION", "All India Council for Technical Education", "https://www.aicte-india.org/schemes/students-development-schemes/Pragati", "Financial support for girl students in AICTE-approved technical institutions.", ["Woman applicant", "Admitted to AICTE-approved technical diploma or degree course", "No more than two family members receive the benefit", "Income and course-year conditions apply"]),
("in-saksham-scholarship", "AICTE Saksham Scholarship", "All India", "EDUCATION", "All India Council for Technical Education", "https://www.aicte-india.org/schemes/students-development-schemes/Saksham", "Scholarship support for differently abled students in technical education.", ["Applicant with specified disability", "Enrolled in AICTE-approved technical course", "Income limit applies", "Course and year-of-study conditions apply"]),
("in-swanath-scholarship", "AICTE Swanath Scholarship", "All India", "EDUCATION", "All India Council for Technical Education", "https://www.aicte-india.org/schemes/students-development-schemes/Swanath", "Support for orphans, martial-law casualties and children of armed forces personnel.", ["Eligible special-category applicant", "Diploma or degree admission", "AICTE-approved institution", "Current notification defines supported cases"]),
("in-isha-sud", "Ishan Uday Special Scholarship", "All India", "EDUCATION", "University Grants Commission", "https://www.ugc.gov.in/Page/Scholarship.aspx", "UGC scholarship for eligible students from the North-Eastern Region.", ["Resident of a North-Eastern Region state", "General degree course in an eligible institution", "Family income ceiling applies", "Not covered by a similar UGC scholarship"]),
("in-national-fellowship-sc", "National Fellowship for SC Students", "All India", "EDUCATION", "University Grants Commission", "https://www.ugc.gov.in/oldpdf/schemes/SC_ST.pdf", "Fellowship assistance for SC students pursuing MPhil or PhD research.", ["Scheduled Caste applicant", "MPhil or PhD research enrollment", "Eligible university or institution", "JRF/academic eligibility conditions apply"]),
("in-national-fellowship-obc", "National Fellowship for OBC Students", "All India", "EDUCATION", "University Grants Council", "https://www.ugc.gov.in/Page/Scholarship.aspx", "Fellowship support for eligible OBC students in research degrees.", ["OBC-NCL applicant", "Registered for MPhil or PhD", "UGC or university eligibility conditions apply"]),
("in-nlm-top-class-edn-sc", "Top Class Education Scheme for SCs", "All India", "EDUCATION", "Department of Social Justice and Empowerment", "https://socialjustice.gov.in/schemes/24", "Support for SC students in notified premier institutions.", ["Scheduled Caste applicant", "Admission in a notified premier institution", "Course and annual income ceilings apply", "Current-year notification criteria apply"]),
("in-nlm-top-class-edn-st", "Top Class Education Scheme for STs", "All India", "EDUCATION", "Ministry of Tribal Affairs", "https://tribal.nic.in/", "Support for ST students in notified premier institutions.", ["Scheduled Tribe applicant", "Admission in a listed institution", "Income and course conditions apply"]),
("in-national-overseas-scholarship", "National Overseas Scholarship", "All India", "EDUCATION", "Department of Social Justice and Empowerment", "https://nosmsje.gov.in/", "Support for postgraduate and research study abroad for specified disadvantaged groups.", ["Eligible SC, OBC, EWS, tribal or minority category", "Admission or offer in an eligible foreign institution", "Age and course limits apply", "Income and merit conditions apply"]),
("in-central-sector-top-class", "Central Sector Scheme of Scholarship for College and University Students", "All India", "EDUCATION", "Department of Higher Education", "https://scholarships.gov.in/", "Merit-based scholarships for students enrolled in recognized colleges and universities.", ["Applicant from an eligible school board merit list", "College or university enrollment", "Family income ceiling applies", "No overlapping central scholarship"]),
("in-isingh-prematric-minority", "Begum Hazrat Mahal National Scholarship", "All India", "EDUCATION", "Maulana Azad Education Foundation", "https://maef.nic.in/", "Scholarship for eligible girl students in Classes 9 to 12.", ["Woman applicant", "Studying in Class 9 to 12", "Family income limit applies", "Recognized institution"]),
("in-kishore-vaigyanik", "INSPIRE Scholarship for Higher Education", "All India", "EDUCATION", "Department of Science and Technology", "https://online-inspire.gov.in/", "Scholarship for eligible science students in higher education.", ["Top performance in designated eligibility route", "Natural or basic science course", "Age and course enrollment conditions apply", "Recognized institution"]),
("in-nmms", "National Means-cum-Merit Scholarship", "All India", "EDUCATION", "Department of School Education and Literacy", "https://scholarships.gov.in/", "Scholarship for financially constrained meritorious students from Class 9 to 12.", ["Studying in Class 9 and eligible board examination route", "Income ceiling applies", "State selection/merit criteria apply", "Maintains continuation criteria"]),
("in-inspire-award-manak", "INSPIRE-MANAK Award", "All India", "EDUCATION", "Department of Science and Technology", "https://www.inspireawards-manak.mic.gov.in/", "Recognition and support for student scientific ideas and innovations.", ["Student in eligible school grade", "Innovation proposal submitted through the school", "Nomination and selection process applies"]),
("in-pm-vidyalaxmi", "PM-Vidyalaxmi Education Loan Portal", "All India", "EDUCATION", "Department of Higher Education", "https://pmvidyalaxmi.co.in/", "Portal for education loan support to students in qualifying higher-education institutions.", ["Admission in a qualifying institution", "Education-loan eligibility under participating bank rules", "Course and credit criteria apply"]),
("in-pm-usha", "PM-USHA", "All India", "EDUCATION", "Department of Higher Education", "https://pmusha.gov.in/", "Higher-education infrastructure and quality support implemented through states.", ["Public higher-education institution", "State or institution participation", "Project eligibility is authority-defined"]),

("in-pm-kisan-samman", "PM-KISAN Samman Nidhi", "All India", "AGRICULTURE", "Department of Agriculture and Farmers Welfare", "https://pmkisan.gov.in/", "Direct income support of ₹6,000 per year to eligible farmer families.", ["Eligible landholding farmer family", "Identity and land records verified", "Exclusion and eKYC rules apply"]),
("in-pm-fasal-bima", "Pradhan Mantri Fasal Bima Yojana", "All India", "AGRICULTURE", "Ministry of Agriculture and Farmers Welfare", "https://pmfby.gov.in/", "Crop insurance against notified natural risks.", ["Eligible farmer or loanee farmer", "Cultivating notified crop", "Premium and enrolment deadline apply"]),
("in-pm-krishi-sinchai", "Pradhan Mantri Krishi Sinchai Yojana", "All India", "AGRICULTURE", "Department of Agriculture and Farmers Welfare", "https://pmksy.gov.in/", "Financial support for irrigation and water-management projects.", ["Eligible farmer or implementing entity", "State guidelines and project category apply"]),
("in-pm-kmy", "PM-KMY Pension Scheme", "All India", "AGRICULTURE", "Department of Agriculture and Farmers Welfare", "https://maandhan.in/", "Voluntary pension for eligible small and marginal farmers.", ["Small or marginal farmer", "Age 18 to 40", "Contribution and eKYC conditions apply"]),
("in-kcc", "Kisan Credit Card", "All India", "AGRICULTURE", "Department of Financial Services", "https://www.pmkisan.gov.in/", "Short-term institutional credit for farmers.", ["Farmer, tenant or agricultural worker as eligible", "Land and account records", "Bank credit assessment applies"]),
("in-pm-annadata", "PM Annadata Aay Sanrakshan Abhiyan", "All India", "AGRICULTURE", "Department of Agriculture and Farmers Welfare", "https://pm-aasha.gov.in/", "Price-support and market-intervention measures for specified agricultural produce.", ["Eligible producer", "Notified crop and market", "Scheme implementation conditions apply"]),
("in-soil-health-card", "Soil Health Card Scheme", "All India", "AGRICULTURE", "Department of Agriculture and Farmers Welfare", "https://soilhealth.dac.gov.in/", "Free soil testing and nutrient recommendations for farmers.", ["Registered or eligible farmer", "Field or village sampling schedule", "No fixed cash benefit"]),

("in-ayushman-bharat", "Ayushman Bharat PM-JAY", "All India", "HEALTH", "National Health Authority", "https://pmjay.gov.in/", "Cashless secondary and tertiary health cover for eligible families.", ["SECC or current verified eligibility category", "Family coverage under beneficiary records", "Treatment at empanelled hospital"]),
("in-pm-bima-jyoti", "Pradhan Mantri Jeevan Jyoti Bima Yojana", "All India", "SOCIAL_SECURITY", "Department of Financial Services", "https://www.jansuraksha.gov.in/", "Low-cost term life insurance linked to a bank or post-office account.", ["Age 18 to 50", "Savings account holder", "Annual consent and premium payment"]),
("in-pm-suraksha-bima", "Pradhan Mantri Suraksha Bima Yojana", "All India", "SOCIAL_SECURITY", "Department of Financial Services", "https://www.jansuraksha.gov.in/", "Accidental death and disability insurance linked to a bank account.", ["Age 18 to 70", "Savings account holder", "Annual consent and premium payment"]),
("in-atal-pension", "Atal Pension Yojana", "All India", "SOCIAL_SECURITY", "Pension Fund Regulatory and Development Authority", "https://www.npscra.nsdl.co.in/scheme-details.php", "Guaranteed pension plan for subscribers choosing a pension amount.", ["Age 18 to 40", "Savings bank or post-office account", "Tax and account eligibility rules apply"]),
("in-nps-vatsalya", "NPS Vatsalya", "All India", "SOCIAL_SECURITY", "Pension Fund Regulatory and Development Authority", "https://npstrust.org.in/", "Pension account for minor children opened and managed by a guardian.", ["Minor child", "Registered guardian", "KYC and contribution rules apply"]),
("in-pm-matru-vandana", "Pradhan Mantri Matru Vandana Yojana", "All India", "WOMEN", "Ministry of Women and Child Development", "https://pmmvy.wcd.gov.in/", "Cash support to eligible pregnant and lactating women for wage-loss compensation.", ["Eligible pregnant or lactating woman", "Prescribed first live birth or current notification category", "Mandatory antenatal and registration conditions"]),
("in-pmsby-women", "Mahila Samman Savings Certificate", "All India", "WOMEN", "Department of Economic Affairs", "https://www.indiapost.gov.in/", "Two-year fixed savings scheme for eligible women and girls.", ["Woman or girl minor through guardian", "Scheme deposit limit applies", "Account opened within notified period"]),
("in-saksham-anganwadi", "Saksham Anganwadi and POSHAN 2.0", "All India", "WOMEN_CHILD", "Ministry of Women and Child Development", "https://poshan.ab.gov.in/", "Nutrition, health and early-childhood support through Anganwadi centres.", ["Pregnant woman, lactating mother or eligible child", "Resident in the service area", "Local Anganwadi enrolment"]),
("in-poshan-abhiyaan", "POSHAN Abhiyaan", "All India", "WOMEN_CHILD", "Ministry of Women and Child Development", "https://poshanabhiyaan.gov.in/", "National nutrition programme with services delivered through government systems.", ["Eligible child or woman", "Participating state or ICDS centre"]),
("in-beti-bachao-beti-padhao", "Beti Bachao Beti Padhao", "All India", "WOMEN_CHILD", "Ministry of Women and Child Development", "https://wcd.gov.in/bbbp-scheme", "Awareness and institutional intervention to improve the status of girls.", ["Girl child or family in a participating area", "Benefits and interventions vary by district"]),

("in-pm-awas-rural", "Pradhan Mantri Awaas Yojana - Gramin", "All India", "HOUSING", "Ministry of Rural Development", "https://pmayg.nic.in/", "Housing assistance for eligible rural households.", ["Household absent from the housing beneficiary list", "Rural residence and eligibility data verified", "SECC or state verification applies"]),
("in-pm-awas-urban", "Pradhan Mantri Awaas Yojana - Urban", "All India", "HOUSING", "Ministry of Housing and Urban Affairs", "https://pmay-urban.gov.in/", "Urban housing assistance under multiple mission verticals.", ["Eligible urban household", "Income and property ownership conditions vary by vertical", "Participating project or state process"]),
("in-pm-svanidhi", "PM Street Vendor's AtmaNirbhar Nidhi", "All India", "LIVELIHOOD", "Ministry of Housing and Urban Affairs", "https://pmsvanidhi.mohua.gov.in/", "Working capital loans for eligible street vendors.", ["Urban street vendor", "Local body or state vendor certificate", "Bank credit and prior-loan conditions apply"]),
("in-mudra", "PM MUDRA Yojana", "All India", "LIVELIHOOD", "Department of Financial Services", "https://www.mudra.org.in/", "Collateral-light bank loans for eligible micro-enterprises.", ["Micro or small business applicant", "Bank appraisal and account eligibility", "Loan category under Shishu, Kishor or Tarun"]),
("in-stand-up-india", "Stand-Up India", "All India", "LIVELIHOOD", "Department of Financial Services", "https://www.standupmitra.in/", "Bank loans for eligible SC, ST and women-owned enterprises.", ["SC or ST applicant or woman applicant", "Greenfield enterprise", "Age and loan eligibility conditions apply"]),
("in-pm-kaushal", "PM Kaushal Vikas Yojana", "All India", "EMPLOYMENT", "Ministry of Skill Development and Entrepreneurship", "https://www.pmkvyofficial.org/", "Short-duration industry-oriented skill training and assessment.", ["Applicant in a notified training target group", "Age criteria vary by course", "Enrolled in an affiliated training centre"]),
("in-pm-rozgar-mela", "PM Rozgar Mela Opportunities", "All India", "EMPLOYMENT", "Department of Personnel and Training", "https://dopt.gov.in/pm-rozgar-mela", "Recruitment opportunities for eligible candidates through participating government bodies.", ["Qualification and age requirements vary by post", "Government recruitment rules apply"]),
("in-ddu-gky", "Deen Dayal Upadhyaya Grameen Kaushalya Yojana", "All India", "EMPLOYMENT", "Ministry of Rural Development", "https://ddugky.gov.in/", "Placement-linked skill training for rural youth.", ["Rural youth in the eligible age and income group", "Course and domicile rules apply", "Certified training partner"]),
("in-startup-india", "Startup India", "All India", "ENTREPRENEURSHIP", "Department for Promotion of Industry and Internal Trade", "https://www.startupindia.gov.in/", "Recognition and support ecosystem for eligible startups.", ["Incorporated startup", "Innovative or scalable business model", "Age of entity and turnover limits apply"]),
("in-ncda-disha", "NCDA DISHA", "All India", "WOMEN_ENTREPRENEUR", "National Commission for Women", "https://ncw.nic.in/", "Entrepreneurship guidance and support for women.", ["Woman applicant", "Current scheme or district eligibility", "Participation through designated institutions"]),

("in-ujjwala", "PM Ujjwala Yojana", "All India", "ENERGY", "Ministry of Petroleum and Natural Gas", "https://www.pmuy.gov.in/", "Subsidized LPG connection for eligible women from deprived households.", ["Adult woman in an eligible household", "No existing LPG connection", "SECC or other current eligibility conditions"]),
("in-saubhagya", "Pradhan Mantri Sahaj Bijli Har Ghar Yojana", "All India", "ENERGY", "Ministry of Power", "https://saubhagya.gov.in/", "Household electricity connection support.", ["Eligible un-electrified household", "State utility verification"]),
("in-pm-kusum", "PM-KUSUM", "All India", "ENERGY_AGRICULTURE", "Ministry of New and Renewable Energy", "https://pmkusum.mnre.gov.in/", "Solar pump and renewable-energy support for farmers and agricultural infrastructure.", ["Farmer or implementing entity", "Component and state-distribution rules apply"]),
("in-pm-e-drive", "PM E-DRIVE", "All India", "TRANSPORT", "Ministry of Heavy Industries", "https://heavyindustries.gov.in/", "Demand incentives and charging support for electric mobility.", ["Eligible vehicle or implementing entity", "OEM and state payment rules apply"]),

("in-nilam", "National Livestock Mission", "All India", "LIVESTOCK", "Department of Animal Husbandry and Dairying", "https://dahd.nic.in/nlm", "Support for eligible livestock entrepreneurship and breed development.", ["Eligible farmer or entrepreneur", "Component and state eligibility apply"]),
("in-rkvy", "Rashtriya Krishi Vikas Yojana", "All India", "AGRICULTURE", "Department of Agriculture and Farmers Welfare", "https://rkvy.nic.in/", "State agriculture and allied-sector investment support.", ["State or implementing institution", "Approved project and beneficiary rules"]),

("in-pm-vishwakarma", "PM Vishwakarma", "All India", "ARTISAN", "Ministry of Micro, Small and Medium Enterprises", "https://pmvishwakarma.gov.in/", "Recognition, training, tools and credit support for traditional artisans.", ["Working artisan in an eligible trade", "Family income and current scheme rules apply", "Training and credit stages apply"]),
("in-sfsc", "Scheme for Formalisation of Micro Food Processing Enterprises", "All India", "ENTREPRENEURSHIP", "Ministry of Food Processing Industries", "https://mofpi.gov.in/Schemes/Scheme-of-Formalisation-of-Micro-Food-Processing-Enterprises", "Credit-linked support for eligible micro food-processing units.", ["Existing or proposed micro food-processing enterprise", "Turnover and project eligibility apply"]),
("in-credit-guarantee", "Credit Guarantee Scheme for Micro and Small Enterprises", "All India", "ENTREPRENEURSHIP", "Ministry of Micro, Small and Medium Enterprises", "https://www.cgtmse.in/", "Collateral-free credit guarantee for eligible MSE loans.", ["Eligible MSE borrower", "Participating lending institution", "Account and guarantee terms apply"]),

("in-disha-national-portal", "National Career Service", "All India", "EMPLOYMENT", "Ministry of Labour and Employment", "https://www.ncs.gov.in/", "Job matching, career counselling and training opportunities.", ["Worker or job seeker", "Registration and profile eligibility"]),
("in-e-shram", "e-Shram", "All India", "SOCIAL_SECURITY", "Ministry of Labour and Employment", "https://eshram.gov.in/", "National database and social-security linkage for unorganized workers.", ["Unorganized worker", "Age 16 to 59", "KYC and account eligibility apply"]),

("ap-jagananna-ammavodi", "Jagananna Amma Vodi", "Andhra Pradesh", "EDUCATION", "Government of Andhra Pradesh", "https://gsws-nbm.ap.gov.in/AmmaVodi/", "Financial support for mothers or guardians sending eligible children to school.", ["Government or recognized school enrollment", "Child and guardian records verified", "Attendance and exclusion rules apply"]),
("ap-jagananna-vidya-kanuka", "Jagananna Vidya Kanuka", "Andhra Pradesh", "EDUCATION", "School Education Department, Andhra Pradesh", "https://cse.ap.gov.in/", "Learning kits and school supplies distributed to eligible government-school students.", ["Government-school student", "State education department eligibility"]),
("ap-jagananna-vasathi-deevena", "Jagananna Vasathi Deevena", "Andhra Pradesh", "EDUCATION", "Government of Andhra Pradesh", "https://jnanabhumi.ap.gov.in/", "Boarding and mess support for eligible ITI, polytechnic, degree and professional students.", ["Eligible Andhra resident", "Course and institution category conditions", "Income and attendance criteria apply"]),
("ap-jagananna-videshi-vidya-deevena", "Jagananna Videshi Vidya Deevena", "Andhra Pradesh", "EDUCATION", "Government of Andhra Pradesh", "https://jnanabhumi.ap.gov.in/", "Support for eligible overseas higher education.", ["Andhra Pradesh applicant", "Admission to an approved foreign university", "Course, income and merit conditions apply"]),
("ap-aasara-pension", "Aasara Pension", "Andhra Pradesh", "SOCIAL_SECURITY", "Department of Women, Child and Disabled Welfare", "https://sspensions.ap.gov.in/SSP", "Social-security pension for eligible vulnerable categories.", ["Eligible category and age criteria", "Residency and exclusion rules apply"]),
("ap-ysr-cheyutha", "YSR Cheyutha", "Andhra Pradesh", "WOMEN", "Government of Andhra Pradesh", "https://navasakam2.apcfss.in/", "Financial support for eligible women entrepreneurs and beneficiaries.", ["Age and caste-category criteria", "AP resident", "Income and exclusion rules apply"]),
("ap-ysr-raitu-bharosa", "YSR Rythu Bharosa", "Andhra Pradesh", "AGRICULTURE", "Department of Agriculture, Andhra Pradesh", "https://apagrisnet.gov.in/", "Investment support for eligible farmers.", ["Eligible cultivator", "Land or tenant records", "Exclusion and eKYC rules apply"]),
("ap-ysr-zero-interest-loan", "YSR Zero Interest Crop Loan", "Andhra Pradesh", "AGRICULTURE", "Government of Andhra Pradesh", "https://apagrisnet.gov.in/", "Interest relief on eligible crop-loan advances.", ["Eligible farmer", "Kisan Credit Card or bank crop-loan account", "Repayment and state rules apply"]),
("ap-pm-house-eligibility", "Pedalandariki Illu", "Andhra Pradesh", "HOUSING", "Government of Andhra Pradesh", "https://navasakam2.apcfss.in/", "Housing support for eligible landless poor households.", ["Eligible household", "Land and income verification", "State housing eligibility list"]),

("ka-bhagya-lakshmi", "Bhagya Lakshmi Scheme", "Karnataka", "WOMEN_CHILD", "Department of Women and Child Development, Karnataka", "https://karnataka.gov.in/", "Insurance-linked support for eligible girl children.", ["Below-poverty-line family", "Girl-child registration under the scheme", "Birth and scheme-continuation rules apply"]),
("ka-matsya-sahaya", "Matsya Athri Scheme", "Karnataka", "LIVELIHOOD", "Department of Fisheries, Karnataka", "https://fisheries.karnataka.gov.in/", "Support for eligible fishing communities.", ["Registered fishing beneficiary", "Income and category rules vary", "Fishery department conditions apply"]),
("ka-rajiv-gandhi-scheme", "Rajiv Gandhi Rural Housing Scheme", "Karnataka", "HOUSING", "Rajiv Gandhi Housing Corporation", "https://ashraya.karnataka.gov.in/", "Housing assistance for eligible rural households.", ["Income and housing-deficiency criteria", "Resident of Karnataka", "Beneficiary list and category rules apply"]),
("ka-samanya-pension", "Karnataka State Old Age Pension", "Karnataka", "SOCIAL_SECURITY", "Department of Social Welfare, Karnataka", "https://sevasindhuservices.karnataka.gov.in/", "Monthly pension for eligible senior citizens.", ["Age and category criteria", "Income and residency rules apply", "Exclusion and bank verification apply"]),
("ka-raita-shakti", "Karnataka Raita Shakti", "Karnataka", "WOMEN_AGRICULTURE", "Department of Agriculture, Karnataka", "https://raitamitra.karnataka.gov.in/", "Support and training for eligible women farmers.", ["Woman farmer", "Land or cultivation records", "Program and district eligibility apply"]),
("ka-vidya-siri", "Vidyasiri", "Karnataka", "EDUCATION", "Department of Backward Classes Welfare, Karnataka", "https://bcwd.karnataka.gov.in/", "Hostel, accommodation or maintenance support for eligible students.", ["Eligible caste or backward-class category", "Post-matric course", "Income and institution criteria apply"]),

("kl-karunya-aram", "Karunya Arogya Suraksha Padhathi", "Kerala", "HEALTH", "Government of Kerala", "https://sha.kerala.gov.in/", "State health-insurance support for eligible families.", ["Resident and category eligibility", "Family beneficiary records", "Empanelled-hospital rules apply"]),
("kl-karunya-benevolent", "Karunya Benevolent Fund", "Kerala", "HEALTH", "Government of Kerala", "https://sha.kerala.gov.in/", "Financial support for eligible high-cost medical treatment.", ["Medical need and diagnosis", "Income and state eligibility", "Application and hospital verification apply"]),
("kl-youth-welfare-fellowship", "Kerala State Youth Welfare Board Fellowship", "Kerala", "EMPLOYMENT", "Kerala State Youth Welfare Board", "https://ksywb.kerala.gov.in/", "Youth scholarship or fellowship support for eligible programmes.", ["Kerala youth applicant", "Age and programme conditions", "Institution or project selection"]),
("kl-aswasakiranam", "Aswasakiranam", "Kerala", "SOCIAL_SECURITY", "Social Justice Department, Kerala", "https://sjd.kerala.gov.in/", "Monthly assistance to eligible caregivers of dependent persons.", ["Primary caregiver", "Dependent person's disability or disease category", "Income and residency criteria apply"]),
("kl-snehasparsham", "Snehasparsham", "Kerala", "SOCIAL_SECURITY", "Government of Kerala", "https://sjd.kerala.gov.in/", "Support for eligible socially vulnerable applicants.", ["Residency and category criteria", "Medical or economic need", "State verification applies"]),
("kl-education-support", "Vidya Nagaram Education Support", "Kerala", "EDUCATION", "Government of Kerala", "https://kerala.gov.in/", "Education support for eligible students through state programmes.", ["Kerala resident", "Course and income criteria vary", "Institution or district verification"]),

("tn-kalaignar-magalir", "Kalaignar Magalir Urimai Thogai", "Tamil Nadu", "WOMEN", "Government of Tamil Nadu", "https://www.tn.gov.in/", "Monthly assistance for eligible women heads of rural and urban families.", ["Woman head of eligible household", "Ration-card and beneficiary verification", "Exclusion and income rules apply"]),
("tn-first-graduate-tuition", "Tamil Nadu First Graduate Tuition Fee Concession", "Tamil Nadu", "EDUCATION", "Department of Higher Education, Tamil Nadu", "https://www.tneaonline.org/", "Tuition-fee concession for eligible first-generation graduates.", ["First graduate in the family", "Course and institution eligibility", "Certificate and admission rules apply"]),
("tn-minority-scholarship", "Tamil Nadu Minority Scholarship", "Tamil Nadu", "EDUCATION", "Adi Dravidar and Tribal Welfare Department", "https://www.tnsocialwelfare.tn.gov.in/", "Scholarship support for eligible minority and disadvantaged students.", ["Eligible community category", "Course, income and attendance criteria", "State or central notification rules"]),
("tn-muthulakshmi-reddy", "Dr Muthulakshmi Reddy Maternity Benefit", "Tamil Nadu", "WOMEN_CHILD", "Tamil Nadu Health and Family Welfare", "https://tnhealth.tn.gov.in/", "Cash support for eligible pregnant women.", ["Tamil Nadu resident", "Pregnancy registration and antenatal rules", "Birth and bank-account verification"]),
("tn-free-bus-travel", "Free Bus Travel for Women", "Tamil Nadu", "WOMEN_TRANSPORT", "Government of Tamil Nadu", "https://www.tnstc.in/", "Free ordinary bus travel for eligible women and transgender persons.", ["Woman or transgender passenger", "Ordinary-fare state bus", "Ticket or zero-fare rules"]),
("tn-chief-minister-health-insurance", "Chief Minister's Comprehensive Health Insurance", "Tamil Nadu", "HEALTH", "Tamil Nadu Health Systems Project", "https://www.cmchistn.com/", "Cashless health insurance for eligible families.", ["Income or eligibility category", "Resident and family-ration records", "Empanelled hospital and procedure rules"]),
("tn-fisherman-assistance", "Tamil Nadu Fishermen Relief and Assistance", "Tamil Nadu", "AGRICULTURE", "Department of Fisheries, Tamil Nadu", "https://fisheries.tn.gov.in/", "Relief support during fishing bans or disasters for eligible fishermen.", ["Registered fishing beneficiary", "Current notification and fishing record", "Disaster or ban-period rules"]),

("ts-thalliki-vandanam", "Talliki Vandhanam", "Telangana", "EDUCATION", "Government of Telangana", "https://telangana.gov.in/", "Student support assistance announced by the Telangana government.", ["Eligible student and parent", "Income and school records", "Implementation notification applies"]),
("ts-telanganalu-pension", "Telangana Aasara Pension", "Telangana", "SOCIAL_SECURITY", "Government of Telangana", "https://tg.meeseva.telangana.gov.in/", "Pension for eligible vulnerable and elderly residents.", ["Age or category criterion", "Telangana residency", "Income and exclusion rules"]),
("ts-kalyana-lakshmi", "Kalyana Lakshmi / Shaadi Mubarak", "Telangana", "WOMEN", "Government of Telangana", "https://telanganaepass.cgg.gov.in/", "Marriage financial assistance for eligible brides.", ["Eligible caste category or one-time notification", "Age and income criteria", "Marriage and residence verification"]),
("ts-rythu-bandhu", "Rythu Bandhu", "Telangana", "AGRICULTURE", "Department of Agriculture, Telangana", "https://rythubandhu.telangana.gov.in/", "Investment support to eligible Telangana farmers.", ["Eligible landholder", "Land and state records", "Exclusion and season rules apply"]),
("ts-rythu-bima", "Rythu Bima", "Telangana", "AGRICULTURE", "Department of Agriculture, Telangana", "https://rythubima.telangana.gov.in/", "Insurance support for eligible farmers.", ["Eligible farmer aged within scheme limits", "Land and nominee records", "Death and claim rules apply"]),
("ts-dharani-subsidy", "Telangana Agricultural Subsidy and Input Support", "Telangana", "AGRICULTURE", "Government of Telangana", "https://agri.telangana.gov.in/", "Agricultural input and subsidy support through state systems.", ["Eligible farmer", "Crop and land verification", "Current notification rules"]),
("ts-rajiv-arogyasri", "Rajiv Aarogyasri", "Telangana", "HEALTH", "Government of Telangana", "https://aarogyasri.telangana.gov.in/", "Health coverage for eligible low-income families.", ["Family eligible under state criteria", "Treatment at network hospital", "Procedure and package conditions"]),
("ts-nirudyoga-bruthi", "Telangana Skill and Employment Support", "Telangana", "EMPLOYMENT", "Government of Telangana", "https://telanganalabour.telangana.gov.in/", "State employment, labour or allowance support for eligible applicants.", ["Age and residency criteria", "Employment status", "Current notification terms"]),
]

def make_scheme(item):
    sid, name, state, category, department, portal, benefit, criteria = item
    return {
        "id": sid,
        "nameEn": name,
        "nameKn": name,
        "nameHi": name,
        "department": department,
        "state": state,
        "category": category,
        "lastVerifiedDate": "2026-11-22",
        "officialPortalUrl": portal,
        "sourceUrls": [portal],
        "helpline": "Verify current helpline on the official portal",
        "benefitSummaryEn": benefit,
        "benefitSummaryKn": benefit,
        "benefitSummaryHi": benefit,
        "annualValueINR": None,
        "deadline": "Check current official notification",
        "eligibilityMode": "MANUAL_REVIEW",
        "eligibilityNoteEn": "Eligibility depends on the current official notification. Confirm age, income, caste/category, education, disability, employment and document conditions directly with the issuing authority.",
        "eligibilityCriteria": [
            {"id": f"crit-{index + 1}", "group": "GENERAL", "criterionEn": criterion}
            for index, criterion in enumerate(criteria)
        ],
        "rules": [],
        "requiredDocuments": [],
        "applicationStepsEn": ["Open the official source.", "Check the current eligibility notification and deadline.", "Prepare the required documents.", "Apply through the designated portal or office.", "Keep the acknowledgement and verify status on the official system."],
        "applicationStepsKn": ["ಅಧಿಕೃತ ಮೂಲವನ್ನು ತೆರೆಯಿರಿ.", "ಪ್ರಸ್ತುತ ಅರ್ಹತೆ ಪ್ರಕಟಣೆ ಮತ್ತು ದಿನಾಂಕವನ್ನು ಪರಿಶೀಲಿಸಿ.", "ಅಗತ್ಯ ದಾಖಲೆಗಳನ್ನು ಸಿದ್ಧಪಡಿಸಿ.", "ನಿಗದಿತ ಪೋರ್ಟಲ್ ಅಥವಾ ಕಛೇರಿಯಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.", "ಸ್ವೀಕೃತಿ保存ಿಸಿ ಮತ್ತು ಅಧಿಕೃತ ವ್ಯವಸ್ಥೆಯಲ್ಲಿ ಸ್ಥಿತಿಯನ್ನು ಪರಿಶೀಲಿಸಿ."],
        "applicationStepsHi": ["आधिकारिक स्रोत खोलें।", "वर्तमान पात्रता अधिसूचना और अंतिम तिथि सत्यापित करें।", "आवश्यक दस्तावेज तैयार करें।", "निर्धारित पोर्टल या कार्यालय से आवेदन करें।", "पावती सुरक्षित रखें और आधिकारिक प्रणाली पर स्थिति जांचें।"],
    }


def main():
    if len(SCHEMES) != 97:
        raise RuntimeError(f"Expected 97 additions, found {len(SCHEMES)}")

    additions = [make_scheme(item) for item in SCHEMES]
    ids = [entry["id"] for entry in additions]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate generated scheme IDs")

    for relative in (
        Path("api/data/schemes.json"),
        Path("frontend/src/data/schemes.json"),
    ):
        path = ROOT / relative
        base = json.loads(path.read_text(encoding="utf-8"))
        existing_by_id = {entry["id"]: entry for entry in base}
        generated_by_id = {entry["id"]: entry for entry in additions}
        existing_ids = set(existing_by_id)
        generated_ids = set(generated_by_id)
        merged = [
            generated_by_id.get(entry["id"], entry)
            for entry in base
        ]
        merged.extend(
            generated_by_id[scheme_id]
            for scheme_id in generated_ids - existing_ids
        )
        for entry in merged:
            if entry.get("eligibilityMode") == "MANUAL_REVIEW":
                entry["sourceUrls"] = list(dict.fromkeys(
                    entry.get("sourceUrls") or [entry.get("officialPortalUrl")]
                ))
                if not entry.get("eligibilityCriteria"):
                    note = entry.get("eligibilityNoteEn") or (
                        "Eligibility depends on the current official notification."
                    )
                    entry["eligibilityCriteria"] = [{
                        "id": "crit-general",
                        "group": "GENERAL",
                        "criterionEn": note,
                    }]
        path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: {len(base)} -> {len(merged)} schemes")

if __name__ == "__main__":
    main()
