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
};
