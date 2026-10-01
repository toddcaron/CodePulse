$ErrorActionPreference = 'Stop'

$sharedFiles = @(
    'codepulse-shared/SKILL.md',
    'codepulse-shared/references/runtime-contract.md',
    'codepulse-shared/references/token-efficiency.md',
    'codepulse-shared/references/grading.md',
    'codepulse-shared/references/severity.md',
    'codepulse-shared/references/recommendation-priority.md',
    'codepulse-shared/references/recommendations-library.md',
    'codepulse-shared/references/report-standard.md',
    'codepulse-shared/references/assessment-methodology.md',
    'codepulse-shared/references/complexity-model.md',
    'codepulse-shared/schemas/finding-schema.json',
    'codepulse-shared/schemas/assessment-result-schema.json',
    'codepulse-shared/schemas/codepulse-report-schema.json',
    'codepulse-shared/renderers/html-template.md',
    'codepulse-shared/renderers/markdown-template.md',
    'codepulse-shared/renderers/executive-summary-template.md'
)

foreach ($file in $sharedFiles) {
    if (-not (Test-Path $file)) { throw "Missing shared file: $file" }
}

foreach ($legacy in @('codepulse-shared/templates','codepulse-shared/schemas/finding-schema.md','codepulse-shared/schemas/assessment-result-schema.md','codepulse-exec/references/executive-scorecard-template.html')) {
    if (Test-Path $legacy) { throw "Legacy report asset must be removed: $legacy" }
}

$allSkills = Get-ChildItem -Directory -Filter 'codepulse-*' |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }
if ($allSkills.Count -ne 10) { throw "Expected 10 total skills (9 assessment + 1 shared), found $($allSkills.Count)" }

$skills = $allSkills | Where-Object { $_.Name -ne 'codepulse-shared' }
if ($skills.Count -ne 9) { throw "Expected 9 assessment skills, found $($skills.Count)" }

$requiredLinks = @(
    '../codepulse-shared/references/runtime-contract.md',
    '../codepulse-shared/references/token-efficiency.md',
    '../codepulse-shared/references/report-standard.md',
    '../codepulse-shared/references/assessment-methodology.md',
    '../codepulse-shared/references/recommendations-library.md',
    '../codepulse-shared/schemas/finding-schema.json',
    '../codepulse-shared/schemas/assessment-result-schema.json',
    '../codepulse-shared/schemas/codepulse-report-schema.json'
)
foreach ($skill in $skills) {
    $text = Get-Content (Join-Path $skill.FullName 'SKILL.md') -Raw
    foreach ($link in $requiredLinks) {
        if ($text.IndexOf(('`' + $link + '`')) -lt 0) {
            throw "$($skill.Name) is missing shared link: $link"
        }
    }
    $renderer = if ($skill.Name -eq 'codepulse-exec') { 'executive-summary-template.md' } else { 'html-template.md' }
    if ($text.IndexOf("``../codepulse-shared/renderers/$renderer``") -lt 0) {
        throw "$($skill.Name) is missing renderer link: $renderer"
    }
    if ($text -match 'report-template\.html|executive-scorecard-template|templates/|-schema\.md') {
        throw "$($skill.Name) still references a legacy HTML template or Markdown schema"
    }
    if ($text.IndexOf('-result.json') -lt 0) {
        throw "$($skill.Name) does not persist a -result.json report object"
    }
}

$full = Get-Content 'codepulse-full/SKILL.md' -Raw
foreach ($weight in @('32%','5%','26%','11%','10%','16%')) {
    if ($full.IndexOf($weight) -lt 0) { throw "codepulse-full is missing weight: $weight" }
}
foreach ($section in @('Executive Summary','Security Assessment','Code Quality Assessment','Dead Code Assessment','Dependency & Framework Assessment','External Exposure Assessment','Codebase Metrics','Top Risks','Recommendations','Modernization Opportunities','Conclusion')) {
    if ($full.IndexOf($section) -lt 0) { throw "codepulse-full is missing report section: $section" }
}

$complexityLink = '`../codepulse-shared/references/complexity-model.md`'
foreach ($skillName in @('codepulse-quality','codepulse-full')) {
    if ((Get-Content "$skillName/SKILL.md" -Raw).IndexOf($complexityLink) -lt 0) {
        throw "$skillName is missing shared link: ../codepulse-shared/references/complexity-model.md"
    }
}
$complexityModel = Get-Content 'codepulse-shared/references/complexity-model.md' -Raw
foreach ($requirement in @('Cyclomatic Complexity','Cognitive Complexity','Accidental Complexity','Inherent vs. Accidental Test','QUAL-CYC-','QUAL-COG-','QUAL-ACC-','manual-estimate')) {
    if ($complexityModel.IndexOf($requirement) -lt 0) { throw "Complexity model is missing: $requirement" }
}

