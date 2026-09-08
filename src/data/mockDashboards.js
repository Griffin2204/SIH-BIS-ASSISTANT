// Mock Data for Producer & Consumer Dashboards

export const PRODUCER_DASHBOARD_DATA = {
  activeApplications: [
    {
      id: 'APP-2026-8891',
      standardCode: 'IS 10500:2012',
      productName: 'Packaged Drinking Water - Line 2 Expansion',
      submissionDate: '2026-01-15',
      currentStage: 'Factory Audit Completed',
      progressPercent: 75,
      nextAction: 'Awaiting Final Test Report from NABL Lab',
      status: 'In Progress'
    },
    {
      id: 'APP-2026-4102',
      standardCode: 'IS 15885:2012',
      productName: 'LED Drivers 50W outdoor',
      submissionDate: '2026-02-01',
      currentStage: 'Document Review',
      progressPercent: 35,
      nextAction: 'Upload Factory Test Equipment Calibration Certificates',
      status: 'Action Required'
    }
  ],
  revisedStandardAlerts: [
    {
      id: 'ALT-1',
      code: 'IS 694:2010',
      title: 'Amendment 3 published for PVC Cable Insulation Fire Safety Tests',
      effectiveDate: '2026-06-01',
      urgency: 'High',
      actionRequired: 'Update Quality Assurance Plan (QAP) before June 2026 audit.'
    },
    {
      id: 'ALT-2',
      code: 'IS 13630:2019',
      title: 'New Eco-Mark criteria added for Ceramic Tile manufacturing',
      effectiveDate: '2026-09-01',
      urgency: 'Medium',
      actionRequired: 'Voluntary application for Eco-Mark endorsement.'
    }
  ],
  complianceChecklist: [
    { id: 1, title: 'In-house testing laboratory setup with calibrated instruments', completed: true },
    { id: 2, title: 'Appointment of qualified Quality Control Manager', completed: true },
    { id: 3, title: 'Scheme of Inspection and Testing (SIT) approval', completed: true },
    { id: 4, title: 'Third-party NABL test report verification', completed: false },
    { id: 5, title: 'Factory layout and machinery flowchart submission', completed: true }
  ]
};

export const CONSUMER_DASHBOARD_DATA = {
  recentVerifications: [
    {
      id: 'V-101',
      type: 'CML Licence',
      query: '7800012345',
      resultName: 'AquaPure Bottlers India Pvt Ltd',
      status: 'Authentic / Active',
      timestamp: 'Today, 02:15 PM'
    },
    {
      id: 'V-102',
      type: 'HUID Hallmark',
      query: 'AB1234',
      resultName: '22K Gold Ring - Shree Sai AHC',
      status: 'Verified Authentic',
      timestamp: 'Yesterday, 06:40 PM'
    },
    {
      id: 'V-103',
      type: 'CML Licence',
      query: '5500043210',
      resultName: 'Kajaria Ceramic Works',
      status: 'Expired Licence',
      timestamp: '04 Mar 2026'
    }
  ],
  savedProducts: [
    { id: 'S-1', title: 'Polycab Maxima 1.5 sq mm Wires', code: 'IS 694:2010', cml: '3100098765', status: 'Valid' },
    { id: 'S-2', title: 'AquaPure Mineral Water 1L', code: 'IS 10500:2012', cml: '7800012345', status: 'Valid' }
  ],
  suspiciousReports: [
    { id: 'R-901', title: 'Fake ISI mark without 10-digit CML on electrical switch', date: '2026-02-18', status: 'Under Investigation' }
  ]
};
