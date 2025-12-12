export type Patient = {
  id: string;
  name: string;
  dob: string;
  gender: 'Male' | 'Female' | 'Other';
  contact: string;
  email: string;
  address: string;
  medicalHistory: {
    allergies: string[];
    conditions: string[];
    medications: Medication[];
  };
  avatarUrl: string;
};

export type Doctor = {
    id: string;
    name: string;
    specialty: string;
    avatarUrl: string;
}

export type Appointment = {
  id: string;
  patientId: string;
  doctorId: string;
  date: string;
  time: string;
  reason: string;
  status: 'Scheduled' | 'Completed' | 'Cancelled';
};

export type Medication = {
    id: string;
    name: string;
    dosage: string;
    frequency: string;
    prescribed: string; // date
};

export type Invoice = {
    id: string;
    patientId: string;
    date: string;
    amount: number;
    status: 'Paid' | 'Pending' | 'Overdue';
    items: {
        description: string;
        amount: number;
    }[];
};

export const doctors: Doctor[] = [
    { id: 'doc-1', name: 'Dr. Alan Grant', specialty: 'Cardiology', avatarUrl: 'https://picsum.photos/seed/doctor1/100/100' },
    { id: 'doc-2', name: 'Dr. Ellie Sattler', specialty: 'Pediatrics', avatarUrl: 'https://picsum.photos/seed/doctor2/100/100' },
    { id: 'doc-3', name: 'Dr. Ian Malcolm', specialty: 'Neurology', avatarUrl: 'https://picsum.photos/seed/doctor3/100/100' },
];

export const patients: Patient[] = [
  {
    id: 'pat-1',
    name: 'Sarah Johnson',
    dob: '1985-05-15',
    gender: 'Female',
    contact: '+1-202-555-0181',
    email: 'sarah.j@example.com',
    address: '123 Maple St, Springfield',
    medicalHistory: {
      allergies: ['Penicillin', 'Peanuts'],
      conditions: ['Hypertension'],
      medications: [
        { id: 'med-1', name: 'Lisinopril', dosage: '10mg', frequency: 'Once a day', prescribed: '2022-01-20' }
      ]
    },
    avatarUrl: 'https://picsum.photos/seed/patient1/100/100',
  },
  {
    id: 'pat-2',
    name: 'Michael Smith',
    dob: '1992-08-22',
    gender: 'Male',
    contact: '+1-202-555-0192',
    email: 'michael.s@example.com',
    address: '456 Oak Ave, Springfield',
    medicalHistory: {
      allergies: ['None'],
      conditions: ['Asthma'],
      medications: [
        { id: 'med-2', name: 'Albuterol Inhaler', dosage: '2 puffs', frequency: 'As needed', prescribed: '2020-03-10' }
      ]
    },
    avatarUrl: 'https://picsum.photos/seed/patient2/100/100',
  },
  {
    id: 'pat-3',
    name: 'Emily Davis',
    dob: '1978-11-30',
    gender: 'Female',
    contact: '+1-202-555-0145',
    email: 'emily.d@example.com',
    address: '789 Pine Ln, Springfield',
    medicalHistory: {
      allergies: ['Sulfa drugs'],
      conditions: ['Diabetes Type 2'],
      medications: [
        { id: 'med-3', name: 'Metformin', dosage: '500mg', frequency: 'Twice a day', prescribed: '2019-06-01' },
        { id: 'med-4', name: 'Atorvastatin', dosage: '20mg', frequency: 'Once a day', prescribed: '2021-09-15' }
      ]
    },
    avatarUrl: 'https://picsum.photos/seed/patient3/100/100',
  },
];

export const appointments: Appointment[] = [
  { id: 'app-1', patientId: 'pat-1', doctorId: 'doc-1', date: new Date().toISOString().split('T')[0], time: '10:00 AM', reason: 'Annual Checkup', status: 'Scheduled' },
  { id: 'app-2', patientId: 'pat-2', doctorId: 'doc-2', date: new Date().toISOString().split('T')[0], time: '11:30 AM', reason: 'Asthma follow-up', status: 'Scheduled' },
  { id: 'app-3', patientId: 'pat-3', doctorId: 'doc-1', date: new Date(new Date().setDate(new Date().getDate() + 1)).toISOString().split('T')[0], time: '02:00 PM', reason: 'Diabetes management', status: 'Scheduled' },
  { id: 'app-4', patientId: 'pat-1', doctorId: 'doc-3', date: new Date(new Date().setDate(new Date().getDate() - 7)).toISOString().split('T')[0], time: '09:00 AM', reason: 'Headaches', status: 'Completed' },
];

export const invoices: Invoice[] = [
    { id: 'inv-001', patientId: 'pat-1', date: '2024-05-01', amount: 150.00, status: 'Paid', items: [{ description: 'Consultation', amount: 150.00 }] },
    { id: 'inv-002', patientId: 'pat-2', date: '2024-05-03', amount: 75.00, status: 'Pending', items: [{ description: 'Follow-up Visit', amount: 75.00 }] },
    { id: 'inv-003', patientId: 'pat-3', date: '2024-04-15', amount: 250.00, status: 'Overdue', items: [{ description: 'Lab Tests', amount: 150.00 }, { description: 'Consultation', amount: 100.00 }] },
];