$findingSchema = Get-Content 'codepulse-shared/schemas/finding-schema.json' -Raw | ConvertFrom-Json
foreach ($field in @('id','category','title','evidence','impact','recommendation','verificationStatus','sourceRepresentation','evidenceRecoveryRequired','evidenceLimitations')) {
    if ($findingSchema.required -notcontains $field) { throw "Finding schema does not require field: $field" }
}
if (-not $findingSchema.properties.severity) { throw 'Finding schema is missing field: severity' }
$verificationValues = $findingSchema.properties.verificationStatus.enum
foreach ($value in @('verified-original','verified-tool-output','partially-verified','unverified','unavailable')) {
    if ($verificationValues -notcontains $value) { throw "Finding schema is missing provenance value: $value" }
}
$representationValues = $findingSchema.properties.sourceRepresentation.enum
foreach ($value in @('original','normalized','compressed','summarized')) {
    if ($representationValues -notcontains $value) { throw "Finding schema is missing provenance value: $value" }
}

$resultSchema = Get-Content 'codepulse-shared/schemas/assessment-result-schema.json' -Raw | ConvertFrom-Json
foreach ($field in @('schemaVersion','assessmentName','repository','assessmentDate','score','status','findings','summary')) {
    if ($resultSchema.required -notcontains $field) { throw "Assessment-result schema does not require field: $field" }
}
foreach ($value in @('complete','incomplete','failed','unavailable')) {
    if ($resultSchema.properties.status.enum -notcontains $value) { throw "Assessment-result schema is missing status: $value" }
}
if (-not $resultSchema.properties.skipReason) { throw 'Assessment-result schema does not document skipReason' }

$reportSchema = Get-Content 'codepulse-shared/schemas/codepulse-report-schema.json' -Raw | ConvertFrom-Json
foreach ($field in @('schemaVersion','reportType','skillName','application','repository','assessmentDate')) {
    if ($reportSchema.required -notcontains $field) { throw "Report schema does not require field: $field" }
}
foreach ($skill in $allSkills | Where-Object { $_.Name -ne 'codepulse-shared' -and $_.Name -ne 'codepulse-full' -and $_.Name -ne 'codepulse-exec' }) {
    if ($resultSchema.properties.assessmentName.enum -notcontains $skill.Name) { throw "Assessment-result schema is missing assessmentName: $($skill.Name)" }
}
foreach ($skill in $skills) {
    if ($reportSchema.properties.skillName.enum -notcontains $skill.Name) { throw "Report schema is missing skillName: $($skill.Name)" }
}
$dashboard = $reportSchema.'$defs'.executive.properties.dashboard
foreach ($field in @('overallGrade','securityPosture','technologyHealth','maintainability','operationalRisk','modernizationReadiness')) {
    if ($dashboard.required -notcontains $field) { throw "Executive dashboard does not require: $field" }
}

$htmlRenderer = Get-Content 'codepulse-shared/renderers/html-template.md' -Raw
foreach ($requirement in @('codepulse-report-schema.json','HTML-escape','```css','Executive Summary','Assessment Dashboard','Overall Grade','Assessment Methodology','Security Assessment','Code Quality Assessment','Dead Code Assessment','Dependency & Framework Assessment','External Exposure Assessment','Codebase Metrics','Top Risks','Recommendations','Modernization Opportunities','Conclusion','Complexity breakdown','verificationStatus')) {
    if ($htmlRenderer.IndexOf($requirement) -lt 0) { throw "HTML renderer is missing: $requirement" }
}
$execRenderer = Get-Content 'codepulse-shared/renderers/executive-summary-template.md' -Raw
foreach ($requirement in @('Executive Dashboard','Application Snapshot','Top Risks','Strengths','Investment Priorities','Modernization Outlook','Executive Recommendation')) {
    if ($execRenderer.IndexOf($requirement) -lt 0) { throw "Executive renderer is missing section: $requirement" }
}
if ((Get-Content 'codepulse-shared/renderers/markdown-template.md' -Raw).IndexOf('explicitly asks for Markdown') -lt 0) {
    throw 'Markdown renderer must be opt-in'
}

$runtime = Get-Content 'codepulse-shared/references/runtime-contract.md' -Raw
foreach ($requirement in @('## Runtime Precedence','## External Context Optimization Runtime','### Mandatory Original Review','### Negative Finding Standard','### Compression Boundaries','### Secrets and Recovery','High or Critical','not detected in the reviewed scope')) {
    if ($runtime.IndexOf($requirement) -lt 0) { throw "Runtime contract is missing requirement: $requirement" }
}

$tokenEfficiency = Get-Content 'codepulse-shared/references/token-efficiency.md' -Raw
if ($tokenEfficiency.IndexOf('## External Proxy Coordination') -lt 0) { throw 'Token-efficiency reference is missing external proxy coordination' }

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
