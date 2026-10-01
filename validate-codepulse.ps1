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

Write-Output 'CodePulse shared-contract validation passed.'
