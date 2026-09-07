import { createClient } from "npm:@supabase/supabase-js@2";

const headers = {
  "content-type": "application/json; charset=utf-8",
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, OPTIONS",
  "access-control-allow-headers": "authorization, x-client-info, apikey, content-type",
};

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body, null, 2), { status, headers });
}

async function readTable(client: ReturnType<typeof createClient>, table: string) {
  const { data, error } = await client.from(table).select("*").order("sort_order", { ascending: true });
  if (error) throw new Error(`${table}: ${error.message}`);
  return data ?? [];
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers });
  if (req.method !== "GET") return json({ error: "method_not_allowed" }, 405);

  const url = Deno.env.get("SUPABASE_URL");
  const secretKeys = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}");
  const secretKey = secretKeys.default ?? Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !secretKey) return json({ error: "supabase_runtime_unconfigured" }, 500);

  const client = createClient(url, secretKey, { auth: { persistSession: false } });

  try {
    const [competencies, metrics, steps, evidence, resources] = await Promise.all([
      readTable(client, "toolkit_competencies"),
      readTable(client, "toolkit_metric_drivers"),
      readTable(client, "toolkit_playbook_steps"),
      readTable(client, "toolkit_evidence_sources"),
      readTable(client, "toolkit_open_resources"),
    ]);

    return json({
      status: "ok",
      backend: "supabase-edge-postgres",
      project: "ape-pfac-pssm5-toolkit",
      generated_at: new Date().toISOString(),
      counts: {
        competencies: competencies.length,
        metric_drivers: metrics.length,
        playbook_steps: steps.length,
        evidence_sources: evidence.length,
        open_resources: resources.length,
      },
      competencies: competencies.map((row: any) => ({
        id: row.competency_id,
        label: row.label,
        agreement_text: row.agreement_text,
        proof: row.patient_first_proof,
        artifact: row.toolkit_artifact,
      })),
      metric_drivers: metrics.map((row: any) => ({
        metric: row.metric_family,
        patient_question: row.patient_first_question,
        improvement_signal: row.improvement_signal,
        pfac_use: row.pfac_co_design_use,
      })),
      playbook_steps: steps.map((row: any) => ({
        title: row.title,
        leader_action: row.leader_action,
        patient_benefit: row.patient_benefit,
        guardrail: row.patient_harm_guardrail,
        artifact: row.artifact_output,
      })),
      evidence: evidence.map((row: any) => ({
        source: row.source_id,
        claim: row.evidence_claim,
        patient_benefit: row.patient_benefit,
        risk_if_ignored: row.patient_risk_if_ignored,
        leadership_use: row.leadership_use,
        ama11_reference: row.ama11_reference,
        evidence_type: row.evidence_type,
      })),
      open_resources: resources.map((row: any) => ({
        name: row.name,
        type: row.resource_type,
        url: row.url,
        description: row.description,
        research_use: row.research_use,
      })),
    });
  } catch (error) {
    return json({ error: "toolkit_data_unavailable", detail: String(error?.message ?? error) }, 502);
  }
});
