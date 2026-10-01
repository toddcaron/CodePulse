$ErrorActionPreference = 'Stop'

$sharedFiles = @(
    'codepulse-shared/references/runtime-contract.md',
    'codepulse-shared/references/token-efficiency.md',
    'codepulse-shared/references/grading.md',
    'codepulse-shared/references/severity.md',
    'codepulse-shared/references/recommendation-priority.md',
    'codepulse-shared/references/recommendations-library.md',
    'codepulse-shared/references/report-standard.md',
    'codepulse-shared/references/assessment-methodology.md',
    'codepulse-shared/schemas/finding-schema.md',
    'codepulse-shared/schemas/assessment-result-schema.md',
    'codepulse-shared/templates/assessment-output-template.md',
    'codepulse-shared/templates/report-template.html',
    'codepulse-shared/templates/executive-report-template.html'
)

foreach ($file in $sharedFiles) {
    if (-not (Test-Path $file)) { throw "Missing shared file: $file" }
}

$skills = Get-ChildItem -Directory -Filter 'codepulse-*' |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }
if ($skills.Count -ne 10) { throw "Expected 10 skills, found $($skills.Count)" }

$requiredLinks = @(
    '../codepulse-shared/references/runtime-contract.md',
    '../codepulse-shared/references/token-efficiency.md',
    '../codepulse-shared/references/report-standard.md',
    '../codepulse-shared/references/assessment-methodology.md',
    '../codepulse-shared/references/recommendations-library.md',
    '../codepulse-shared/schemas/finding-schema.md',
    '../codepulse-shared/schemas/assessment-result-schema.md'
)
foreach ($skill in $skills) {
    $text = Get-Content (Join-Path $skill.FullName 'SKILL.md') -Raw
    foreach ($link in $requiredLinks) {
        if ($text.IndexOf(('`' + $link + '`')) -lt 0) {
            throw "$($skill.Name) is missing shared link: $link"
        }
    }
    if (Test-Path (Join-Path $skill.FullName 'references/report-template.html')) {
        throw "$($skill.Name) contains a duplicate local report template"
    }
}

$full = Get-Content 'codepulse-full/SKILL.md' -Raw
foreach ($weight in @('30%','5%','25%','10%','15%')) {
    if ($full.IndexOf($weight) -lt 0) { throw "codepulse-full is missing weight: $weight" }
}
foreach ($section in @('Executive Summary','Security Assessment','MFA Assessment','Code Quality Assessment','Dead Code Assessment','Dependency & Framework Assessment','External Exposure Assessment','Codebase Metrics','Top Risks','Recommendations','Modernization Opportunities','Conclusion')) {
    if ($full.IndexOf($section) -lt 0) { throw "codepulse-full is missing report section: $section" }
}

$findingSchema = Get-Content 'codepulse-shared/schemas/finding-schema.md' -Raw
foreach ($field in @('`id`','`category`','`severity`','`title`','`evidence`','`impact`','`recommendation`')) {
    if ($findingSchema.IndexOf($field) -lt 0) { throw "Finding schema is missing field: $field" }
}

$resultSchema = Get-Content 'codepulse-shared/schemas/assessment-result-schema.md' -Raw
foreach ($field in @('assessmentName','repository','assessmentDate','score','status','findings','summary')) {
    if ($resultSchema.IndexOf($field) -lt 0) { throw "Assessment-result schema is missing field: $field" }
}

foreach ($field in @('`verificationStatus`','`sourceRepresentation`','`evidenceRecoveryRequired`','`evidenceLimitations`')) {
    if ($findingSchema.IndexOf($field) -lt 0) { throw "Finding schema is missing provenance field: $field" }
}
foreach ($field in @('verified-original','verified-tool-output','partially-verified','unverified','unavailable','original','normalized','compressed','summarized')) {
    if ($findingSchema.IndexOf($field) -lt 0) { throw "Finding schema is missing provenance value: $field" }
}
if ($resultSchema.IndexOf('`skipReason`') -lt 0) { throw 'Assessment-result schema does not document skipReason' }

$runtime = Get-Content 'codepulse-shared/references/runtime-contract.md' -Raw
foreach ($requirement in @('## Runtime Precedence','## External Context Optimization Runtime','### Mandatory Original Review','### Negative Finding Standard','### Compression Boundaries','### Secrets and Recovery','High or Critical','not detected in the reviewed scope')) {
    if ($runtime.IndexOf($requirement) -lt 0) { throw "Runtime contract is missing requirement: $requirement" }
}

$tokenEfficiency = Get-Content 'codepulse-shared/references/token-efficiency.md' -Raw
if ($tokenEfficiency.IndexOf('## External Proxy Coordination') -lt 0) { throw 'Token-efficiency reference is missing external proxy coordination' }

foreach ($required in @('verificationStatus','sourceRepresentation','evidenceRecoveryRequired','evidenceLimitations','findingId')) {
    if ((Get-Content 'codepulse-shared/templates/assessment-output-template.md' -Raw).IndexOf($required) -lt 0) {
        throw "Assessment-output template is missing provenance field: $required"
    }
}

foreach ($requirement in @('normalized assessment result','evidence references','original evidence','only after evidence and finding validation','intentionally skipped','compressed summary')) {
    if ($full.IndexOf($requirement, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw "codepulse-full is missing orchestration requirement: $requirement"
    }
}

$setupDoc = Get-Content 'docs/caveman-runtime-setup.md' -Raw
foreach ($requirement in @('npx -y github:JuliusBrussee/caveman -- --only copilot --with-init','npm install -g @caveman-ai/cli','caveman setup --install','Caveman Proxy','Apache-2.0','Installation Validation Checklist','Secrets remain redacted','optional')) {
    if ($setupDoc.IndexOf($requirement, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw "Caveman setup documentation is missing: $requirement"
    }
}

$generatedInstructions = @(
    '.github/copilot-instructions.md',
    'AGENTS.md',
    '.cursor/rules/caveman.mdc',
    '.windsurf/rules/caveman.md',
    '.clinerules/caveman.md',
    '.opencode/AGENTS.md'
)
foreach ($file in $generatedInstructions) {
    if (-not (Test-Path $file)) { continue }
    $text = Get-Content $file -Raw
    if ($text.IndexOf('CodePulse assessments', [System.StringComparison]::OrdinalIgnoreCase) -lt 0 -or
        $text.IndexOf('runtime-contract.md', [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw "Generated Caveman instructions do not defer to the CodePulse runtime contract: $file"
    }
}

$benchmarkDoc = Get-Content 'docs/caveman-benchmark-plan.md' -Raw
foreach ($mode in @('CodePulse only','Repo instructions','Proxy','Both')) {
    if ($benchmarkDoc.IndexOf($mode, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw "Caveman benchmark plan is missing comparison mode: $mode"
    }
}
foreach ($metric in @('Duration','input tokens','output tokens','Findings produced','verified against originals','Report completeness','Assessment failures')) {
    if ($benchmarkDoc.IndexOf($metric, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw "Caveman benchmark plan is missing capture field: $metric"
    }
}

Write-Output 'CodePulse shared-contract validation passed.'
