// Mock Database for Producer CML Licences, HUID Hallmarking, and AHC Centers

export const MOCK_LICENCES = {
  '7800012345': {
    cmlNumber: '7800012345',
    status: 'Verified',
    statusBadge: 'Active Licence',
    producerName: 'AquaPure Bottlers India Pvt Ltd',
    brandName: 'AquaPure Mineral',
    isStandard: 'IS 10500:2012',
    standardTitle: 'Drinking Water Specification',
    category: 'Packaged Drinking Water',
    factoryAddress: 'Plot No. 42, Industrial Area Phase II, MIDC Chakan, Pune, Maharashtra - 410501',
    validFrom: '2021-04-01',
    validTo: '2026-03-31',
    grantDate: '2016-04-01',
    holdingBranch: 'Pune Branch Office (PBO)',
    testReportNo: 'TR/PBO/2024/0987',
    officialRegistryUrl: 'https://manakonline.in/MANAK/licenceVerification?cml=7800012345'
  },
  '3100098765': {
    cmlNumber: '3100098765',
    status: 'Verified',
    statusBadge: 'Active Licence',
    producerName: 'Polycab Cables & Wires Ltd',
    brandName: 'Polycab Maxima',
    isStandard: 'IS 694:2010',
    standardTitle: 'PVC Insulated Cables up to 1100V',
    category: 'Building Wires & Power Cables',
    factoryAddress: 'Survey No. 74/1, Halol Industrial Estate, Panchmahal, Gujarat - 389350',
    validFrom: '2018-09-15',
    validTo: '2027-09-14',
    grantDate: '2012-09-15',
    holdingBranch: 'Vadodara Branch Office (VBO)',
    testReportNo: 'TR/VBO/2024/4412',
    officialRegistryUrl: 'https://manakonline.in/MANAK/licenceVerification?cml=3100098765'
  },
  '5500043210': {
    cmlNumber: '5500043210',
    status: 'Expired',
    statusBadge: 'Licence Expired',
    producerName: 'Kajaria Ceramic Works Ltd',
    brandName: 'Kajaria Duragres',
    isStandard: 'IS 13630:2019',
    standardTitle: 'Ceramic Tiles Specification',
    category: 'Glazed Vitrified Tiles',
    factoryAddress: 'Gala No. 12, Sikandrabad Industrial Zone, Bulandshahr, UP - 203205',
    validFrom: '2019-01-01',
    validTo: '2023-12-31',
    grantDate: '2014-01-01',
    holdingBranch: 'Noida Branch Office (NBO)',
    testReportNo: 'TR/NBO/2022/8821',
    officialRegistryUrl: 'https://manakonline.in/MANAK/licenceVerification?cml=5500043210'
  }
};

export const MOCK_HUID_RECORDS = {
  'AB1234': {
    huid: 'AB1234',
    status: 'Authentic',
    articleType: 'Gold Ring 22K',
    purity: '22K916 (91.6% Pure Gold)',
    weightGram: '8.450 g',
    hallmarkedDate: '2025-11-12',
    ahcName: 'Shree Sai Assaying & Hallmarking Centre',
    ahcRegNo: 'AHC/MH/PUNE/042',
    jewellerName: 'PN Gadgil & Sons Jewellers',
    jewellerLicence: 'HM/C-67890123'
  },
  'XY9876': {
    huid: 'XY9876',
    status: 'Authentic',
    articleType: 'Gold Chain 18K',
    purity: '18K750 (75.0% Pure Gold)',
    weightGram: '14.200 g',
    hallmarkedDate: '2026-01-20',
    ahcName: 'Zaveri Bazaar Hallmarking Pvt Ltd',
    ahcRegNo: 'AHC/MH/MUM/008',
    jewellerName: 'Malabar Gold & Diamonds',
    jewellerLicence: 'HM/C-11223344'
  }
};

export const MOCK_AHC_CENTERS = [
  { id: 1, name: 'Shree Sai Assaying & Hallmarking Centre', city: 'Pune', state: 'Maharashtra', regNo: 'AHC/MH/PUNE/042', phone: '+91 20 2567 8901', status: 'Recognized' },
  { id: 2, name: 'Zaveri Bazaar Hallmarking Pvt Ltd', city: 'Mumbai', state: 'Maharashtra', regNo: 'AHC/MH/MUM/008', phone: '+91 22 6633 4455', status: 'Recognized' },
  { id: 3, name: 'Apex Precious Metals Refinery & AHC', city: 'Bengaluru', state: 'Karnataka', regNo: 'AHC/KA/BLR/019', phone: '+91 80 4123 9988', status: 'Recognized' },
  { id: 4, name: 'Northern India Gold Refinery & AHC', city: 'New Delhi', state: 'Delhi', regNo: 'AHC/DL/DEL/005', phone: '+91 11 2345 6789', status: 'Recognized' }
];
