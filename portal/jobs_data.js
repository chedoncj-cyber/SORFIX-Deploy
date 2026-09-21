// Live job listings data — sourced from company careers pages (May 2026)
// Each entry: { id, title, dept, location, type, posted, deadline, summary }

const JOBS_DATA = {

  // ── GSE — Ghana ─────────────────────────────────────────────────────────────
  GCB: [
    { id:'GCB-001', title:'Graduate Trainee — Retail Banking',       dept:'Retail Banking',   location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-10', deadline:'2026-06-20', summary:'GCB Bank's annual graduate intake. Rotational programme covering branch operations, credit, and digital banking. Open to recent graduates (min 2:2).' },
    { id:'GCB-002', title:'Relationship Manager — Corporate Banking', dept:'Corporate Banking',location:'Kumasi, Ghana',     type:'Full-time', posted:'2026-05-05', deadline:'2026-06-15', summary:'Manage a portfolio of corporate clients, drive revenue growth, and provide tailored financial solutions. 3+ yrs banking experience required.' },
    { id:'GCB-003', title:'IT Security Analyst',                      dept:'Technology',       location:'Accra, Ghana',     type:'Full-time', posted:'2026-04-28', deadline:'2026-06-10', summary:'Monitor and protect GCB's digital infrastructure. Experience with SIEM tools, penetration testing, and ISO 27001 preferred.' },
    { id:'GCB-004', title:'Credit Risk Analyst',                      dept:'Risk Management',  location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-12', deadline:'2026-06-25', summary:'Assess credit applications, build risk models, and maintain credit policy compliance. CFA or FRM qualification an advantage.' },
    { id:'GCB-005', title:'Digital Banking Product Officer',          dept:'Digital Banking',  location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-18', deadline:'2026-07-01', summary:'Drive GCB\'s digital transformation by managing mobile and internet banking products. Agile product management experience needed.' },
  ],
  MTNGH: [
    { id:'MTNGH-001', title:'Network Infrastructure Engineer',        dept:'Technology',       location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-15', deadline:'2026-06-30', summary:'Plan, deploy and optimise MTN Ghana's 4G/5G radio access network. CCNP or equivalent required. Experience with Huawei/Ericsson RAN solutions preferred.' },
    { id:'MTNGH-002', title:'Mobile Money Product Manager',           dept:'Mobile Financial Services', location:'Accra, Ghana', type:'Full-time', posted:'2026-05-08', deadline:'2026-06-22', summary:'Lead MoMo product roadmap, partnerships, and go-to-market strategy. 5+ yrs fintech or telco product management experience.' },
    { id:'MTNGH-003', title:'Data Scientist — Customer Analytics',    dept:'Analytics',        location:'Accra, Ghana',     type:'Full-time', posted:'2026-04-30', deadline:'2026-06-15', summary:'Build ML models to drive customer retention, churn prediction, and personalised offers. Python/R, SQL and experience with big data platforms required.' },
    { id:'MTNGH-004', title:'Corporate Sales Executive',              dept:'Enterprise Business', location:'Tema, Ghana',   type:'Full-time', posted:'2026-05-20', deadline:'2026-07-05', summary:'Acquire and manage large enterprise accounts, selling MTN connectivity, cloud, and IoT solutions. B2B sales track record essential.' },
  ],
  GGBL: [
    { id:'GGBL-001', title:'Brand Manager — Guinness',                dept:'Marketing',        location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-12', deadline:'2026-06-28', summary:'Lead brand strategy, campaigns, and consumer insights for the Guinness portfolio in Ghana. FMCG brand management experience required.' },
    { id:'GGBL-002', title:'Trade Marketing Executive',               dept:'Commercial',       location:'Kumasi, Ghana',    type:'Full-time', posted:'2026-05-06', deadline:'2026-06-20', summary:'Execute in-outlet activation, visibility, and promotion programmes across the Southern Ghana region.' },
    { id:'GGBL-003', title:'Brewery Engineer — Utilities',            dept:'Supply Chain',     location:'Achimota, Ghana',  type:'Full-time', posted:'2026-04-22', deadline:'2026-06-10', summary:'Operate and maintain steam, compressed air, and refrigeration systems at the Achimota brewery. HND/BSc Mechanical or Chemical Engineering.' },
  ],
  EGL: [
    { id:'EGL-001', title:'Investment Analyst',                       dept:'Finance',          location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Support portfolio analysis, valuations and reporting across EGL\'s insurance, asset management, and healthcare subsidiaries. CFA Level II+ preferred.' },
    { id:'EGL-002', title:'Business Development Manager — Insurance', dept:'Insurance',        location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-03', deadline:'2026-06-18', summary:'Grow the retail and corporate insurance book through agent channels and direct sales. 4+ yrs insurance industry experience.' },
  ],
  CAL: [
    { id:'CAL-001', title:'Graduate Trainee — Commercial Banking',    dept:'Commercial Banking', location:'Accra, Ghana',   type:'Full-time', posted:'2026-05-17', deadline:'2026-07-01', summary:'Competitive two-year trainee programme with rotations across corporate, trade finance and treasury. Strong academic record required.' },
    { id:'CAL-002', title:'Treasury Dealer',                          dept:'Treasury',         location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Execute FX and money market trades, manage liquidity positions and correspondent banking relationships. ACI Dealing Certificate preferred.' },
    { id:'CAL-003', title:'Compliance Officer',                       dept:'Compliance',       location:'Accra, Ghana',     type:'Full-time', posted:'2026-04-25', deadline:'2026-06-12', summary:'Ensure adherence to Bank of Ghana regulations, AML/CFT policies, and internal control frameworks. Legal or banking background essential.' },
  ],
  FML: [
    { id:'FML-001', title:'Sales Representative — Northern Regions',  dept:'Sales',            location:'Tamale, Ghana',    type:'Full-time', posted:'2026-05-11', deadline:'2026-06-25', summary:'Drive Fan Milk distributor sales and route-to-market coverage across the Northern, Upper East and Upper West regions.' },
    { id:'FML-002', title:'Quality Assurance Technician',             dept:'Operations',       location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-02', deadline:'2026-06-16', summary:'Maintain production quality standards, conduct in-process and finished product testing at the Fan Milk plant. HND Food Science or equivalent.' },
  ],
  SOGEGH: [
    { id:'SOGEGH-001', title:'Retail Banking Officer',                dept:'Retail Banking',   location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Serve individual and SME clients, cross-sell banking products, and achieve assigned deposit and lending targets.' },
    { id:'SOGEGH-002', title:'IT Applications Developer',             dept:'Technology',       location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-07', deadline:'2026-06-21', summary:'Develop and support core banking application integrations. Java/Spring Boot and Oracle DB experience required.' },
  ],
  GOIL: [
    { id:'GOIL-001', title:'Petroleum Engineer',                      dept:'Operations',       location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Oversee bulk fuel storage, distribution planning, and station network technical operations. BSc Petroleum or Chemical Engineering.' },
    { id:'GOIL-002', title:'Health Safety & Environment Officer',     dept:'HSE',              location:'Tema, Ghana',      type:'Full-time', posted:'2026-04-29', deadline:'2026-06-15', summary:'Implement GOIL\'s HSE management system, conduct site audits, and maintain incident reporting. NEBOSH certificate required.' },
  ],
  SCB: [
    { id:'SCB-001', title:'International Graduate Programme — Ghana', dept:'Graduate Talent',  location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-01', deadline:'2026-06-15', summary:'Standard Chartered\'s global graduate programme with rotations across wholesale banking, retail, and risk. Top graduates from any discipline welcomed.' },
    { id:'SCB-002', title:'Client Coverage Analyst — Wholesale Banking', dept:'Wholesale Banking', location:'Accra, Ghana', type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Support senior bankers in origination, deal execution, and client relationship management for corporate and institutional clients.' },
    { id:'SCB-003', title:'Financial Crime Compliance Manager',       dept:'Compliance',       location:'Accra, Ghana',     type:'Full-time', posted:'2026-04-20', deadline:'2026-06-08', summary:'Lead AML, sanctions, and anti-bribery compliance activities for Standard Chartered Ghana. 5+ yrs financial crime experience.' },
  ],
  TOTAL: [
    { id:'TOTAL-001', title:'Retail Network Engineer',               dept:'Retail',           location:'Accra, Ghana',     type:'Full-time', posted:'2026-05-10', deadline:'2026-06-24', summary:'Manage construction and maintenance of TotalEnergies Ghana\'s service station network. Civil engineering background preferred.' },
    { id:'TOTAL-002', title:'HSSE Coordinator',                      dept:'Safety',           location:'Tema, Ghana',      type:'Full-time', posted:'2026-05-04', deadline:'2026-06-18', summary:'Coordinate health, safety, security, and environmental activities across depot and retail operations. NEBOSH IGC essential.' },
    { id:'TOTAL-003', title:'Commercial Sales Representative',        dept:'Lubricants & B2B', location:'Accra, Ghana',     type:'Full-time', posted:'2026-04-26', deadline:'2026-06-12', summary:'Grow lubricants and fuels revenue with industrial and transport fleet clients. Clean driving licence required.' },
  ],

  // ── JSE — South Africa ───────────────────────────────────────────────────────
  NPN: [
    { id:'NPN-001', title:'Data Engineer — eCommerce Platforms',     dept:'Technology',       location:'Cape Town, South Africa', type:'Full-time', posted:'2026-05-15', deadline:'2026-06-30', summary:'Build data pipelines supporting Naspers\' global ecommerce portfolio. Experience with Spark, dbt, and cloud data warehouses required.' },
    { id:'NPN-002', title:'M&A Analyst — Ventures',                  dept:'Corporate Development', location:'Cape Town, South Africa', type:'Full-time', posted:'2026-05-08', deadline:'2026-06-22', summary:'Support deal origination, due diligence, and portfolio monitoring across Naspers\' technology investment portfolio.' },
    { id:'NPN-003', title:'Group Financial Reporting Manager',        dept:'Finance',          location:'Cape Town, South Africa', type:'Full-time', posted:'2026-04-30', deadline:'2026-06-15', summary:'Lead IFRS financial reporting for the Naspers group. CA(SA) or equivalent with listed-company reporting experience essential.' },
  ],
  BHP: [
    { id:'BHP-001', title:'Mining Engineer — Operations',            dept:'Operations',       location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-12', deadline:'2026-06-28', summary:'Support open-cut and underground mining operations, production planning, and continuous improvement initiatives. BSc Mining Engineering required.' },
    { id:'BHP-002', title:'Safety & Health Advisor',                 dept:'Health & Safety',  location:'Rustenburg, South Africa',  type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Drive safety culture and compliance across BHP South Africa sites. COMSOC 2 or equivalent safety qualification required.' },
    { id:'BHP-003', title:'Graduate Programme — Engineering',        dept:'Graduate Talent',  location:'Perth (relocation supported)', type:'Full-time', posted:'2026-05-01', deadline:'2026-06-14', summary:'BHP\'s 18-month graduate programme placing engineers across mining, processing, and maintenance disciplines worldwide.' },
    { id:'BHP-004', title:'Environmental Advisor',                   dept:'Sustainability',   location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-04-25', deadline:'2026-06-10', summary:'Manage environmental monitoring, permit compliance, and community engagement for BHP South Africa operations. BSc Environmental Science.' },
  ],
  AGL: [
    { id:'AGL-001', title:'Geotechnical Engineer',                   dept:'Engineering',      location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Provide geotechnical design and monitoring support for Anglo American\'s open-pit and underground operations. MEng Geotechnical preferred.' },
    { id:'AGL-002', title:'Community Relations Manager',             dept:'Social Performance', location:'Limpopo, South Africa', type:'Full-time', posted:'2026-05-07', deadline:'2026-06-22', summary:'Lead community investment, social impact measurement, and stakeholder engagement at the Mogalakwena complex.' },
    { id:'AGL-003', title:'Process Metallurgist',                    dept:'Processing',       location:'North West, South Africa', type:'Full-time', posted:'2026-04-28', deadline:'2026-06-12', summary:'Optimise processing plant performance and metallurgical recovery. BSc Metallurgy or Chemical Engineering required.' },
    { id:'AGL-004', title:'ESG Reporting Analyst',                   dept:'Sustainability',   location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-18', deadline:'2026-07-04', summary:'Consolidate ESG data, prepare sustainability reports (GRI, TCFD, ISSB), and support investor relations on sustainability topics.' },
  ],
  SOL: [
    { id:'SOL-001', title:'Chemical Process Engineer',               dept:'Operations',       location:'Secunda, South Africa', type:'Full-time', posted:'2026-05-16', deadline:'2026-07-01', summary:'Optimise Sasol\'s world-scale CTL and GTL process units. BSc Chemical Engineering, 2+ yrs plant experience required.' },
    { id:'SOL-002', title:'Energy Trading Analyst',                  dept:'Energy',           location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-09', deadline:'2026-06-24', summary:'Analyse electricity and gas markets, support physical and financial energy trading activities. Economics or engineering background.' },
    { id:'SOL-003', title:'Maintenance Planner — Mechanical',        dept:'Asset Management', location:'Sasolburg, South Africa', type:'Full-time', posted:'2026-04-22', deadline:'2026-06-08', summary:'Plan and schedule preventive and corrective maintenance activities for rotating and static equipment. Artisan trade test an advantage.' },
  ],
  MTN: [
    { id:'MTN-001', title:'5G Network Architect',                    dept:'Technology',       location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Design and govern MTN Group\'s pan-African 5G architecture roadmap. 8+ yrs telecoms network architecture experience.' },
    { id:'MTN-002', title:'Fintech Product Director — Africa',       dept:'Fintech',          location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-06', deadline:'2026-06-20', summary:'Lead mobile money product strategy across 16 African markets. P&L ownership experience in fintech or payments required.' },
    { id:'MTN-003', title:'Senior Software Engineer — Cloud Services', dept:'Technology',     location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-04-28', deadline:'2026-06-14', summary:'Build and scale cloud-native microservices powering MTN\'s digital ecosystem. Go/Java, Kubernetes, AWS/GCP experience required.' },
    { id:'MTN-004', title:'Regulatory Affairs Manager',              dept:'Legal & Regulatory', location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-19', deadline:'2026-07-05', summary:'Engage with national communications regulators across MTN\'s African markets on licensing, spectrum, and tariff matters.' },
  ],
  SBK: [
    { id:'SBK-001', title:'Investment Banking Analyst',              dept:'Investment Banking', location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-11', deadline:'2026-06-27', summary:'Support deal origination, financial modelling, and client presentations in Standard Bank\'s CIB division. CA(SA)/CFA preferred.' },
    { id:'SBK-002', title:'Quantitative Risk Analyst',               dept:'Risk',             location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-04', deadline:'2026-06-18', summary:'Develop and validate market risk models (VaR, stress testing) for the trading book. Strong Python/R and statistics background.' },
    { id:'SBK-003', title:'Pan-Africa Product Manager — Trade Finance', dept:'Transactional Banking', location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-04-27', deadline:'2026-06-12', summary:'Manage documentary credits, guarantees, and supply chain finance products across 20 African markets.' },
  ],
  FSR: [
    { id:'FSR-001', title:'Data Scientist — Credit Decisioning',     dept:'Analytics',        location:'Sandton, South Africa', type:'Full-time', posted:'2026-05-17', deadline:'2026-07-02', summary:'Build ML credit scorecards and decision engines for FNB\'s retail lending portfolio. Python, H2O.ai, and credit risk domain knowledge.' },
    { id:'FSR-002', title:'Financial Planner — WesBank Fleet',       dept:'WesBank',          location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-05-08', deadline:'2026-06-23', summary:'Advise corporate clients on vehicle fleet financing, insurance, and maintenance solutions. CFP or RFP qualification preferred.' },
    { id:'FSR-003', title:'Cybersecurity Architect',                 dept:'Technology',       location:'Sandton, South Africa', type:'Full-time', posted:'2026-04-30', deadline:'2026-06-16', summary:'Design and govern Firstrand\'s information security architecture across FNB, Rand Merchant Bank, and WesBank. CISSP required.' },
  ],
  SHP: [
    { id:'SHP-001', title:'Store Operations Manager',                dept:'Retail Operations', location:'Cape Town, South Africa', type:'Full-time', posted:'2026-05-15', deadline:'2026-06-30', summary:'Lead a high-volume Shoprite supermarket, managing P&L, team performance, and customer satisfaction. Retail management experience essential.' },
    { id:'SHP-002', title:'Supply Chain Analyst',                    dept:'Supply Chain',     location:'Brackenfell, South Africa', type:'Full-time', posted:'2026-05-10', deadline:'2026-06-25', summary:'Optimise inventory planning, replenishment, and distribution network efficiency across the Shoprite group.' },
    { id:'SHP-003', title:'Software Developer — Retail Systems',     dept:'Technology',       location:'Cape Town, South Africa', type:'Full-time', posted:'2026-05-03', deadline:'2026-06-17', summary:'Develop and maintain Shoprite\'s POS, loyalty, and e-commerce platforms. Java/Kotlin or React experience preferred.' },
    { id:'SHP-004', title:'Merchandise Planner — Groceries',         dept:'Merchandising',    location:'Brackenfell, South Africa', type:'Full-time', posted:'2026-04-25', deadline:'2026-06-10', summary:'Drive category range, pricing, and promotion planning for the ambient grocery category across 2,000+ stores.' },
  ],
  VOD: [
    { id:'VOD-001', title:'IoT Solutions Architect',                 dept:'Enterprise Business', location:'Midrand, South Africa', type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Design end-to-end IoT connectivity and platform solutions for Vodacom\'s enterprise clients in agriculture, logistics, and smart cities.' },
    { id:'VOD-002', title:'Network Operations Centre Engineer',      dept:'Network Operations', location:'Midrand, South Africa', type:'Full-time', posted:'2026-05-06', deadline:'2026-06-20', summary:'Monitor and troubleshoot Vodacom\'s 4G/5G network on a shift basis. Telecoms fault management experience required.' },
    { id:'VOD-003', title:'Legal Counsel — Regulatory',             dept:'Legal',            location:'Johannesburg, South Africa', type:'Full-time', posted:'2026-04-29', deadline:'2026-06-14', summary:'Advise on ICASA regulatory matters, spectrum licensing, and competition law compliance. LLB with telecoms regulatory exposure.' },
  ],
  NED: [
    { id:'NED-001', title:'Graduate Programme — Finance',           dept:'Graduate Talent',  location:'Sandton, South Africa', type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Nedbank\'s structured 24-month programme for finance, accounting, and economics graduates. CA(SA) articles pathway available.' },
    { id:'NED-002', title:'ESG Investment Analyst',                  dept:'Asset Management', location:'Sandton, South Africa', type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Integrate ESG factors into investment research and portfolio construction for Nedbank\'s institutional asset management division. CFA encouraged.' },
  ],

  // ── NGX — Nigeria ────────────────────────────────────────────────────────────
  DANGCEM: [
    { id:'DANGCEM-001', title:'Production Manager — Cement Plant',   dept:'Operations',       location:'Obajana, Kogi State', type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Oversee clinker and cement production at Dangote\'s 15Mtpa Obajana plant. BSc Chemical/Mechanical Engineering, 10+ yrs cement industry experience.' },
    { id:'DANGCEM-002', title:'Distribution & Logistics Coordinator', dept:'Supply Chain',    location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-07', deadline:'2026-06-22', summary:'Coordinate nationwide cement distribution via road, rail, and waterway logistics. SAP TM experience preferred.' },
    { id:'DANGCEM-003', title:'Quality Control Analyst',             dept:'Quality',          location:'Ibese, Ogun State',    type:'Full-time', posted:'2026-04-29', deadline:'2026-06-15', summary:'Perform physical and chemical testing of raw materials and finished products at Ibese plant. BSc Chemistry or Material Science.' },
    { id:'DANGCEM-004', title:'HSE Officer',                         dept:'Safety',           location:'Obajana, Kogi State',  type:'Full-time', posted:'2026-05-19', deadline:'2026-07-05', summary:'Implement and monitor HSE management systems across Dangote Cement production sites. NEBOSH NGC/IGC required.' },
  ],
  ZENITHBANK: [
    { id:'ZENITHBANK-001', title:'Graduate Trainee — Banking Operations', dept:'Operations',  location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-16', deadline:'2026-07-01', summary:'Zenith Bank\'s annual graduate recruitment. Candidates must not be older than 26 and must possess min 2:2 degree. Strong numerical aptitude required.' },
    { id:'ZENITHBANK-002', title:'Relationship Manager — Oil & Gas', dept:'Corporate Banking', location:'Lagos (Victoria Island)', type:'Full-time', posted:'2026-05-09', deadline:'2026-06-24', summary:'Manage energy sector clients, structure financing solutions, and grow the oil and gas loan book. 5+ yrs corporate banking experience.' },
    { id:'ZENITHBANK-003', title:'Cybersecurity Engineer',           dept:'IT Security',      location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-01', deadline:'2026-06-15', summary:'Defend Zenith Bank\'s digital infrastructure. Experience with SIEM, EDR, and cloud security platforms (Azure Sentinel, Splunk). CISSP a plus.' },
    { id:'ZENITHBANK-004', title:'Treasury Sales Officer',           dept:'Treasury',         location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-04-23', deadline:'2026-06-09', summary:'Market fixed income, FX, and structured products to institutional and corporate clients. ACI Dealing Certificate preferred.' },
  ],
  GTCO: [
    { id:'GTCO-001', title:'Management Associate Programme',         dept:'Graduate Talent',  location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'GTCO\'s flagship management associate scheme. Competitive 18-month rotational programme for exceptional graduates under 28.' },
    { id:'GTCO-002', title:'Digital Product Manager — GTWorld',      dept:'Digital Banking',  location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-07', deadline:'2026-06-22', summary:'Own the GTWorld mobile app product roadmap — features, releases, and user experience. Agile PM experience and fintech passion required.' },
    { id:'GTCO-003', title:'Private Banking Relationship Officer',   dept:'Private Banking',  location:'Lagos (Ikoyi)',         type:'Full-time', posted:'2026-04-29', deadline:'2026-06-14', summary:'Manage high-net-worth client portfolios, providing investment, lending, and lifestyle banking services. Discretion and strong client skills essential.' },
  ],
  MTNN: [
    { id:'MTNN-001', title:'Senior Network Engineer — 5G Rollout',   dept:'Network',          location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-15', deadline:'2026-06-30', summary:'Lead technical planning and deployment of MTN Nigeria\'s 5G NR network in Lagos and Abuja. Huawei gNodeB experience preferred.' },
    { id:'MTNN-002', title:'MoMo Business Development Manager',      dept:'Fintech / MoMo',   location:'Abuja, Nigeria',       type:'Full-time', posted:'2026-05-08', deadline:'2026-06-23', summary:'Grow MTN Nigeria\'s mobile money agent network and merchant ecosystem. 4+ yrs payment or agency banking experience.' },
    { id:'MTNN-003', title:'Backend Software Engineer (Go/Java)',     dept:'Technology',       location:'Lagos, Nigeria',       type:'Full-time',  posted:'2026-05-02', deadline:'2026-06-17', summary:'Build scalable APIs for MTN Nigeria\'s digital services platform. Go or Java microservices, Kubernetes, and 3+ yrs backend experience required.' },
    { id:'MTNN-004', title:'Corporate Communications Specialist',    dept:'Communications',   location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-04-24', deadline:'2026-06-09', summary:'Manage media relations, internal communications, and brand reputation for MTN Nigeria. Degree in Communications or Journalism.' },
  ],
  AIRTELAFRI: [
    { id:'AIRTELAFRI-001', title:'Chief Data Officer — West Africa',  dept:'Data & Analytics', location:'Lagos, Nigeria',      type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Lead data strategy, governance, and analytics for Airtel\'s West African markets (Nigeria, Ghana, Sierra Leone, others).' },
    { id:'AIRTELAFRI-002', title:'Network Quality Engineer',          dept:'Technology',       location:'Port Harcourt, Nigeria', type:'Full-time', posted:'2026-05-06', deadline:'2026-06-20', summary:'Monitor, analyse, and improve Airtel Nigeria\'s 4G network KPIs (CSFB, DL throughput, RRC SR). TEMS/NEMO drive test tools experience.' },
    { id:'AIRTELAFRI-003', title:'SME Sales Manager',                 dept:'Enterprise Sales', location:'Kano, Nigeria',        type:'Full-time', posted:'2026-04-28', deadline:'2026-06-14', summary:'Drive SME data and voice revenue growth in Northern Nigeria. Strong B2B telecoms sales record required.' },
  ],
  ACCESS: [
    { id:'ACCESS-001', title:'Graduate Trainee Programme 2026',      dept:'Graduate Talent',  location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-17', deadline:'2026-07-02', summary:'Access Bank\'s annual intake for exceptional graduates. Candidates should not exceed 26 years. Min 2:2 in any discipline. Aptitude test required.' },
    { id:'ACCESS-002', title:'Trade Finance Officer',                 dept:'Trade Finance',    location:'Lagos (Marina)',        type:'Full-time', posted:'2026-05-10', deadline:'2026-06-25', summary:'Process LCs, bills, guarantees, and collections for trade finance clients. CDCS certification an advantage.' },
    { id:'ACCESS-003', title:'Application Security Engineer',        dept:'IT Security',      location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-03', deadline:'2026-06-18', summary:'Conduct code reviews, DAST/SAST scanning, and security architecture reviews for Access Bank\'s digital banking applications.' },
  ],
  UBA: [
    { id:'UBA-001', title:'Pan-African HR Business Partner',          dept:'Human Resources',  location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-16', deadline:'2026-07-01', summary:'Support HR operations across multiple UBA African subsidiaries. Experience in multi-country HR in a banking environment essential.' },
    { id:'UBA-002', title:'Corporate Banking Manager — Infrastructure', dept:'Corporate Banking', location:'Abuja, Nigeria',    type:'Full-time', posted:'2026-05-09', deadline:'2026-06-24', summary:'Originate and execute infrastructure finance transactions for government and DFI clients. Project finance deal experience required.' },
    { id:'UBA-003', title:'Digital Experience Designer (UI/UX)',      dept:'Technology',       location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-01', deadline:'2026-06-16', summary:'Design intuitive interfaces for UBA\'s mobile banking apps across Africa. Figma proficiency and mobile-first design experience required.' },
  ],
  FBNH: [
    { id:'FBNH-001', title:'Relationship Manager — Mid-Market',       dept:'Commercial Banking', location:'Lagos, Nigeria',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Manage a portfolio of mid-market commercial clients, growing deposits, loans, and trade finance volumes. 4+ yrs commercial banking experience.' },
    { id:'FBNH-002', title:'IT Audit Specialist',                     dept:'Internal Audit',   location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-07', deadline:'2026-06-22', summary:'Plan and execute IT and cybersecurity audits across First Bank\'s technology landscape. CISA or CISM certification required.' },
    { id:'FBNH-003', title:'Agent Banking Expansion Officer',         dept:'Agency Banking',   location:'Onitsha, Nigeria',     type:'Full-time', posted:'2026-04-29', deadline:'2026-06-14', summary:'Recruit, train, and manage First Bank\'s agency banking network in the South-East region. Field sales background preferred.' },
  ],
  NESTLE: [
    { id:'NESTLE-001', title:'Supply Chain Graduate Trainee',         dept:'Supply Chain',     location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-15', deadline:'2026-06-30', summary:'Nestlé Nigeria\'s 12-month graduate trainee scheme focused on procurement, logistics, and planning. Supply chain or engineering degree preferred.' },
    { id:'NESTLE-002', title:'Key Account Manager',                   dept:'Sales',            location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-08', deadline:'2026-06-23', summary:'Manage Nestlé\'s relationships with major modern trade and distributor accounts (Shoprite, SPAR, Game). 3+ yrs FMCG key account management.' },
    { id:'NESTLE-003', title:'Factory Quality Manager',               dept:'Quality',          location:'Agbara, Ogun State',   type:'Full-time', posted:'2026-04-30', deadline:'2026-06-16', summary:'Lead quality systems, food safety certification (ISO 22000/FSSC 22000), and team capability at Nestlé\'s Agbara factory.' },
  ],
  BUACEMENT: [
    { id:'BUACEMENT-001', title:'Plant Operations Engineer',          dept:'Operations',       location:'Edo State, Nigeria',   type:'Full-time', posted:'2026-05-12', deadline:'2026-06-28', summary:'Monitor and optimise kiln, mill, and packing operations at BUA Cement\'s Okpella plant. BSc Mechanical/Chemical Engineering, cement experience preferred.' },
    { id:'BUACEMENT-002', title:'Regional Sales Manager — North',     dept:'Commercial',       location:'Kano, Nigeria',        type:'Full-time', posted:'2026-05-05', deadline:'2026-06-19', summary:'Drive cement sales revenue and market share growth across Northern Nigeria dealer and distributor network.' },
    { id:'BUACEMENT-003', title:'Power Plant Technician',             dept:'Utilities',        location:'Kalambaina, Sokoto',   type:'Full-time', posted:'2026-04-27', deadline:'2026-06-12', summary:'Operate and maintain captive gas power plant supplying BUA Cement\'s Kalambaina facility. Electrical/mechanical artisan qualification required.' },
  ],

  // ── NSE — Kenya ──────────────────────────────────────────────────────────────
  SAFCOM: [
    { id:'SAFCOM-001', title:'Infrastructure SRE Engineer',           dept:'Technology',       location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-10', deadline:'2026-06-25', summary:'Ensure reliability, availability, and performance of Safaricom\'s core infrastructure. Kubernetes, Terraform, and Linux administration expertise required.' },
    { id:'SAFCOM-002', title:'Talent Acquisition Manager — Technology', dept:'HR',             location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-03', deadline:'2026-06-18', summary:'Lead end-to-end technical hiring for Safaricom\'s engineering and product teams. In-house tech recruitment experience essential.' },
    { id:'SAFCOM-003', title:'Cloud & Network Cybersecurity Analyst',  dept:'Security',        location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-04-25', deadline:'2026-06-11', summary:'Monitor threats, conduct vulnerability assessments, and strengthen security posture across Safaricom\'s cloud and telco infrastructure.' },
    { id:'SAFCOM-004', title:'M-PESA Business Partnerships Lead',     dept:'Fintech',          location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-16', deadline:'2026-07-01', summary:'Drive strategic fintech partnerships that extend M-PESA\'s ecosystem. Experience in payments, APIs, or financial services partnerships required.' },
    { id:'SAFCOM-005', title:'Data Scientist — Network Analytics',    dept:'Analytics',        location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-20', deadline:'2026-07-05', summary:'Develop predictive models to optimise network capacity and quality of experience. Python, Spark, and telecoms domain knowledge needed.' },
  ],
  EQUITY: [
    { id:'EQUITY-001', title:'Digital Credit Product Manager',        dept:'Digital Banking',  location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Own Equity\'s mobile credit products (Eazzy Loan, EquiDuuka) — roadmap, pricing, and risk parameters. 4+ yrs digital credit experience.' },
    { id:'EQUITY-002', title:'Branch Manager',                        dept:'Retail Banking',   location:'Eldoret, Kenya',       type:'Full-time', posted:'2026-05-07', deadline:'2026-06-22', summary:'Lead an Equity Bank branch — business development, operations, team management, and compliance. 5+ yrs banking, 2+ yrs management experience.' },
    { id:'EQUITY-003', title:'Pan-Africa IT Security Engineer',       dept:'Technology',       location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-04-29', deadline:'2026-06-15', summary:'Protect Equity\'s digital infrastructure across its 7-country African footprint. CISSP or CISM, cloud security experience required.' },
  ],
  KCB: [
    { id:'KCB-001', title:'Graduate Talent Programme 2026',           dept:'Graduate Talent',  location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-15', deadline:'2026-06-30', summary:'KCB Group\'s competitive 12-month graduate programme. Open to recent graduates (First Class or Upper Second) in any discipline.' },
    { id:'KCB-002', title:'Trade Finance Manager',                    dept:'Corporate Banking', location:'Nairobi, Kenya',      type:'Full-time', posted:'2026-05-09', deadline:'2026-06-24', summary:'Structure and manage trade finance facilities for KCB\'s East African corporate clients. CDCS holder preferred. 5+ yrs trade finance experience.' },
    { id:'KCB-003', title:'Bancassurance Officer',                    dept:'Bancassurance',    location:'Kampala, Uganda',      type:'Full-time', posted:'2026-05-02', deadline:'2026-06-17', summary:'Sell insurance products through KCB Uganda\'s branch network. Certificate of Proficiency (CoP) in Insurance and 2+ yrs insurance sales experience.' },
  ],
  EABL: [
    { id:'EABL-001', title:'Sales Representative — On-Trade',         dept:'Sales',            location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Drive EABL brand visibility and volume in bars, hotels, and restaurants across Nairobi. Route-to-market experience in FMCG preferred.' },
    { id:'EABL-002', title:'Brewery Engineer — Packaging',            dept:'Supply Chain',     location:'Ruaraka, Nairobi',     type:'Full-time', posted:'2026-05-06', deadline:'2026-06-20', summary:'Operate and maintain EABL\'s packaging lines (bottling, kegging, canning). Mechanical/Electrical Engineering degree required.' },
    { id:'EABL-003', title:'Finance Business Partner',                dept:'Finance',          location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-04-28', deadline:'2026-06-14', summary:'Provide commercial finance support to EABL\'s commercial and supply chain functions. CPA(K) or ACCA, FMCG finance background preferred.' },
  ],
  COOP: [
    { id:'COOP-001', title:'Agricultural Finance Officer',            dept:'Agribusiness Banking', location:'Nakuru, Kenya',    type:'Full-time', posted:'2026-05-17', deadline:'2026-07-02', summary:'Provide financial advisory and credit solutions to farmers, cooperatives, and agri-businesses in the Rift Valley region.' },
    { id:'COOP-002', title:'Mobile Banking Developer (Android)',      dept:'Technology',       location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-10', deadline:'2026-06-25', summary:'Build and maintain Co-op Bank\'s MCo-op Cash mobile app. Kotlin, RESTful APIs, and 3+ yrs Android development experience required.' },
  ],
  ABSA: [
    { id:'ABSA-001', title:'Relationship Manager — SME Banking',      dept:'Business Banking', location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-16', deadline:'2026-07-01', summary:'Grow ABSA Kenya\'s SME portfolio — acquisition, retention, and cross-selling of business banking products. 3+ yrs SME relationship management.' },
    { id:'ABSA-002', title:'Risk & Compliance Officer',               dept:'Risk',             location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-08', deadline:'2026-06-23', summary:'Monitor operational risk, implement the compliance management framework, and liaise with CBK. 3+ yrs banking compliance experience.' },
    { id:'ABSA-003', title:'Graduate Trainee 2026 — Kenya',          dept:'Graduate Talent',  location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-01', deadline:'2026-06-15', summary:'ABSA\'s 18-month African graduate programme. Rotational placements in retail, business, and corporate banking.' },
  ],
  NCBA: [
    { id:'NCBA-001', title:'Digital Lending Product Manager',         dept:'Digital Banking',  location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Manage NCBA\'s M-Shwari and Loop digital lending products. Partnership with Safaricom, data-driven credit, and product KPI ownership experience needed.' },
    { id:'NCBA-002', title:'Private Wealth Manager',                  dept:'Wealth Management', location:'Nairobi, Kenya',     type:'Full-time', posted:'2026-05-07', deadline:'2026-06-22', summary:'Advise HNWI clients on investment, estate planning, and structured solutions. Minimum KES 50M AUM relationship track record preferred.' },
    { id:'NCBA-003', title:'IT Infrastructure Engineer',              dept:'Technology',       location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-04-29', deadline:'2026-06-14', summary:'Maintain and evolve NCBA\'s hybrid cloud infrastructure (Azure, VMware, Cisco). CCNP or Azure Administrator certification preferred.' },
  ],
  SCBK: [
    { id:'SCBK-001', title:'International Graduate Programme — Kenya',dept:'Graduate Talent',  location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Standard Chartered\'s global programme rotating across wholesale banking, risk, and finance. Top-tier university graduates welcomed.' },
    { id:'SCBK-002', title:'Cash Management Sales Manager',           dept:'Transaction Banking', location:'Nairobi, Kenya',    type:'Full-time', posted:'2026-05-05', deadline:'2026-06-19', summary:'Sell cash management, trade, and liquidity solutions to large corporates and institutions in East Africa. 5+ yrs transaction banking experience.' },
  ],
  BRITAM: [
    { id:'BRITAM-001', title:'Unit Trust Fund Manager',               dept:'Asset Management', location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Manage Britam Asset Management\'s equity and fixed income unit trust funds. CFA charterholder, 5+ yrs buy-side investment management.' },
    { id:'BRITAM-002', title:'Actuarial Analyst',                     dept:'Actuarial',        location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-06', deadline:'2026-06-20', summary:'Support reserving, pricing, and regulatory capital modelling for Britam\'s life and general insurance portfolios. Part-qualified actuary (IFoA/SOA).' },
    { id:'BRITAM-003', title:'Insurance Sales Agent — Retail Life',   dept:'Sales',            location:'Mombasa, Kenya',       type:'Full-time', posted:'2026-04-28', deadline:'2026-06-14', summary:'Sell individual life, health, and savings products to retail clients in Coast Region. Cert of Proficiency in Insurance required.' },
  ],
  KENGEN: [
    { id:'KENGEN-001', title:'Geothermal Plant Engineer',             dept:'Generation',       location:'Olkaria, Naivasha',    type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Operate and maintain KenGen\'s geothermal steam turbines at Olkaria. BSc Mechanical or Electrical Engineering, 3+ yrs power plant experience.' },
    { id:'KENGEN-002', title:'Environmental & Social Officer',        dept:'Sustainability',   location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-04', deadline:'2026-06-18', summary:'Prepare ESIAs, manage community relations programmes, and support KenGen\'s climate strategy. BSc Environmental Science, 3+ yrs relevant experience.' },
    { id:'KENGEN-003', title:'Project Engineer — Wind Power',        dept:'Renewable Energy',  location:'Ngong Hills, Kenya',   type:'Full-time', posted:'2026-04-27', deadline:'2026-06-12', summary:'Provide technical oversight for KenGen\'s wind power projects. BSc Electrical Engineering, wind turbine O&M experience preferred.' },
  ],

  // ── CSE — Morocco ────────────────────────────────────────────────────────────
  ATW: [
    { id:'ATW-001', title:'Wealth Management Advisor',              dept:'Private Banking',  location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-12', deadline:'2026-06-28', summary:'Serve HNWI clients across Attijariwafa Bank\'s private banking franchise. Experience in portfolio management, estate planning, and cross-border advisory required.' },
    { id:'ATW-002', title:'Digital Transformation Project Manager', dept:'Technology',       location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-06', deadline:'2026-06-22', summary:'Lead digitisation of retail banking processes. Agile PM experience, familiarity with Temenos core banking and API-first architecture preferred.' },
    { id:'ATW-003', title:'Trade Finance Specialist',               dept:'Corporate Banking',location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-04-28', deadline:'2026-06-14', summary:'Structure and process documentary credits, guarantees, and supply-chain finance instruments. ICC CDCS certification advantageous.' },
  ],
  IAM: [
    { id:'IAM-001', title:'5G Radio Access Network Engineer',       dept:'Network',          location:'Rabat, Morocco',       type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Deploy and optimise Maroc Telecom\'s 5G NR rollout. Experience with Nokia/Huawei RAN, NSA/SA architecture, and 5G planning tools required.' },
    { id:'IAM-002', title:'Product Manager — Enterprise Cloud',     dept:'B2B Services',     location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-07', deadline:'2026-06-21', summary:'Define and drive cloud and hosted services products for large enterprise customers. Cloud certification (AWS/Azure) and B2B product management experience.' },
    { id:'IAM-003', title:'Cybersecurity Analyst',                  dept:'Security',         location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-04-25', deadline:'2026-06-12', summary:'Monitor SOC alerts, perform threat hunting, and manage vulnerability assessments. CISSP or CEH certification preferred.' },
  ],
  OCP: [
    { id:'OCP-001', title:'Process Engineer — Phosphate Flotation', dept:'Operations',       location:'Khouribga, Morocco',   type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Optimise phosphate beneficiation circuits and flotation reagent programs. BSc Chemical or Mining Engineering with 3+ yrs mineral processing experience.' },
    { id:'OCP-002', title:'Agronomist — Fertilizer Solutions',      dept:'Agriculture',      location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Provide agronomic support and soil analysis to develop customised fertilizer prescriptions for African and Latin American markets.' },
    { id:'OCP-003', title:'Digital Data Scientist — Mining',        dept:'Analytics',        location:'Rabat, Morocco',       type:'Full-time', posted:'2026-04-30', deadline:'2026-06-16', summary:'Apply ML to optimise extraction yields and predict equipment failures across OCP mine sites. Python, PySpark, and time-series modelling skills required.' },
  ],
  BCP: [
    { id:'BCP-001', title:'Credit Analyst — SME Banking',          dept:'Risk',             location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-11', deadline:'2026-06-27', summary:'Evaluate credit proposals for SME clients, prepare risk opinions, and monitor loan portfolios. Financial analysis and CFA foundation level preferred.' },
    { id:'BCP-002', title:'Compliance Officer — AML/CFT',          dept:'Compliance',       location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-03', deadline:'2026-06-19', summary:'Ensure adherence to BAM AML/CFT regulations, screen transactions, and maintain KYC/CDD frameworks. CAMS certification is advantageous.' },
  ],
  BMCE: [
    { id:'BMCE-001', title:'Corporate Relationship Manager — Africa',dept:'Corporate Banking',location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Manage relationships with large corporates across Bank of Africa\'s 35-country African network. Bilingual (French/English), 5+ yrs corporate banking.' },
    { id:'BMCE-002', title:'Treasury FX Dealer',                    dept:'Financial Markets',location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-04', deadline:'2026-06-18', summary:'Execute spot, forward, and options transactions in MAD, EUR, and USD. ACI Diploma preferred; experience with Bloomberg FXGO essential.' },
  ],
  CIH: [
    { id:'CIH-001', title:'Real Estate Loan Officer',               dept:'Retail Banking',   location:'Marrakech, Morocco',   type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Originate and process residential mortgage applications for CIH Bank\'s retail clients. Real estate finance experience and client acquisition skills required.' },
    { id:'CIH-002', title:'IT Project Manager — Core Banking',      dept:'Technology',       location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Lead migration and enhancement projects on CIH\'s Flexcube core banking platform. PMP certification and core banking project experience required.' },
  ],
  HPS: [
    { id:'HPS-001', title:'Software Engineer — Payment Switching',  dept:'Engineering',      location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-17', deadline:'2026-07-03', summary:'Develop and maintain HPS\'s PowerCARD switch and issuing platform. Java, ISO 8583, and experience with Visa/Mastercard certifications a strong plus.' },
    { id:'HPS-002', title:'Solutions Architect — Fintech',          dept:'Pre-Sales',        location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-10', deadline:'2026-06-26', summary:'Design end-to-end payment processing architectures for HPS\'s global banking clients. Cloud (AWS/Azure), microservices, and PCI-DSS knowledge required.' },
    { id:'HPS-003', title:'QA Engineer — Payment Systems',          dept:'Quality Assurance',location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-02', deadline:'2026-06-17', summary:'Build automated test frameworks for payment switch regression suites. Selenium, JMeter, and EMV knowledge preferred.' },
  ],
  COSUMAR: [
    { id:'COSUMAR-001', title:'Process Engineer — Sugar Refinery',  dept:'Operations',       location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Optimise sugar crystallisation, evaporation, and refining processes at Cosumar\'s Casablanca plant. BSc Chemical Engineering with sugar industry experience.' },
    { id:'COSUMAR-002', title:'Agronomy Field Supervisor',          dept:'Agriculture',      location:'Tadla, Morocco',       type:'Full-time', posted:'2026-05-06', deadline:'2026-06-22', summary:'Support sugarbeet and sugarcane farmers in the Tadla-Azilal basin. Coordinate planting programmes and crop quality improvements.' },
  ],
  CIMAR: [
    { id:'CIMAR-001', title:'Cement Plant Engineer',                dept:'Operations',       location:'Ait Baha, Morocco',    type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Oversee kiln, mill, and quality control operations at Ciments du Maroc\'s Ait Baha plant. BSc Mechanical or Process Engineering with cement industry background.' },
    { id:'CIMAR-002', title:'Sustainability & Environment Officer',  dept:'HSE',              location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-05', deadline:'2026-06-21', summary:'Manage carbon reporting (EU ETS aligned), dust emissions monitoring, and ISO 14001 compliance across Ciments du Maroc facilities.' },
  ],
  WAFA: [
    { id:'WAFA-001', title:'Actuarial Analyst — Life & Health',     dept:'Actuarial',        location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-18', deadline:'2026-07-04', summary:'Perform reserving, pricing, and experience analysis for Wafa Assurance\'s life and takaful portfolios. Part-qualified actuary (IFoA/DAA) preferred.' },
    { id:'WAFA-002', title:'Insurance Sales Manager — Bancassurance',dept:'Sales',            location:'Casablanca, Morocco',  type:'Full-time', posted:'2026-05-10', deadline:'2026-06-26', summary:'Drive life and non-life insurance sales through Attijariwafa Bank\'s branch network. Bancassurance management experience and insurance licence required.' },
  ],

  // ── EGX — Egypt ─────────────────────────────────────────────────────────────
  COMI: [
    { id:'COMI-001', title:'Corporate Banking Relationship Manager', dept:'Corporate Banking',location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Manage a portfolio of large corporate clients at CIB Egypt, cross-selling trade finance, FX hedging, and cash management solutions. 5+ yrs corporate banking.' },
    { id:'COMI-002', title:'Data Analytics Engineer',               dept:'Technology',       location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Build scalable data pipelines and BI dashboards to support CIB\'s digital banking strategy. Python, Apache Spark, and Snowflake experience preferred.' },
    { id:'COMI-003', title:'Graduate Development Programme',        dept:'Graduate Talent',  location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-01', deadline:'2026-06-15', summary:'CIB\'s flagship 18-month rotational programme across retail, corporate, treasury, and risk. Top Egyptian university graduates with strong GPA welcome.' },
  ],
  HRHO: [
    { id:'HRHO-001', title:'Real Estate Sales Executive',           dept:'Sales',            location:'New Cairo, Egypt',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Sell Heliopolis Housing residential units in New Cairo and Ain Sokhna. 3+ yrs real estate sales experience and strong client network required.' },
    { id:'HRHO-002', title:'Construction Project Manager',          dept:'Engineering',      location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-07', deadline:'2026-06-22', summary:'Oversee on-site construction teams, coordinate contractors, and maintain schedule and budget adherence for residential project delivery. BSc Civil Engineering.' },
  ],
  TMGH: [
    { id:'TMGH-001', title:'Sales Director — Compound Developments',dept:'Sales',            location:'Sixth of October, Egypt',type:'Full-time',posted:'2026-05-15', deadline:'2026-07-01', summary:'Lead SODIC\'s sales team for its flagship compound developments in West Cairo. Real estate sector leadership and 8+ yrs luxury residential sales experience.' },
    { id:'TMGH-002', title:'Urban Planner — Master Community',      dept:'Design',           location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Develop land-use plans and community master plans for SODIC\'s mixed-use developments. Architecture or urban planning degree with AutoCAD/Revit proficiency.' },
  ],
  ESRS: [
    { id:'ESRS-001', title:'Steelmaking Process Engineer',          dept:'Operations',       location:'10th of Ramadan City, Egypt',type:'Full-time',posted:'2026-05-11',deadline:'2026-06-26',summary:'Optimise Ezz Steel\'s electric arc furnace and continuous casting operations. BSc Metallurgical or Materials Engineering with 3+ yrs steelmaking experience.' },
    { id:'ESRS-002', title:'Procurement Specialist — Raw Materials', dept:'Procurement',     location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Source scrap steel, ferroalloys, and electrodes for Ezz Steel\'s rolling and melting shops. CIPS qualification and commodity procurement background preferred.' },
  ],
  SWDY: [
    { id:'SWDY-001', title:'Petrochemicals Process Engineer',       dept:'Operations',       location:'Alexandria, Egypt',    type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Support operations at SIDPEC\'s polyethylene production complex. BSc Chemical Engineering with polymer processing plant experience and PI/DCS knowledge.' },
    { id:'SWDY-002', title:'Health, Safety & Environmental Officer',dept:'HSE',              location:'Alexandria, Egypt',    type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Implement OHSAS 18001/ISO 14001 programmes, conduct risk assessments, and manage emergency response plans at SIDPEC\'s plant.' },
  ],
  MNHD: [
    { id:'MNHD-001', title:'Property Sales Consultant',            dept:'Sales',            location:'Nasr City, Cairo, Egypt',type:'Full-time',posted:'2026-05-12',deadline:'2026-06-27',summary:'Promote and sell Medinet Nasr Housing residential and commercial units to retail clients. Real estate licence and 2+ yrs property sales experience.' },
    { id:'MNHD-002', title:'Technical Operations Supervisor',       dept:'Facilities Mgmt', location:'New Cairo, Egypt',     type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Oversee maintenance and utilities operations across MNHD\'s residential compounds. BSc Mechanical or Electrical Engineering, 5+ yrs facilities management.' },
  ],
  FWRY: [
    { id:'FWRY-001', title:'Product Manager — Digital Payments',    dept:'Product',          location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-17', deadline:'2026-07-03', summary:'Own the roadmap for Fawry\'s bill payment and POS merchant products. Payments industry experience, strong data analysis skills, and Agile methodology.' },
    { id:'FWRY-002', title:'Partnership Development Manager',        dept:'Business Dev',     location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-10', deadline:'2026-06-26', summary:'Identify and onboard new biller and enterprise clients for Fawry\'s payment network. Fintech B2B sales experience and strong corporate network in Egypt.' },
    { id:'FWRY-003', title:'Data Engineer — Transaction Analytics',  dept:'Analytics',        location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-03', deadline:'2026-06-18', summary:'Process and analyse Fawry\'s millions of daily payment transactions to detect fraud and improve acceptance rates. Python, Kafka, and Spark experience needed.' },
  ],
  PHDC: [
    { id:'PHDC-001', title:'Brand & Marketing Manager',             dept:'Marketing',        location:'New Cairo, Egypt',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Lead Palm Hills\' brand strategy and marketing campaigns for new compound launches. Real estate marketing experience and digital media expertise required.' },
    { id:'PHDC-002', title:'Customer Experience Manager',           dept:'Customer Service', location:'6th of October, Egypt',type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Design and implement customer journey improvements across pre-sale, sale, and post-handover touchpoints for Palm Hills\' residential community residents.' },
  ],
  JUFO: [
    { id:'JUFO-001', title:'Export Sales Manager — GCC & Africa',   dept:'Sales',            location:'Cairo, Egypt',         type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Grow Juhayna\'s dairy and juice exports in Gulf, North Africa, and Sub-Saharan Africa markets. FMCG export sales management experience and Arabic/English fluency.' },
    { id:'JUFO-002', title:'Quality Control Analyst',               dept:'Quality Assurance',location:'6th of October, Egypt',type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Conduct microbiological and physicochemical testing on Juhayna dairy and juice products. BSc Food Science or Chemistry, experience with HACCP and ISO 22000.' },
  ],
  OCDI: [
    { id:'OCDI-001', title:'Textile Design Engineer',               dept:'Design',           location:'10th of Ramadan, Egypt',type:'Full-time',posted:'2026-05-11',deadline:'2026-06-26',summary:'Develop carpet and rug designs for Oriental Weavers\' export markets. Experience with CAD weaving design software and international colour-trend forecasting.' },
    { id:'OCDI-002', title:'Production Planning Supervisor',        dept:'Operations',       location:'10th of Ramadan, Egypt',type:'Full-time',posted:'2026-05-04',deadline:'2026-06-19',summary:'Plan and schedule loom operations across Oriental Weavers\' production floors to meet export delivery targets. ERP (SAP) and textile manufacturing background.' },
  ],

  // ── BRVM — West Africa ───────────────────────────────────────────────────────
  SNTS: [
    { id:'SNTS-001', title:'Network Systems Engineer — 4G/5G',      dept:'Technology',       location:'Dakar, Senegal',       type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Plan and deploy Sonatel\'s 4G LTE-A and 5G NR sites across Senegal. Experience with Nokia or Ericsson RAN, CPRI/eCPRI, and LTE/NR planning tools required.' },
    { id:'SNTS-002', title:'Mobile Money Partnerships Manager',      dept:'Financial Services',location:'Dakar, Senegal',       type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Develop and manage Orange Money partnerships with banks, merchants, and fintechs in Senegal. 5+ yrs mobile money or fintech partnerships experience.' },
    { id:'SNTS-003', title:'Enterprise Account Manager',            dept:'B2B',              location:'Dakar, Senegal',       type:'Full-time', posted:'2026-04-28', deadline:'2026-06-14', summary:'Manage and grow large enterprise accounts in Senegal and the sub-region. Sell ICT, connectivity, cloud, and IoT solutions. Fluent French required.' },
  ],
  SGBCI: [
    { id:'SGBCI-001', title:'Corporate Credit Risk Analyst',        dept:'Risk',             location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-14',deadline:'2026-06-30',summary:'Analyse large corporate credit files, write risk opinions, and monitor loan portfolio quality for SocGen CI. French language skills and credit analysis training required.' },
    { id:'SGBCI-002', title:'Transaction Banking Product Officer',   dept:'Transaction Svc',  location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-07',deadline:'2026-06-22',summary:'Manage and grow SocGen CI\'s cash management and trade finance product suite for corporate clients in Francophone West Africa.' },
  ],
  ORANGECI: [
    { id:'ORANGECI-001', title:'Orange Money Product Manager',       dept:'Financial Services',location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-15',deadline:'2026-07-01',summary:'Lead Orange Money CI product strategy and merchant ecosystem. 5+ yrs mobile money product management, strong understanding of WAEMU regulatory framework.' },
    { id:'ORANGECI-002', title:'Network Deployment Engineer',        dept:'Technology',       location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-08',deadline:'2026-06-24',summary:'Oversee site acquisition, civil works, and equipment installation for Orange CI\'s network expansion across Cote d\'Ivoire. French required.' },
  ],
  SAPH: [
    { id:'SAPH-001', title:'Agronomy Supervisor — Rubber Estates',  dept:'Agriculture',      location:'Adzope, Cote d\'Ivoire', type:'Full-time',posted:'2026-05-11',deadline:'2026-06-26',summary:'Supervise tapping operations, fertiliser application, and clone replanting programmes on SAPH rubber plantations. BSc Tropical Agronomy, French required.' },
    { id:'SAPH-002', title:'Latex Processing Engineer',             dept:'Operations',       location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-04',deadline:'2026-06-19',summary:'Operate and optimise SAPH\'s latex concentration and dry rubber processing facilities. BSc Chemical or Processing Engineering with rubber industry experience.' },
  ],
  SIFCA: [
    { id:'SIFCA-001', title:'Sustainability & ESG Manager',          dept:'CSR',              location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-16',deadline:'2026-07-02',summary:'Lead SIFCA Group\'s sustainability programme across palm oil, rubber, and sugar operations. RSP/RSPO certification management, GRI reporting, and supply-chain traceability.' },
    { id:'SIFCA-002', title:'Finance & Treasury Analyst',            dept:'Finance',          location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-09',deadline:'2026-06-25',summary:'Support cash management, FX hedging, and commodity price risk management across SIFCA Group subsidiaries. DSCG or CA with agribusiness experience preferred.' },
  ],
  ECOBANK: [
    { id:'ECOBANK-001', title:'Pan-African Graduate Programme',      dept:'Graduate Talent',  location:'Lomé, Togo (pan-Africa)',type:'Full-time',posted:'2026-05-12',deadline:'2026-06-27',summary:'Ecobank\'s flagship pan-African graduate programme with rotations across 35 countries. Strong academics, ambition to build a career across Africa, bilingual preferred.' },
    { id:'ECOBANK-002', title:'Digital Banking Channel Manager',      dept:'Digital',          location:'Lagos, Nigeria',       type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Manage and grow Ecobank\'s mobile banking and Ecobank Pay digital platform across multiple African markets. Fintech product management, API/open banking knowledge.' },
    { id:'ECOBANK-003', title:'Trade Finance Specialist',             dept:'Corporate Banking',location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-04-27',deadline:'2026-06-12',summary:'Structure and execute documentary credit, guarantees, and supply-chain finance for corporate clients across West and Central Africa. ICC CDCS preferred.' },
  ],
  CORIS: [
    { id:'CORIS-001', title:'Retail Banking Advisor',                dept:'Retail Banking',   location:'Ouagadougou, Burkina Faso',type:'Full-time',posted:'2026-05-13',deadline:'2026-06-28',summary:'Provide financial advisory and product cross-selling services to individual and SME clients at Coris Bank branches. French required, banking experience an asset.' },
    { id:'CORIS-002', title:'IT Systems Administrator',              dept:'Technology',       location:'Ouagadougou, Burkina Faso',type:'Full-time',posted:'2026-05-06',deadline:'2026-06-21',summary:'Maintain Coris Bank\'s IT infrastructure, servers, and network security. MCSA or Linux SysAdmin certification, banking IT environment experience preferred.' },
  ],
  NSIABN: [
    { id:'NSIABN-001', title:'Credit Officer — SME & Corporates',   dept:'Credit',           location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-14',deadline:'2026-06-30',summary:'Evaluate SME and corporate lending requests, prepare credit memoranda, and monitor portfolio quality at NSIA Banque CI. French required, banking degree preferred.' },
    { id:'NSIABN-002', title:'Insurance Sales Advisor',             dept:'Bancassurance',    location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-07',deadline:'2026-06-22',summary:'Sell life and non-life NSIA insurance products through the bank branch network and direct channels. Insurance licence and client-facing sales experience required.' },
  ],
  TOTALCI: [
    { id:'TOTALCI-001', title:'Fuel Retail Station Manager',         dept:'Retail',           location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-15',deadline:'2026-07-01',summary:'Oversee day-to-day operations of TotalEnergies CI service stations including staff management, safety compliance, and revenue targets. French required.' },
    { id:'TOTALCI-002', title:'HSSE Officer',                        dept:'Safety',           location:'San Pedro, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-08',deadline:'2026-06-24',summary:'Implement TotalEnergies\' HSSE standards across CI depot and retail network. NEBOSH certificate or equivalent, French language essential.' },
  ],
  SOLIBRA: [
    { id:'SOLIBRA-001', title:'Brand Manager — Premium Beers',       dept:'Marketing',        location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-11',deadline:'2026-06-26',summary:'Lead marketing campaigns and activation programmes for SOLIBRA\'s Heineken and Primus brands in Cote d\'Ivoire. FMCG brand management experience, French required.' },
    { id:'SOLIBRA-002', title:'Brewery Maintenance Technician',       dept:'Operations',       location:'Abidjan, Cote d\'Ivoire',type:'Full-time',posted:'2026-05-04',deadline:'2026-06-19',summary:'Perform preventive and corrective maintenance on SOLIBRA brewing, filling, and packaging equipment. Electromechanical trade qualification, French required.' },
  ],

  // ── BSE — Botswana ───────────────────────────────────────────────────────────
  FNBB: [
    { id:'FNBB-001', title:'Business Banking Adviser',               dept:'Business Banking', location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Grow and manage a portfolio of SME and business banking clients for FNB Botswana. Experience in business lending, transactional banking, and relationship management.' },
    { id:'FNBB-002', title:'Software Developer — Digital Banking',   dept:'Technology',       location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Develop and maintain FNB Botswana\'s mobile and internet banking platforms. Java/Kotlin, Spring Boot, and REST API development experience required.' },
    { id:'FNBB-003', title:'Credit Risk Analyst',                    dept:'Risk',             location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-04-28', deadline:'2026-06-13', summary:'Assess retail and business credit applications, build scorecards, and monitor loan portfolio performance. ACIArb or Risk qualification advantageous.' },
  ],
  CHOBE: [
    { id:'CHOBE-001', title:'Head of Sustainability & Conservation',  dept:'Conservation',     location:'Kasane, Botswana',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Lead Chobe Holdings\' wildlife management, anti-poaching, and community conservation programmes across Botswana and Zimbabwe. BSc Wildlife Management + field experience.' },
    { id:'CHOBE-002', title:'Safari Lodge General Manager',           dept:'Hospitality',      location:'Chobe, Botswana',      type:'Full-time', posted:'2026-05-06', deadline:'2026-06-22', summary:'Manage all operations at a luxury Chobe Safari Lodge. 5+ yrs lodge management experience, strong guest experience track record, and hospitality degree.' },
  ],
  SEFALANA: [
    { id:'SEFALANA-001', title:'Retail Area Manager — Northern Region',dept:'Retail',          location:'Francistown, Botswana', type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Oversee Sefalana supermarket and wholesale operations in Northern Botswana. Retail management experience, strong P&L accountability, and people leadership skills.' },
    { id:'SEFALANA-002', title:'Supply Chain Planner',                dept:'Logistics',        location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-06', deadline:'2026-06-22', summary:'Manage demand forecasting, stock replenishment, and supplier relations for Sefalana\'s FMCG distribution business. ERP (SAP) and supply chain qualification preferred.' },
  ],
  STANBW: [
    { id:'STANBW-001', title:'Transactional Banking Sales Officer',   dept:'Corporate Banking',location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Sell cash management, trade, and payment solutions to Standard Chartered Botswana\'s corporate and institutional clients. Transaction banking experience required.' },
    { id:'STANBW-002', title:'Client Services Officer',              dept:'Retail Banking',   location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Serve personal and premium banking clients, process transactions, and resolve queries at Standard Chartered Botswana branches. Banking or finance diploma preferred.' },
  ],
  LETSHEGO: [
    { id:'LETSHEGO-001', title:'Deductions-Based Lending Officer',   dept:'Credit',           location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Originate and process payroll-deduction loans for civil servants and public sector employees. Microfinance or consumer lending experience required.' },
    { id:'LETSHEGO-002', title:'Technology Innovation Analyst',      dept:'Digital',          location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Support Letshego\'s digital lending and agency banking transformation across multiple African markets. Mobile money, API integration, and fintech background.' },
  ],
  BTCL: [
    { id:'BTCL-001', title:'Fibre Network Rollout Engineer',         dept:'Network',          location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Plan, deploy, and commission BTCL\'s FTTH and enterprise fibre network. CCNP/CCNA or BSNL equivalent, experience with GPON/XGS-PON platforms preferred.' },
    { id:'BTCL-002', title:'Enterprise Solutions Sales Manager',     dept:'B2B Sales',        location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Acquire and grow corporate clients for BTCL\'s managed ICT, cloud, and connectivity services. B2B telecoms sales track record essential.' },
  ],
  BOTASH: [
    { id:'BOTASH-001', title:'Chemical Process Engineer — Soda Ash', dept:'Operations',       location:'Sua Pan, Botswana',    type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Optimise Botash\'s solar evaporation and carbonation process at Sua Pan. BSc Chemical Engineering, 3+ yrs process plant experience in mineral extraction preferred.' },
    { id:'BOTASH-002', title:'Maintenance Planner',                  dept:'Maintenance',      location:'Sua Pan, Botswana',    type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Schedule and track preventive maintenance programmes for Botash\'s evaporator, crystalliser, and dryer equipment. SAP PM module and mechanical trade background.' },
  ],
  BIHL: [
    { id:'BIHL-001', title:'Insurance Underwriter — Life & Savings',  dept:'Life Insurance',   location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Assess life, disability, and savings product applications, set pricing, and manage reinsurance treaties for BIHL group. Actuarial or insurance qualification required.' },
    { id:'BIHL-002', title:'Financial Advisor',                       dept:'Wealth',           location:'Francistown, Botswana', type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Provide financial planning, retirement, and investment advice to BIHL clients. CFP or equivalent financial planning qualification and 3+ yrs advisory experience.' },
  ],
  CRESTA: [
    { id:'CRESTA-001', title:'Hotel General Manager',                dept:'Hospitality',      location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Lead operations, guest experience, and financial performance of a Cresta hotel property. 8+ yrs hotel management, hospitality degree, and proven P&L ownership.' },
    { id:'CRESTA-002', title:'Food & Beverage Manager',             dept:'F&B',              location:'Livingstone, Zambia',  type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Manage restaurant, bar, and banqueting operations at a Cresta property near Victoria Falls. Culinary/hospitality management qualification and 4+ yrs F&B leadership.' },
  ],
  SECHABA: [
    { id:'SECHABA-001', title:'Brand Activation Manager',            dept:'Marketing',        location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Plan and execute Sechaba Brewery brand events, trade activations, and sponsorship platforms across Botswana. FMCG/beverages marketing experience preferred.' },
    { id:'SECHABA-002', title:'Packaging Technician',               dept:'Operations',       location:'Gaborone, Botswana',   type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Operate and maintain bottling, labelling, and packaging lines at the Sechaba brewery. Trade qualification in mechanics or electrical with beverage industry experience.' },
  ],

  // ── NSX — Namibia ────────────────────────────────────────────────────────────
  FNBN: [
    { id:'FNBN-001', title:'Commercial Banking Manager',             dept:'Commercial Banking',location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Manage and grow a book of commercial banking clients for FNB Namibia. Experience in business credit, transactional banking, and relationship management required.' },
    { id:'FNBN-002', title:'Digital Banking Developer',              dept:'Technology',       location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Develop FNB Namibia\'s app and internet banking features. React Native, Java/Kotlin, and secure mobile banking API experience required.' },
  ],
  CGP: [
    { id:'CGP-001', title:'Corporate Credit Manager',               dept:'Credit Risk',      location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Evaluate and structure corporate loan facilities for Capricorn Group clients. CA(NAM) or risk qualification, 5+ yrs corporate credit experience required.' },
    { id:'CGP-002', title:'Group Strategy Analyst',                  dept:'Strategy',         location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-06', deadline:'2026-06-22', summary:'Support Capricorn Group\'s strategic planning process, M&A evaluation, and subsidiary performance monitoring. MBA or CFA with financial analysis skills.' },
  ],
  BIDVNA: [
    { id:'BIDVNA-001', title:'Trade and Industrial Products Manager', dept:'Sales',            location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Grow Bidvest Namibia\'s industrial distribution and services portfolio. B2B sales experience in Namibian commercial and mining sectors required.' },
    { id:'BIDVNA-002', title:'Logistics Operations Supervisor',       dept:'Logistics',        location:'Walvis Bay, Namibia',  type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Oversee warehousing and last-mile delivery operations at Bidvest Namibia\'s Walvis Bay facility. Supply chain management qualification preferred.' },
  ],
  OLDMUT_NA: [
    { id:'OLDMUT_NA-001', title:'Financial Advisor — Retirement',    dept:'Advisory',         location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Provide pension and retirement planning advice to individuals and employers. CFP (NAM) or RE5 qualification, 3+ yrs life assurance advisory experience.' },
    { id:'OLDMUT_NA-002', title:'Actuarial Analyst',                 dept:'Actuarial',        location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Perform valuation and pricing analysis for Old Mutual Namibia\'s life and savings portfolios. Part-qualified actuary (FIA/FSA) with 2+ yrs local experience preferred.' },
  ],
  NAMCO: [
    { id:'NAMCO-001', title:'Brewing Process Supervisor',            dept:'Operations',       location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Supervise lager brewing, fermentation, and filtration at Namibia Breweries. BSc Food Science or Chemical Engineering with brewing industry experience.' },
    { id:'NAMCO-002', title:'Sales Territory Manager',               dept:'Sales',            location:'Oshakati, Namibia',    type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Manage Windhoek Lager and Tafel distribution across the Northern Region. FMCG or beverages sales management, valid driving licence required.' },
  ],
  ORYX: [
    { id:'ORYX-001', title:'Property Asset Manager',                 dept:'Asset Management', location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Manage Oryx Properties\' commercial and retail portfolio to maximise NAV and income returns. BSc Property Studies or CPMD qualification, 4+ yrs property management.' },
    { id:'ORYX-002', title:'Lease Negotiation Officer',              dept:'Leasing',          location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Negotiate and execute lease agreements for Oryx commercial and retail spaces. Commercial property leasing background and contract drafting experience required.' },
  ],
  TCO: [
    { id:'TCO-001', title:'Microfinance Loan Officer',               dept:'Financial Services',location:'Windhoek, Namibia',   type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Originate and service consumer and housing microloans for Trustco Finance. Customer-facing sales experience, understanding of Namibian consumer credit regulations.' },
    { id:'TCO-002', title:'IT Infrastructure Specialist',            dept:'Technology',       location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Administer Trustco Group\'s server, storage, and network infrastructure. CCNA or MCSE certification, hybrid cloud (Azure) administration experience preferred.' },
  ],
  STANBK_NA: [
    { id:'STANBK_NA-001', title:'Business Banker — Growth Segment',  dept:'Business Banking', location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Grow Standard Bank Namibia\'s SME client base through lending, transactional, and FX solutions. Business banking experience and strong Namibian client network.' },
    { id:'STANBK_NA-002', title:'Compliance Analyst',                dept:'Compliance',       location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-07', deadline:'2026-06-22', summary:'Monitor adherence to NAMFISA and BoN regulatory requirements. CAMS or legal qualification, 3+ yrs bank compliance experience in Namibia.' },
  ],
  LHN: [
    { id:'LHN-001', title:'Credit Analyst — Payroll Lending',        dept:'Credit',           location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Assess and process payroll-deduction loan applications for Letshego Namibia civil servant clients. Credit analysis skills and understanding of Namibian employment law.' },
    { id:'LHN-002', title:'Customer Service Officer',                dept:'Operations',       location:'Oshikango, Namibia',   type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Process customer transactions, handle queries, and support agent banking onboarding at Letshego\'s Northern Namibia branches.' },
  ],
  OHLTHAVER: [
    { id:'OHLTHAVER-001', title:'Group Finance Manager',             dept:'Finance',          location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Lead financial reporting, treasury, and group consolidation for O&L Group\'s diversified Namibian operations. CA(NAM), 5+ yrs group finance experience.' },
    { id:'OHLTHAVER-002', title:'Retail Operations Manager',         dept:'Retail',           location:'Windhoek, Namibia',    type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Oversee Ongos Valley shopping centre and retail tenant management. Commercial property operations background and experience managing anchor tenants.' },
  ],

  // ── SEM — Mauritius ──────────────────────────────────────────────────────────
  MCB: [
    { id:'MCB-001', title:'Corporate Banking Relationship Manager',  dept:'Corporate Banking',location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Manage large corporate and institutional client relationships for MCB Group. Experience in structured lending, trade finance, and cross-border banking across East Africa.' },
    { id:'MCB-002', title:'Quantitative Analyst — Financial Markets', dept:'Trading',         location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Build pricing and risk models for MCB\'s fixed income and FX derivatives portfolio. Advanced Python, statistics, and Bloomberg experience required. CFA/FRM preferred.' },
    { id:'MCB-003', title:'Digital Transformation Manager',          dept:'Technology',       location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-04-28', deadline:'2026-06-13', summary:'Lead MCB\'s API banking, mobile wallet, and RegTech initiatives. Product management, open banking standards (PSD2/Open Finance), and fintech ecosystem experience.' },
  ],
  SBM: [
    { id:'SBM-001', title:'Global Business Banking Specialist',      dept:'Global Business',  location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Service global business companies and family offices using Mauritius as a gateway to Africa/Asia. Knowledge of Mauritius IFC regime, CRS/FATCA, and cross-border structuring.' },
    { id:'SBM-002', title:'Treasury Dealer',                         dept:'Treasury',         location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Execute FX, money market, and fixed income trades for SBM Holdings. ACI Dealing Certificate, Bloomberg Terminal proficiency, and 3+ yrs dealing room experience.' },
  ],
  ENL: [
    { id:'ENL-001', title:'Group Strategy & M&A Analyst',           dept:'Strategy',         location:'Ebene, Mauritius',      type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Support ENL Group\'s strategic planning, investment appraisal, and M&A activities across real estate, agribusiness, and logistics. MBA or CFA with 3+ yrs experience.' },
    { id:'ENL-002', title:'Real Estate Development Manager',        dept:'Property',         location:'Grand Baie, Mauritius', type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Manage the planning, permitting, and delivery of ENL\'s residential and mixed-use development projects. BSc Architecture or Property Development, 5+ yrs experience.' },
  ],
  CIEL: [
    { id:'CIEL-001', title:'Textile Production Manager',             dept:'Manufacturing',    location:'Vacoas, Mauritius',     type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Oversee garment manufacturing operations for CIEL Textile\'s export clients. BSc Industrial Engineering or Textile Technology, 5+ yrs production management in apparel.' },
    { id:'CIEL-002', title:'Healthcare Services Developer',          dept:'Healthcare',       location:'Pamplemousses, Mauritius',type:'Full-time',posted:'2026-05-04',deadline:'2026-06-19',summary:'Develop CIEL\'s medical and healthcare services portfolio in Mauritius and the Indian Ocean region. MBA in healthcare management, 5+ yrs healthcare strategy experience.' },
  ],
  ROGERS: [
    { id:'ROGERS-001', title:'Tourism & Hospitality Director',       dept:'Travel',           location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Lead Rogers\' travel and destination management portfolio including Beachcomber hotels. 10+ yrs luxury hospitality leadership, French language and regional market expertise.' },
    { id:'ROGERS-002', title:'Logistics Operations Manager',         dept:'Logistics',        location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Oversee Rogers Logistics warehousing and distribution operations. Supply chain qualification, Customs Management Systems experience, and 5+ yrs logistics leadership.' },
  ],
  IBL: [
    { id:'IBL-001', title:'Business Development Manager — Seafood',  dept:'Agribusiness',     location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Grow IBL\'s seafood export business across European and US markets. International seafood trade experience, strong buyer network, and French/English fluency.' },
    { id:'IBL-002', title:'Group IT Security Manager',               dept:'Technology',       location:'Ebene, Mauritius',      type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Define and implement IBL Group\'s cybersecurity framework across diversified subsidiaries. CISSP, SOC management, and ISO 27001 lead auditor experience required.' },
  ],
  PHOENIX: [
    { id:'PHOENIX-001', title:'Brand Manager — Phoenix Beer',        dept:'Marketing',        location:'Phoenix, Mauritius',    type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Lead brand strategy, campaigns, and consumer insight for Phoenix Beverages\' flagship lager brand. FMCG brand management, 4+ yrs beverages marketing experience.' },
    { id:'PHOENIX-002', title:'Brewery Process Technician',          dept:'Operations',       location:'Phoenix, Mauritius',    type:'Full-time', posted:'2026-05-06', deadline:'2026-06-22', summary:'Maintain fermentation, filtration, and packaging equipment at the Phoenix brewery. Electromechanical trade certificate, beverage manufacturing environment experience.' },
  ],
  SWAN: [
    { id:'SWAN-001', title:'Marine & Cargo Underwriter',             dept:'Underwriting',     location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Underwrite marine cargo, hull, and logistics policies for Swan General\'s commercial lines. ACII qualification, 4+ yrs marine insurance underwriting experience.' },
    { id:'SWAN-002', title:'Claims Executive — Motor & Property',    dept:'Claims',           location:'Curepipe, Mauritius',   type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Process and settle motor and property insurance claims fairly and efficiently. Insurance claims management training or ACII membership, 3+ yrs claims experience.' },
  ],
  HAREL: [
    { id:'HAREL-001', title:'ICT Solutions Account Manager',         dept:'Technology Sales', location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Sell Harel Mallac Technologies ICT, cloud, and managed services to Mauritian enterprises. 5+ yrs B2B technology sales, vendor certifications (IBM, HP, Cisco) preferred.' },
    { id:'HAREL-002', title:'Engineering Projects Manager',          dept:'Engineering',      location:'Port Louis, Mauritius', type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Manage Harel Mallac Engineering project delivery for industrial, ports, and construction sector clients. BSc Mechanical or Civil Engineering, PMP certification preferred.' },
  ],
  TERRA: [
    { id:'TERRA-001', title:'Cane Sugar Agronomy Manager',           dept:'Agriculture',      location:'Beau Plan, Mauritius',  type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Lead cane variety trials, soil management, and crop improvement programmes for Terra Mauricia\'s estates. BSc Tropical Agronomy with sugar industry experience required.' },
    { id:'TERRA-002', title:'Sugar Mill Process Engineer',           dept:'Manufacturing',    location:'Beau Plan, Mauritius',  type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Optimise milling, evaporation, and crystallisation operations at Terra Mauricia\'s factory. BSc Chemical or Mechanical Engineering, sugar mill experience preferred.' },
  ],

  // ── MSE — Malawi ─────────────────────────────────────────────────────────────
  NBM: [
    { id:'NBM-001', title:'Retail Banking Manager',                  dept:'Retail Banking',   location:'Blantyre, Malawi',     type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Lead retail banking sales and service delivery at NBM branches in Blantyre. 5+ yrs retail banking management, strong deposit growth and client acquisition record.' },
    { id:'NBM-002', title:'Treasury & FX Dealer',                   dept:'Treasury',         location:'Lilongwe, Malawi',     type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Execute MWK/USD/EUR foreign exchange and money market trades for National Bank of Malawi. ACI Foundation Certificate, Reuters Dealing experience preferred.' },
  ],
  NICO: [
    { id:'NICO-001', title:'Life Insurance Sales Manager',           dept:'Life Insurance',   location:'Lilongwe, Malawi',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Grow NICO Life\'s individual and group life insurance book. Insurance sales management background, COP in Insurance, and strong broker/agent network in Malawi.' },
    { id:'NICO-002', title:'Claims Assessor — General Insurance',    dept:'Claims',           location:'Blantyre, Malawi',     type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Investigate and settle general insurance claims including motor, property, and liability. Insurance qualification, 3+ yrs claims experience in Malawi or neighbouring markets.' },
  ],
  TNM: [
    { id:'TNM-001', title:'Network Planning Engineer',               dept:'Network',          location:'Blantyre, Malawi',     type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Plan and roll out TNM\'s 3G/4G network capacity and coverage across Malawi. BSc Telecommunications Engineering, experience with Nokia or Huawei RAN tools required.' },
    { id:'TNM-002', title:'Mobile Financial Services Product Manager',dept:'Digital',          location:'Lilongwe, Malawi',     type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Own TNM Mpamba mobile money product roadmap, integrations, and merchant ecosystem growth. Fintech product management and mobile money regulatory knowledge required.' },
  ],
  AIRTELMW: [
    { id:'AIRTELMW-001', title:'Enterprise Solutions Manager',       dept:'B2B',              location:'Lilongwe, Malawi',     type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Sell Airtel Malawi ICT, connectivity, and cloud solutions to large enterprise and government clients. B2B telecoms sales experience and Malawi government sector network.' },
    { id:'AIRTELMW-002', title:'Customer Experience Lead',          dept:'Customer Service', location:'Blantyre, Malawi',     type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Oversee Airtel Malawi\'s contact centre and retail service quality. NPS management, customer journey design, and 5+ yrs customer experience leadership.' },
  ],
  PCL: [
    { id:'PCL-001', title:'Group Finance Director',                  dept:'Finance',          location:'Blantyre, Malawi',     type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Lead Press Corporation\'s group financial reporting, treasury, and investor relations. CA(Malawi) or ACCA FCCA, 8+ yrs CFO or senior finance leadership in listed companies.' },
    { id:'PCL-002', title:'Investment Analyst',                      dept:'Corporate Dev',    location:'Blantyre, Malawi',     type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Support PCL\'s portfolio evaluation, M&A transactions, and subsidiary performance monitoring. CFA Level II+ or MBA Finance, 3+ yrs investment analysis experience.' },
  ],
  FMBCH: [
    { id:'FMBCH-001', title:'Corporate Banking Relationship Manager',dept:'Corporate Banking',location:'Blantyre, Malawi',     type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Manage large corporate and institutional client accounts for FMB Capital Holdings. 5+ yrs corporate banking lending and cross-selling track record in Malawi.' },
    { id:'FMBCH-002', title:'Digital Banking Officer',              dept:'Digital',          location:'Lilongwe, Malawi',     type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Drive FMB\'s mobile and internet banking user acquisition and feature adoption. Digital marketing and banking app product management experience required.' },
  ],
  ILLOVO: [
    { id:'ILLOVO-001', title:'Agronomy Extension Officer — Sugarcane',dept:'Agriculture',     location:'Nchalo, Malawi',       type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Provide agronomy advisory and extension services to Illovo outgrower farmers in the Shire Valley. BSc Agriculture, strong field engagement and Chichewa communication skills.' },
    { id:'ILLOVO-002', title:'Process Chemist',                      dept:'Factory',          location:'Nchalo, Malawi',       type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Monitor and optimise sugar refining process chemistry at Illovo\'s Nchalo factory. BSc Chemistry or Chemical Engineering, sugar industry experience advantageous.' },
  ],
  SUNBIRD: [
    { id:'SUNBIRD-001', title:'Hotel Operations Manager',            dept:'Hospitality',      location:'Mangochi, Malawi',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Manage daily hotel operations at Sunbird Nkopola Lodge on Lake Malawi. Hospitality degree, 5+ yrs lodge operations management, and proven guest satisfaction record.' },
    { id:'SUNBIRD-002', title:'Sales & Events Coordinator',         dept:'Sales',            location:'Lilongwe, Malawi',     type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Coordinate conferencing, weddings, and corporate events business for Sunbird Tourism. Events management background and Malawi corporate client network advantageous.' },
  ],
  STANBIC_MW: [
    { id:'STANBIC_MW-001', title:'Business Banking Advisor',         dept:'Business Banking', location:'Blantyre, Malawi',     type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Grow and manage SME client portfolios for Stanbic Bank Malawi. Business lending, transactional banking, and client relationship management experience required.' },
    { id:'STANBIC_MW-002', title:'Compliance Officer',              dept:'Compliance',       location:'Lilongwe, Malawi',     type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Ensure RBM regulatory compliance, AML/CFT implementation, and conduct monitoring for Stanbic Malawi. Legal or compliance qualification, 3+ yrs banking compliance.' },
  ],
  LAFARGE_MW: [
    { id:'LAFARGE_MW-001', title:'Process Engineer — Cement Plant',  dept:'Operations',       location:'Zomba, Malawi',        type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Optimise kiln, raw mill, and cement mill operations at Lafarge Malawi\'s plant. BSc Chemical or Mechanical Engineering with cement or minerals processing experience.' },
    { id:'LAFARGE_MW-002', title:'Commercial Sales Representative',  dept:'Sales',            location:'Blantyre, Malawi',     type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Grow Lafarge Malawi\'s cement and construction materials sales with distributors, hardware retailers, and large construction projects across Southern Malawi.' },
  ],

  // ── BVMT — Tunisia ───────────────────────────────────────────────────────────
  ATTIJARITN: [
    { id:'ATTIJARITN-001', title:'Corporate Banking Relationship Manager',dept:'Corporate Banking',location:'Tunis, Tunisia',    type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Manage large corporate client relationships for Attijari Bank Tunisie. Arabic and French bilingual, 5+ yrs corporate banking in North Africa preferred.' },
    { id:'ATTIJARITN-002', title:'Digital Banking Product Officer',   dept:'Digital',          location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Drive Attijari Bank TN\'s mobile banking and digital payment product roadmap. Fintech product management, open banking, and BCB regulatory knowledge required.' },
  ],
  BIAT: [
    { id:'BIAT-001', title:'Capital Markets Analyst',                dept:'Financial Markets',location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Analyse Tunisian equity and fixed income markets, produce research reports, and support BIAT\'s asset management portfolio decisions. CFA progress preferred.' },
    { id:'BIAT-002', title:'Private Banker',                         dept:'Private Banking',  location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Manage HNWI client portfolios for BIAT Private Banking, providing investment, estate, and tax planning advisory. 5+ yrs wealth management experience, French/Arabic bilingual.' },
  ],
  SFBT: [
    { id:'SFBT-001', title:'Brand Manager — Boga & Celtia',         dept:'Marketing',        location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Lead marketing strategy and consumer campaigns for SFBT\'s flagship Boga juices and Celtia beer brands. FMCG marketing, 4+ yrs beverages brand management, French required.' },
    { id:'SFBT-002', title:'Quality Control Supervisor',             dept:'Quality Assurance',location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Oversee in-process and finished product quality testing at SFBT\'s beverage plants. BSc Food Science or Chemistry, ISO 9001/FSSC 22000 and French required.' },
  ],
  POULINA: [
    { id:'POULINA-001', title:'Group Finance Controller',            dept:'Finance',          location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Lead financial control and management reporting for Poulina Group Holding\'s diversified subsidiaries. DSCG or IFRS-qualified accountant, 5+ yrs group finance experience.' },
    { id:'POULINA-002', title:'Agri-Food Sales Manager — Export',    dept:'Sales',            location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Grow Poulina\'s poultry and processed food exports to Sub-Saharan Africa and Gulf markets. FMCG export sales management, Arabic/French/English trilingual preferred.' },
  ],
  DELICE: [
    { id:'DELICE-001', title:'Dairy Innovation Manager',             dept:'R&D',              location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Lead new product development for Delice Holding\'s dairy portfolio. BSc Food Technology, yogurt and cheese production experience, and consumer insight-driven NPD process expertise.' },
    { id:'DELICE-002', title:'Distribution Network Manager',         dept:'Sales',            location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Optimise Delice\'s route-to-market coverage and distributor management across Greater Tunis and coastal regions. FMCG sales operations and distribution management background.' },
  ],
  ORANGE_TN: [
    { id:'ORANGE_TN-001', title:'5G Programme Manager',              dept:'Network',          location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Lead Orange Tunisie\'s 5G SA architecture rollout. RAN/core network programme management experience, Nokia/Ericsson vendor background, and French/Arabic required.' },
    { id:'ORANGE_TN-002', title:'Enterprise Account Executive',      dept:'B2B',              location:'Sfax, Tunisia',        type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Acquire and manage large enterprise accounts for Orange Tunisie\'s ICT, connectivity, and cloud services in Southern Tunisia. B2B telecoms sales background required.' },
  ],
  TELNET_TN: [
    { id:'TELNET_TN-001', title:'Software Engineer — Embedded Systems',dept:'Engineering',   location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Develop firmware and middleware for Telnet\'s IoT and connected devices. C/C++, RTOS, and Zigbee/LoRaWAN/BLE protocol experience required. French/Arabic.' },
    { id:'TELNET_TN-002', title:'AI Solutions Architect',             dept:'Innovation',       location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-06', deadline:'2026-06-22', summary:'Design and deploy AI/ML solutions for Telnet\'s enterprise clients. Python, TensorFlow/PyTorch, cloud (Azure/AWS), and French language skills required.' },
  ],
  ALKIMIA: [
    { id:'ALKIMIA-001', title:'Chemical Process Engineer',            dept:'Operations',       location:'Gabes, Tunisia',       type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Operate and optimise Alkimia\'s chlor-alkali production and caustic soda processing plant. BSc Chemical Engineering, electrochemistry and continuous processing experience.' },
    { id:'ALKIMIA-002', title:'Environmental & Safety Officer',       dept:'HSE',              location:'Gabes, Tunisia',       type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Manage Alkimia\'s ISO 14001 and ISO 45001 compliance and chemical plant emergency response programme. Process safety qualification and French required.' },
  ],
  CITYC: [
    { id:'CITYC-001', title:'Automotive Brand Representative',        dept:'Sales',            location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Represent City Cars\' Kia and Suzuki dealerships to retail and fleet clients. Strong automotive product knowledge, customer relationship skills, and French language.' },
    { id:'CITYC-002', title:'After-Sales Service Advisor',            dept:'After-Sales',      location:'Sfax, Tunisia',        type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Manage customer vehicle service bookings, communicate repair estimates, and ensure customer satisfaction at City Cars service centres across Tunisia.' },
  ],
  STAR_TN: [
    { id:'STAR_TN-001', title:'Motor Insurance Underwriter',          dept:'Underwriting',     location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Assess and price motor fleet and individual vehicle insurance risks for STAR\'s commercial lines. Insurance underwriting qualification, French/Arabic, 3+ yrs motor experience.' },
    { id:'STAR_TN-002', title:'Actuary — Life & Health Reserves',    dept:'Actuarial',        location:'Tunis, Tunisia',       type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Perform life and health insurance reserving, pricing, and experience analysis. Part-qualified actuary, DSCG, or equivalent quantitative qualification required.' },
  ],

  // ── DSE — Tanzania ───────────────────────────────────────────────────────────
  CRDB: [
    { id:'CRDB-001', title:'Corporate Banking Manager',              dept:'Corporate Banking',location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-12',deadline:'2026-06-27',summary:'Manage large corporate client relationships for CRDB Bank Tanzania. Structured lending, trade finance, and FX hedging experience. Swahili and English required.' },
    { id:'CRDB-002', title:'Digital Product Manager — CRDBKwikPesa', dept:'Digital Banking',  location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-05',deadline:'2026-06-20',summary:'Drive mobile money and agency banking product growth for CRDB\'s CRDBKwikPesa platform. Mobile financial services product management, API integration, and DFS regulatory knowledge.' },
    { id:'CRDB-003', title:'Graduate Trainee Programme',             dept:'Graduate Talent',  location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-04-28',deadline:'2026-06-13',summary:'CRDB Bank\'s two-year graduate development programme rotating across retail, corporate, operations, and technology. First class or upper second honours from Tanzanian universities.' },
  ],
  NMB_TZ: [
    { id:'NMB_TZ-001', title:'Agri-Finance Specialist',              dept:'Agricultural Banking',location:'Dodoma, Tanzania',  type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Structure and manage agricultural value chain financing products for NMB Bank Tanzania\'s smallholder and commercial farmer clients. Agri-finance and rural banking background.' },
    { id:'NMB_TZ-002', title:'Technology Risk Officer',              dept:'Risk',             location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-06',deadline:'2026-06-21',summary:'Identify and mitigate IT and cyber risks across NMB\'s core banking and digital platforms. CISA or CRISC certification preferred, Tanzanian banking regulatory knowledge.' },
  ],
  TBL_TZ: [
    { id:'TBL_TZ-001', title:'Trade Marketing Manager',              dept:'Commercial',       location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-14',deadline:'2026-06-30',summary:'Execute Tanzania Breweries\' trade activation, outlet management, and distributor programmes. FMCG trade marketing, 4+ yrs beverages industry experience, Swahili required.' },
    { id:'TBL_TZ-002', title:'Brewery Quality Manager',              dept:'Quality Assurance',location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-07',deadline:'2026-06-23',summary:'Lead quality systems and product testing across TBL\'s brewing and packaging operations. BSc Food Science or Chemistry, Brewing & Distilling qualification, ISO 9001 experience.' },
  ],
  TCCL: [
    { id:'TCCL-001', title:'Leaf Tobacco Technology Manager',        dept:'Leaf Operations',  location:'Morogoro, Tanzania',   type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Manage Tanzania Cigarette Company\'s leaf tobacco procurement, grading, and agronomy support programmes. BSc Agriculture, tobacco leaf processing experience required.' },
    { id:'TCCL-002', title:'Brand Marketing Manager',                dept:'Marketing',        location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-08',deadline:'2026-06-24',summary:'Develop and execute brand strategies for TCCL\'s cigarette portfolio in Tanzania. FMCG marketing management, Swahili fluency, and strong regulatory awareness required.' },
  ],
  TPCC: [
    { id:'TPCC-001', title:'Cement Plant Operations Engineer',        dept:'Manufacturing',    location:'Wazo Hill, Dar es Salaam',type:'Full-time',posted:'2026-05-11',deadline:'2026-06-26',summary:'Operate and optimise TPCC\'s cement kiln, raw and finish mill equipment. BSc Mechanical or Chemical Engineering, 3+ yrs cement plant operations, Swahili preferred.' },
    { id:'TPCC-002', title:'Sales Territory Manager — Northern Zone', dept:'Sales',            location:'Arusha, Tanzania',     type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Grow TPCC cement sales through distributors, hardware retailers, and large infrastructure projects across Northern Tanzania. FMCG/construction materials sales background.' },
  ],
  VODA_TZ: [
    { id:'VODA_TZ-001', title:'M-Pesa Product Innovation Manager',   dept:'Digital Services', location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-16',deadline:'2026-07-02',summary:'Drive new M-Pesa product features and merchant integrations for Vodacom Tanzania. Mobile money product management, DFS ecosystem expertise, and API/open banking knowledge.' },
    { id:'VODA_TZ-002', title:'Network Quality Engineer',             dept:'Network',          location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-09',deadline:'2026-06-25',summary:'Monitor and improve LTE/5G NSA radio access network KPIs for Vodacom Tanzania. Ericsson/Huawei OSS experience, drive test and network optimisation skills required.' },
  ],
  STANBIC_TZ: [
    { id:'STANBIC_TZ-001', title:'Transactional Banking Specialist',  dept:'Corporate Banking',location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-13',deadline:'2026-06-28',summary:'Sell cash management, payroll, and trade solutions to Stanbic Tanzania\'s corporate and public sector clients. Transaction banking background and Tanzania market knowledge.' },
    { id:'STANBIC_TZ-002', title:'AML Compliance Analyst',            dept:'Compliance',       location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-06',deadline:'2026-06-21',summary:'Perform AML transaction monitoring and investigation for Stanbic Tanzania. CAMS certification preferred, understanding of BoT and FATF compliance requirements.' },
  ],
  KCB_TZ: [
    { id:'KCB_TZ-001', title:'Retail Banking Officer',               dept:'Retail Banking',   location:'Mwanza, Tanzania',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Serve individual and SME clients at KCB Bank Tanzania branches. Deposit mobilisation, product cross-selling, and customer service skills. Banking qualification preferred.' },
    { id:'KCB_TZ-002', title:'Mortgage Products Manager',            dept:'Home Loans',       location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-07',deadline:'2026-06-23',summary:'Manage and grow KCB Tanzania\'s home loan and affordable housing portfolio. Mortgage lending, property valuation, and Tanzania housing finance market knowledge.' },
  ],
  DCB: [
    { id:'DCB-001', title:'Community Banking Officer',               dept:'Microfinance',     location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-12',deadline:'2026-06-27',summary:'Originate and manage microfinance loans for DCB Commercial Bank\'s low-income and informal sector clients. Community development finance background and Swahili required.' },
    { id:'DCB-002', title:'Operations Supervisor',                    dept:'Operations',       location:'Dodoma, Tanzania',     type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Oversee branch teller, vault, and back-office operations at DCB Commercial Bank. Banking operations experience and Bank of Tanzania payments system knowledge required.' },
  ],
  EQUITY_TZ: [
    { id:'EQUITY_TZ-001', title:'Business Development Manager — SME',dept:'Business Banking', location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-15',deadline:'2026-07-01',summary:'Acquire and grow Equity Bank Tanzania\'s SME banking portfolio through lending, mobile, and merchant payment solutions. 4+ yrs SME banking and Tanzanian market knowledge.' },
    { id:'EQUITY_TZ-002', title:'EazzyBanking Mobile Specialist',    dept:'Digital',          location:'Dar es Salaam, Tanzania',type:'Full-time',posted:'2026-05-08',deadline:'2026-06-24',summary:'Drive adoption of Equity\'s EazzyBanking app and agent banking channels in Tanzania. Mobile banking product experience, community banking, and Swahili language required.' },
  ],

  // ── ZSE — Zimbabwe ───────────────────────────────────────────────────────────
  ECONET: [
    { id:'ECONET-001', title:'EcoCash Product Manager',              dept:'Fintech',          location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Lead EcoCash product strategy, merchant ecosystem expansion, and interoperability initiatives. Mobile money product management, RBZ regulatory understanding, and Shona/English bilingual.' },
    { id:'ECONET-002', title:'5G Network Engineer',                  dept:'Technology',       location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Plan and deploy Econet\'s 5G NSA network across Harare CBD and key urban centres. Ericsson or Huawei RAN experience, BSc Telecommunications Engineering required.' },
    { id:'ECONET-003', title:'Enterprise ICT Solutions Manager',     dept:'B2B',              location:'Bulawayo, Zimbabwe',   type:'Full-time', posted:'2026-04-28', deadline:'2026-06-13', summary:'Grow Econet\'s enterprise ICT and connectivity revenues across Bulawayo and Matabeleland. 5+ yrs B2B telecoms sales, strong Zimbabwean corporate client network.' },
  ],
  DELTA_ZW: [
    { id:'DELTA_ZW-001', title:'Brewing Operations Manager',          dept:'Manufacturing',    location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Oversee brewing, fermentation, and packaging operations at Delta Beverages. BSc Food Science or Chemical Engineering with brewery management experience.' },
    { id:'DELTA_ZW-002', title:'Trade Marketing Executive',           dept:'Commercial',       location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Execute Delta\'s outlet activation and distributor development programmes for Castle Lager and Chibuku brands across Harare and Midlands provinces.' },
  ],
  INNSCOR: [
    { id:'INNSCOR-001', title:'Franchise Operations Manager',         dept:'QSR Operations',   location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Oversee Innscor\'s Chicken Inn, Pizza Inn, and Creamy Inn QSR network operations across Zimbabwe. Franchise operations background and 5+ yrs QSR management experience.' },
    { id:'INNSCOR-002', title:'Supply Chain Manager — FMCG',          dept:'Supply Chain',     location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Manage procurement, cold chain logistics, and distribution for Innscor\'s food manufacturing and QSR subsidiaries. CIPS qualification and FMCG supply chain management.' },
  ],
  CBZ: [
    { id:'CBZ-001', title:'Corporate Lending Manager',               dept:'Corporate Banking',location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Structure and manage corporate loan facilities for CBZ Holdings\' large corporate and government-linked clients. 6+ yrs corporate credit and banking experience in Zimbabwe.' },
    { id:'CBZ-002', title:'InsurTech Product Manager — CBZ Life',    dept:'Insurance',        location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Drive CBZ Life\'s digital insurance products including mobile and bancassurance channels. Insurance product management, RBZ IPEC regulatory knowledge, and fintech background.' },
  ],
  FBC_ZW: [
    { id:'FBC_ZW-001', title:'Treasury Manager',                     dept:'Treasury',         location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Manage FBC Holdings\' liquidity, foreign exchange, and money market operations. Treasury qualification, RBZ forex regulations knowledge, and Bloomberg Terminal experience.' },
    { id:'FBC_ZW-002', title:'Business Banking Advisor',             dept:'Business Banking', location:'Gweru, Zimbabwe',      type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Grow FBC Bank\'s SME client portfolio in Midlands province. Business lending, transactional banking, and strong Zimbabwean agricultural sector understanding preferred.' },
  ],
  STANBIC_ZW: [
    { id:'STANBIC_ZW-001', title:'Capital Markets Analyst',          dept:'Investment Banking',location:'Harare, Zimbabwe',    type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Support Stanbic Zimbabwe\'s ZSE capital markets and advisory mandates. Financial modelling, IFRS reporting, and ZSE/Zimbabwe Securities and Exchange Commission knowledge.' },
    { id:'STANBIC_ZW-002', title:'Compliance Manager — ZPCS Reporting',dept:'Compliance',     location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Manage RBZ, ZACC, and FATF compliance programmes at Stanbic Zimbabwe. CAMS, legal qualification, 5+ yrs banking compliance in Zimbabwe required.' },
  ],
  OLDMUT_ZW: [
    { id:'OLDMUT_ZW-001', title:'Unit Trust Portfolio Manager',       dept:'Asset Management', location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Manage Old Mutual Zimbabwe\'s equity and money market unit trust funds. CFA charterholder, 5+ yrs buy-side investment management, ZSE equities expertise required.' },
    { id:'OLDMUT_ZW-002', title:'Actuarial Analyst',                 dept:'Actuarial',        location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Support life insurance reserving and pricing for Old Mutual Zimbabwe. Part-qualified actuary (IFoA or Actuarial Society of South Africa), 2+ yrs local experience.' },
  ],
  SIMBISA: [
    { id:'SIMBISA-001', title:'QSR Operations Manager — East Africa', dept:'International Ops',location:'Nairobi, Kenya',       type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Manage Simbisa Brands\' Chicken Inn and Pizza Inn outlets across Kenya and Uganda. QSR multi-unit operations experience, P&L management, and East Africa market knowledge.' },
    { id:'SIMBISA-002', title:'Supply Chain & Procurement Specialist',dept:'Procurement',      location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Source food ingredients, packaging, and logistics for Simbisa\'s regional franchise network. CIPS qualification and FMCG food procurement experience required.' },
  ],
  SEEDCO_ZW: [
    { id:'SEEDCO_ZW-001', title:'Plant Breeder — Maize',             dept:'R&D',              location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Lead SeedCo\'s maize hybrid breeding programme for Southern and East African markets. PhD Plant Breeding or BSc with 5+ yrs applied breeding experience required.' },
    { id:'SEEDCO_ZW-002', title:'Agri-Business Development Manager', dept:'Sales',            location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Grow SeedCo\'s certified seed sales through dealer networks and outgrower programmes across Zambia and Malawi. Agribusiness sales management, 4+ yrs seed industry experience.' },
  ],
  NATFOODS: [
    { id:'NATFOODS-001', title:'Milling Operations Manager',          dept:'Operations',       location:'Harare, Zimbabwe',     type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Lead wheat milling and maize processing operations at National Foods Zimbabwe. BSc Food Science or Milling Technology, 5+ yrs grain milling operations management.' },
    { id:'NATFOODS-002', title:'Commercial Sales Manager — Retail',   dept:'Sales',            location:'Bulawayo, Zimbabwe',   type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Manage National Foods\' retail and wholesale distributor network across Matabeleland. FMCG sales management, strong Zimbabwean retailer relationships, and P&L accountability.' },
  ],

  // ── LUSE — Zambia ────────────────────────────────────────────────────────────
  ZAMBEEF: [
    { id:'ZAMBEEF-001', title:'Agribusiness Development Manager',    dept:'Agriculture',      location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Develop Zambeef\'s outgrower and contract farming programmes across Zambia. BSc Agribusiness or Agricultural Economics, 5+ yrs agribusiness operations in Sub-Saharan Africa.' },
    { id:'ZAMBEEF-002', title:'Cold Chain Logistics Supervisor',     dept:'Logistics',        location:'Kitwe, Zambia',        type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Manage refrigerated transport and cold storage operations for Zambeef\'s Copperbelt distribution network. Cold chain logistics experience and food safety qualification required.' },
    { id:'ZAMBEEF-003', title:'Retail Operations Manager — Shoprite Meat',dept:'Retail',      location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-04-29', deadline:'2026-06-14', summary:'Oversee Zambeef\'s in-store meat counters across the Shoprite and other key retail chains in Zambia. Retail food operations management, HACCP, and 4+ yrs meat retail experience.' },
  ],
  ZANACO: [
    { id:'ZANACO-001', title:'Agricultural Finance Manager',          dept:'Agriculture Banking',location:'Lusaka, Zambia',    type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Develop and manage agricultural lending products for ZANACO\'s smallholder and commercial farming clients. Agri-finance background, Bank of Zambia regulatory knowledge required.' },
    { id:'ZANACO-002', title:'Digital Banking Product Manager',       dept:'Digital',          location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Lead ZANACO\'s Xapit mobile money and internet banking product strategy. Mobile financial services product management and Zambia DFS ecosystem experience preferred.' },
  ],
  CEC: [
    { id:'CEC-001', title:'Power Systems Engineer',                  dept:'Engineering',      location:'Kitwe, Zambia',        type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Maintain and optimise CEC\'s 220kV transmission infrastructure on the Copperbelt. BSc Electrical Engineering, HV substation operations, and ERB licensing knowledge required.' },
    { id:'CEC-002', title:'Commercial Manager — Mining Utilities',   dept:'Commercial',       location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Negotiate power supply agreements and manage large mining customer accounts for CEC. Energy contracts, PPA structuring, and Zambia mining sector knowledge required.' },
  ],
  ZAMBREW: [
    { id:'ZAMBREW-001', title:'Master Brewer',                       dept:'Brewing',          location:'Ndola, Zambia',        type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Lead Zambia Breweries\' brewing operations and quality programmes at the Ndola plant. MSc Brewing Science or IOB/IBD Master Brewer qualification, 5+ yrs brewery leadership.' },
    { id:'ZAMBREW-002', title:'Sales Territory Manager',             dept:'Sales',            location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Grow Zambia Breweries\' Mosi and Castle Lager market share through distributor and outlet management. FMCG/beverage territory sales experience and Zambia market knowledge.' },
  ],
  ZCCM_IH: [
    { id:'ZCCM_IH-001', title:'Portfolio Investment Analyst',        dept:'Investments',      location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-16', deadline:'2026-07-02', summary:'Analyse ZCCM-IH\'s mining and industrial equity portfolio, prepare board investment papers, and monitor portfolio performance. CFA Level II+, mining sector valuation experience.' },
    { id:'ZCCM_IH-002', title:'Corporate Finance Manager',           dept:'Finance',          location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-09', deadline:'2026-06-25', summary:'Manage ZCCM-IH\'s capital structure, dividend policy, and corporate transactions. ACCA/CIMA qualified, 6+ yrs corporate finance or treasury in mining or natural resources.' },
  ],
  STANDARD_ZM: [
    { id:'STANDARD_ZM-001', title:'Wholesale Banking Relationship Manager',dept:'Wholesale',  location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-12', deadline:'2026-06-27', summary:'Manage large corporate and institutional client relationships for Standard Chartered Zambia. Structured finance, trade, and FX solutions expertise. 6+ yrs corporate banking.' },
    { id:'STANDARD_ZM-002', title:'International Graduate Programme — Zambia',dept:'Graduate',location:'Lusaka, Zambia',     type:'Full-time', posted:'2026-05-05', deadline:'2026-06-20', summary:'Standard Chartered\'s global 18-month graduate programme. Zambia cohort rotations across wholesale banking, retail, risk, and finance. Strong academic record required.' },
  ],
  AIRTELZM: [
    { id:'AIRTELZM-001', title:'Airtel Money Product Manager',        dept:'Digital Services', location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-13', deadline:'2026-06-28', summary:'Own Airtel Money Zambia product strategy including merchant payments, bulk disbursements, and cross-border remittances. Mobile money product management, BoZ PSRPA knowledge.' },
    { id:'AIRTELZM-002', title:'Network Coverage Planning Engineer', dept:'Network',          location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-06', deadline:'2026-06-21', summary:'Plan and optimise Airtel Zambia\'s 4G LTE-A coverage across urban and peri-urban areas. RAN planning tools (Atoll/ICS), BSc Telecommunications Engineering required.' },
  ],
  STANBIC_ZM: [
    { id:'STANBIC_ZM-001', title:'Business Banking Advisor',          dept:'Business Banking', location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-14', deadline:'2026-06-30', summary:'Grow and manage Stanbic Zambia\'s SME and business banking portfolio. Business lending, FX, and transactional banking experience. Strong Zambian SME client network.' },
    { id:'STANBIC_ZM-002', title:'Trade Finance Officer',             dept:'Trade Finance',    location:'Ndola, Zambia',        type:'Full-time', posted:'2026-05-07', deadline:'2026-06-23', summary:'Process import/export documentary credits, guarantees, and supply chain finance for Stanbic Zambia corporate clients. ICC CDCS certification, 3+ yrs trade finance experience.' },
  ],
  ZAMBIA_SUGAR: [
    { id:'ZAMBIA_SUGAR-001', title:'Agronomy Manager — Cane Development',dept:'Agriculture',  location:'Mazabuka, Zambia',     type:'Full-time', posted:'2026-05-15', deadline:'2026-07-01', summary:'Lead Zambia Sugar\'s cane agronomy research, irrigation management, and outgrower support programmes in Mazabuka. BSc Agronomy, sugarcane cultivation experience required.' },
    { id:'ZAMBIA_SUGAR-002', title:'Process Engineer — Sugar Factory', dept:'Manufacturing',   location:'Mazabuka, Zambia',     type:'Full-time', posted:'2026-05-08', deadline:'2026-06-24', summary:'Optimise cane milling, evaporation, and crystallisation at Zambia Sugar\'s Nakambala estate factory. BSc Chemical Engineering, 3+ yrs sugar mill operations experience.' },
  ],
  CHILANGA: [
    { id:'CHILANGA-001', title:'Kiln Operations Supervisor',          dept:'Manufacturing',    location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-11', deadline:'2026-06-26', summary:'Supervise pyroprocessing and clinker production at Chilanga Cement\'s rotary kiln. BSc Mechanical or Chemical Engineering, 3+ yrs cement kiln operations experience.' },
    { id:'CHILANGA-002', title:'Regional Sales Manager — Lusaka',     dept:'Sales',            location:'Lusaka, Zambia',       type:'Full-time', posted:'2026-05-04', deadline:'2026-06-19', summary:'Manage Chilanga Cement\'s Lusaka and Central Province dealer and construction project sales. Building materials sales background and strong Zambian contractor network required.' },
  ],
};
