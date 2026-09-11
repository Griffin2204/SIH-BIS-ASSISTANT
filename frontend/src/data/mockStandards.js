// Mock Database for Indian Standards (BIS)

export const MOCK_STANDARDS = [
  {
    id: 'IS-10500-2012',
    code: 'IS 10500:2012',
    title: 'Drinking Water Specification (Second Revision)',
    category: 'Food & Water Safety',
    department: 'Food and Agriculture Department (FAD)',
    mandatory: true,
    status: 'Active',
    revisionDate: '2012-06-01',
    description: 'Prescribes the quality requirements for drinking water supplied to the public or packaged for consumption. Includes physical, chemical, toxic, and bacteriological standards.',
    keyParameters: [
      { parameter: 'pH Value', limit: '6.5 to 8.5', unit: '-' },
      { parameter: 'Total Dissolved Solids (TDS)', limit: '500 max (2000 in absence of alternate source)', unit: 'mg/l' },
      { parameter: 'Turbidity', limit: '1 max (5 in absence of alternate source)', unit: 'NTU' },
      { parameter: 'Lead (as Pb)', limit: '0.01 max', unit: 'mg/l' },
      { parameter: 'Arsenic (as As)', limit: '0.01 max', unit: 'mg/l' },
      { parameter: 'E. Coli / Coliform Bacteria', limit: 'Shall not be detectable in any 100 ml sample', unit: 'CFU' }
    ],
    officialUrl: 'https://www.services.bis.gov.in/php/BIS_2/bis_cafe/standards/is_10500_2012.pdf',
    compulsoryScheme: 'Scheme-I (ISI Mark)',
    summary: 'Essential standard for public health and packaged drinking water plants across India.'
  },
  {
    id: 'IS-694-2010',
    code: 'IS 694:2010',
    title: 'Polyvinyl Chloride Insulated Cables for Working Voltages up to and Including 1100 V',
    category: 'Electrical & Electronics',
    department: 'Electrotechnical Department (ETD)',
    mandatory: true,
    status: 'Active',
    revisionDate: '2010-11-15',
    description: 'Specifies safety, insulation, and conductor requirements for PVC insulated single-core and multi-core electric cables used in domestic wiring and industrial apparatus.',
    keyParameters: [
      { parameter: 'Voltage Rating', limit: 'Up to 1100V AC', unit: 'V' },
      { parameter: 'Conductor Resistance', limit: 'Max 12.1 ohm/km at 20°C (for 1.5 sq mm)', unit: 'ohm/km' },
      { parameter: 'Insulation Resistance', limit: 'Min 10 M ohm-km at 70°C', unit: 'M ohm-km' },
      { parameter: 'Flame Retardancy', limit: 'Passes Category A test', unit: '-' }
    ],
    officialUrl: 'https://www.services.bis.gov.in/php/BIS_2/bis_cafe/standards/is_694_2010.pdf',
    compulsoryScheme: 'Scheme-I (ISI Mark)',
    summary: 'Mandatory ISI mark for all building wiring cables manufactured or imported in India.'
  },
  {
    id: 'IS-13630-2019',
    code: 'IS 13630:2019',
    title: 'Ceramic Tiles - Sampling and Methods of Test (Parts 1 to 15)',
    category: 'Civil Engineering & Building Materials',
    department: 'Civil Engineering Department (CED)',
    mandatory: true,
    status: 'Active',
    revisionDate: '2019-03-20',
    description: 'Covers test methods for determining dimensions, surface quality, water absorption, breaking strength, modulus of rupture, and chemical resistance of ceramic tiles.',
    keyParameters: [
      { parameter: 'Water Absorption (Group BIa)', limit: 'E ≤ 0.5%', unit: '%' },
      { parameter: 'Breaking Strength', limit: 'Min 1300 N (for thickness ≥ 7.5 mm)', unit: 'N' },
      { parameter: 'Modulus of Rupture', limit: 'Min 35 N/mm²', unit: 'N/mm²' },
      { parameter: 'Deep Abrasion Resistance', limit: 'Max 175 mm³', unit: 'mm³' }
    ],
    officialUrl: 'https://www.services.bis.gov.in/php/BIS_2/bis_cafe/standards/is_13630_2019.pdf',
    compulsoryScheme: 'Quality Control Order (QCO)',
    summary: 'Mandatory for ceramic tile manufacturers under the Ministry of Commerce QCO.'
  },
  {
    id: 'IS-15652-2006',
    code: 'IS 15652:2006',
    title: 'Insulating Mats for Electrical Purposes - Specification',
    category: 'Electrical & Safety Equipment',
    department: 'Electrotechnical Department (ETD)',
    mandatory: true,
    status: 'Active',
    revisionDate: '2006-08-10',
    description: 'Specifies requirements for elastomer insulating mats used as floor covering for protection of workers near high voltage electrical apparatus.',
    keyParameters: [
      { parameter: 'Dielectric Strength', limit: 'Up to 30 kV AC for Class 2', unit: 'kV' },
      { parameter: 'Tensile Strength', limit: 'Min 15 N/mm²', unit: 'N/mm²' },
      { parameter: 'Elongation at Break', limit: 'Min 250%', unit: '%' },
      { parameter: 'Leakage Current', limit: 'Less than 10 mA at proof voltage', unit: 'mA' }
    ],
    officialUrl: 'https://www.services.bis.gov.in/php/BIS_2/bis_cafe/standards/is_15652_2006.pdf',
    compulsoryScheme: 'Scheme-I (ISI Mark)',
    summary: 'Essential occupational safety requirement in sub-stations and control rooms.'
  },
  {
    id: 'IS-14286-2019',
    code: 'IS 14286:2019 / IEC 61215',
    title: 'Terrestrial Photovoltaic (PV) Modules - Design Qualification and Type Approval',
    category: 'Renewable Energy & Solar',
    department: 'Renewable Energy Department (RED)',
    mandatory: true,
    status: 'Active',
    revisionDate: '2019-12-05',
    description: 'Lays down requirements for design qualification and type approval of terrestrial solar PV modules suitable for long-term operation in outdoor climates.',
    keyParameters: [
      { parameter: 'Maximum Power Output Pmax', limit: 'Within ±3% of nameplate rating', unit: 'W' },
      { parameter: 'Damp Heat Test', limit: '1000 hours at 85°C / 85% RH', unit: 'hours' },
      { parameter: 'Thermal Cycling Test', limit: '200 cycles from -40°C to +85°C', unit: 'cycles' },
      { parameter: 'Insulation Resistance', limit: 'Min 40 M ohm-m²', unit: 'M ohm-m²' }
    ],
    officialUrl: 'https://www.services.bis.gov.in/php/BIS_2/bis_cafe/standards/is_14286_2019.pdf',
    compulsoryScheme: 'Compulsory Registration Scheme (CRS)',
    summary: 'Mandatory under Ministry of New and Renewable Energy (MNRE) solar Quality Control Order.'
  },
  {
    id: 'IS-15885-2-13',
    code: 'IS 15885 (Part 2/Sec 13):2012',
    title: 'Safety of Lamp Controlgear - Particular Requirements for DC or AC Supplied Electronic Controlgear for LED Modules',
    category: 'Electronics & IT',
    department: 'Electronics and IT Department (LITD)',
    mandatory: true,
    status: 'Active',
    revisionDate: '2012-04-18',
    description: 'Specifies safety rules for LED drivers and electronic controlgear used in residential, commercial, and street lighting applications.',
    keyParameters: [
      { parameter: 'Operating Voltage Range', limit: '90V to 300V AC', unit: 'V' },
      { parameter: 'Power Factor', limit: 'Min 0.90 for >5W', unit: '-' },
      { parameter: 'Total Harmonic Distortion (THD)', limit: 'Less than 15%', unit: '%' },
      { parameter: 'Creepage & Clearance', limit: 'Min 3.0 mm', unit: 'mm' }
    ],
    officialUrl: 'https://www.services.bis.gov.in/php/BIS_2/bis_cafe/standards/is_15885.pdf',
    compulsoryScheme: 'Compulsory Registration Scheme (CRS)',
    summary: 'Mandatory CRS registration for all LED drivers sold in India.'
  }
];

export const CATEGORIES = [
  'All Categories',
  'Food & Water Safety',
  'Electrical & Electronics',
  'Civil Engineering & Building Materials',
  'Electrical & Safety Equipment',
  'Renewable Energy & Solar',
  'Electronics & IT',
  'Chemicals & Plastics',
  'Textiles & Garments',
  'Medical Devices'
];
