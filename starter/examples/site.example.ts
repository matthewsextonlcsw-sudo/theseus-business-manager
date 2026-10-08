// EXAMPLE ONLY: a fictional business used to test the starter. Never ship these facts.
// To try it: copy this file over src/data/site.ts in a scratch copy of the starter.

export const site = {
  url: 'https://northside-family-dental.example',
  name: 'Northside Family Dental',
  schemaType: 'Dentist',
  description: 'Gentle family dentistry in Floral Park, with evening hours for working parents.',
  regulated: true,
  phone: '(516) 555-0148',
  email: 'hello@northside-family-dental.example',
  address: {
    street: '1 Example Plaza',
    city: 'Floral Park',
    region: 'NY',
    postalCode: '11001',
    country: 'US'
  },
  areaServed: ['Floral Park', 'Nassau County'],
  hours: [
    { days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday'], opens: '08:00', closes: '19:00' },
    { days: ['Friday'], opens: '08:00', closes: '15:00' }
  ],
  googleProfileUrl: '',
  primaryAction: { label: 'Request an appointment', href: '/contact/' },
  formAction: '',
  afterContact: 'We call you back within one business day to find a time that works.'
} as const;

export const hero = {
  audience: 'For families in Floral Park and nearby Nassau County',
  headline: 'Checkups that fit around school and work',
  mechanism: 'Evening appointments four days a week, and a front desk that answers the phone.',
  proofPoint: ''
};

export const services: { name: string; summary: string }[] = [
  { name: 'Checkups and cleanings', summary: 'Exams, cleanings and X-rays for children and adults.' },
  { name: 'Fillings and crowns', summary: 'Repairs explained before we start, with the cost in writing.' },
  { name: 'Emergency visits', summary: 'Same-day visits for pain or a broken tooth when we have an opening.' }
];

export const faqs: [question: string, answer: string][] = [
  ['Do you see children?', 'Yes. We see patients of all ages, starting with a first visit around age one.'],
  ['Are you open in the evening?', 'Yes, until 7 pm Monday through Thursday.']
];

export const proof: { quote: string; who: string }[] = [];
