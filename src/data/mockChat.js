// Mock Database for RAG Chat & Recommendations

export const MOCK_SUGGESTED_QUESTIONS = [
  'What are the permissible limits for lead and TDS in drinking water under IS 10500:2012?',
  'Is ISI mark mandatory for PVC electrical wires used in building construction?',
  'How do I verify the 6-digit HUID code on gold jewelry?',
  'What documents are required to apply for a BIS licence under Scheme-I?',
  'What is the difference between ISI Mark (Scheme-I) and CRS Registration?'
];

export const MOCK_CHAT_RESPONSES = [
  {
    keywords: ['drinking water', 'is 10500', 'water', 'tds', 'lead', 'ph'],
    answer: 'According to **IS 10500:2012** (Drinking Water Specification - Second Revision), the mandatory chemical & physical limits for drinking water in India are:\n\n' +
      '• **pH Value**: 6.5 to 8.5\n' +
      '• **Total Dissolved Solids (TDS)**: Maximum 500 mg/l (acceptable), up to 2000 mg/l in absence of alternate source.\n' +
      '• **Turbidity**: Max 1 NTU (acceptable limit), up to 5 NTU permissible.\n' +
      '• **Lead (as Pb)**: Maximum permissible limit is **0.01 mg/l**.\n' +
      '• **Bacteriological**: *E. Coli* or thermotolerant coliform bacteria must NOT be detectable in any 100 ml sample.\n\n' +
      'All commercial packaged drinking water units in India must hold a mandatory BIS CML licence displaying the ISI mark.',
    confidenceScore: 0.98,
    confidenceLabel: 'High Trust (98%)',
    citations: [
      {
        standardCode: 'IS 10500:2012',
        title: 'Drinking Water Specification',
        section: 'Table 1 & Table 2, Page 2-4',
        url: 'https://www.services.bis.gov.in/php/BIS_2/bis_cafe/standards/is_10500_2012.pdf'
      }
    ]
  },
  {
    keywords: ['wire', 'cable', 'is 694', 'pvc', 'electrical', 'building'],
    answer: 'Yes, under the Electrical Wires and Cables (Quality Control) Order, **ISI mark certification under IS 694:2010** is strictly **mandatory** for all PVC insulated electrical cables up to 1100V sold, manufactured, or imported in India.\n\n' +
      'Key testing requirements under IS 694:\n' +
      '• Conductor resistance test at 20°C\n' +
      '• Insulation resistance at maximum operating temperature (70°C)\n' +
      '• High voltage spark test\n' +
      '• Flammability & smoke density test\n\n' +
      'Selling uncertified PVC electrical wires is a punishable offense under Section 17 of the BIS Act, 2016.',
    confidenceScore: 0.95,
    confidenceLabel: 'High Trust (95%)',
    citations: [
      {
        standardCode: 'IS 694:2010',
        title: 'PVC Insulated Cables for Working Voltages up to 1100 V',
        section: 'Section 4 (Quality Control Order 2012)',
        url: 'https://www.services.bis.gov.in/php/BIS_2/bis_cafe/standards/is_694_2010.pdf'
      }
    ]
  },
  {
    keywords: ['huid', 'gold', 'hallmark', 'jewelry', 'jewellery'],
    answer: 'A **Hallmark Unique Identification (HUID)** is a 6-digit alphanumeric code (e.g. `AB1234`) laser etched on every hallmarked gold jewelry article alongside the BIS logo and purity mark (e.g., 22K916).\n\n' +
      'How to verify your HUID:\n' +
      '1. Open the **VERIFY** tab on this portal or download the official **BIS CARE App**.\n' +
      '2. Enter the 6-digit HUID code etched on your gold item.\n' +
      '3. View details including Jeweller Name, Registration No., Hallmarking Center (AHC) details, Article Type, Weight, and Purity.',
    confidenceScore: 0.99,
    confidenceLabel: 'High Trust (99%)',
    citations: [
      {
        standardCode: 'IS 1417:2019',
        title: 'Gold and Gold Alloys, Jewellery/Artefacts — Fineness and Marking',
        section: 'BIS Hallmarking Scheme Guidelines 2021',
        url: 'https://www.bis.gov.in/hallmarking-2/huid/'
      }
    ]
  }
];

export const DEFAULT_BOT_RESPONSE = {
  answer: 'Thank you for your technical query. Based on the Bureau of Indian Standards (BIS) repository:\n\n' +
    '• Indian Standards (IS codes) provide technical specifications, sampling guidelines, and quality standards.\n' +
    '• Manufacturers can apply for ISI Mark (Scheme-I) or Compulsory Registration Scheme (CRS) via the Manakonline portal.\n' +
    '• Consumers can verify CML licences and 6-digit HUID gold hallmarking numbers in real time.\n\n' +
    'Please search for specific IS codes (e.g. *IS 10500*, *IS 694*, *IS 13630*) or ask a detailed query for precise official citations.',
  confidenceScore: 0.82,
  confidenceLabel: 'Moderate Trust (82%)',
  citations: [
    {
      standardCode: 'BIS Act 2016',
      title: 'Bureau of Indian Standards Rules & Regulations',
      section: 'Section 14 & 16',
      url: 'https://www.bis.gov.in/'
    }
  ]
};
