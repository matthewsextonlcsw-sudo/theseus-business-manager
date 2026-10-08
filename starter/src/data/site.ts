// Every business fact the site shows lives here, once. Fill in every [insert ...] value from the
// approved brief and the client's own records. The QA script fails while any placeholder remains.
// Facts must match the Google Business Profile exactly: name, address, phone, hours.

export const site = {
  url: 'https://example.com',
  name: '[insert business name]',
  // schema.org type for structured data, e.g. LocalBusiness, Dentist, MedicalBusiness, ProfessionalService
  schemaType: 'LocalBusiness',
  description: '[insert one-sentence description: who it is for and the outcome]',
  // Licensed clinical practice (therapy, medical, dental)? Turns on the crisis notice and the
  // no-health-details note on the contact form, and keeps testimonials off the page.
  regulated: false,
  phone: '[insert phone, as shown on the Google profile]',
  email: '[insert email]',
  address: {
    street: '[insert street]',
    city: '[insert city]',
    region: '[insert state]',
    postalCode: '[insert ZIP]',
    country: 'US'
  },
  areaServed: ['[insert town or county]'],
  hours: [
    // One line per day group, exactly as on the Google profile.
    { days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], opens: '09:00', closes: '17:00' }
  ],
  googleProfileUrl: '',
  primaryAction: {
    label: '[insert action, e.g. Book a 20-minute consultation]',
    href: '/contact/'
  },
  // Where the contact form posts. Leave empty to show a call and email path instead of a form.
  formAction: '',
  // What happens after someone reaches out, stated plainly and kept true.
  afterContact: '[insert what happens next and how fast, e.g. We reply within one business day.]'
} as const;

export const hero = {
  audience: '[insert who it is for]',
  headline: '[insert the outcome, in the buyer\'s words]',
  mechanism: '[insert how it works, in one line]',
  proofPoint: '' // one real, specific proof point, or empty
};

export const services: { name: string; summary: string }[] = [
  { name: '[insert service]', summary: '[insert what the customer gets]' }
];

// Real questions customers ask, with true answers. Empty is better than invented.
export const faqs: [question: string, answer: string][] = [];

// Real outcomes with permission to publish. Leave empty for regulated clinical practices.
export const proof: { quote: string; who: string }[] = [];
