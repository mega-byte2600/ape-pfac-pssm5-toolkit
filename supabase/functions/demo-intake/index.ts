import { createClient } from "npm:@supabase/supabase-js@2";

const headers = {
  "content-type": "application/json; charset=utf-8",
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "authorization, x-client-info, apikey, content-type",
};

const priorities = new Set([
  "patient-safety",
  "experience-metrics",
  "pfac-launch",
  "equity-access",
  "leadership-follow-through",
]);

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body, null, 2), { status, headers });
}

function clean(value: unknown, maxLength: number) {
  return String(value ?? "").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, maxLength);
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers });
  if (req.method !== "POST") return json({ error: "method_not_allowed" }, 405);

  let payload: Record<string, unknown>;
  try {
    payload = await req.json();
  } catch {
    return json({ error: "invalid_json" }, 400);
  }

  const role = clean(payload.role, 80);
  const organization = clean(payload.organization, 120);
  const priority = clean(payload.priority, 80);
  const message = clean(payload.message, 1200);

  const errors: string[] = [];
  if (role.length < 2) errors.push("role_required");
  if (organization.length < 2) errors.push("organization_required");
  if (!priorities.has(priority)) errors.push("priority_invalid");
  if (message.length < 10) errors.push("message_too_short");
  if (/\b(ssn|social security|medical record|mrn|date of birth|dob)\b/i.test(message)) {
    errors.push("private_patient_identifiers_not_allowed");
  }
  if (errors.length) return json({ error: "validation_failed", errors }, 422);

  const url = Deno.env.get("SUPABASE_URL");
  const secretKeys = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}");
  const secretKey = secretKeys.default ?? Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !secretKey) return json({ error: "supabase_runtime_unconfigured" }, 500);

  const client = createClient(url, secretKey, { auth: { persistSession: false } });
  const { data, error } = await client
    .from("demo_intake_notes")
    .insert({ role, organization, priority, message, source: "demo-web" })
    .select("id, created_at, priority")
    .single();

  if (error) return json({ error: "intake_unavailable", detail: error.message }, 502);

  return json({
    status: "received",
    intake: data,
    privacy_note: "Demo-only note received. Do not submit PHI or private patient identifiers.",
    next_step: "Use this note to drive PFAC discussion and leadership follow-through planning.",
  }, 201);
});
