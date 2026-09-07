create table if not exists public.demo_intake_notes (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  role text not null,
  organization text not null,
  priority text not null,
  message text not null,
  source text not null default 'demo-web',
  constraint demo_intake_role_length check (char_length(role) between 2 and 80),
  constraint demo_intake_organization_length check (char_length(organization) between 2 and 120),
  constraint demo_intake_priority_allowed check (
    priority in (
      'patient-safety',
      'experience-metrics',
      'pfac-launch',
      'equity-access',
      'leadership-follow-through'
    )
  ),
  constraint demo_intake_message_length check (char_length(message) between 10 and 1200)
);

alter table public.demo_intake_notes enable row level security;
revoke all on table public.demo_intake_notes from anon, authenticated;

comment on table public.demo_intake_notes is
  'Demo-only sanitized PFAC/PSSM 5 intake notes. Do not store PHI or private patient details.';
