#requires -Version 5.1
<#
.SYNOPSIS
  Codex-free 2013/2014 38-question PDF split and 181-parent ledger check.
.DESCRIPTION
  Run inside the existing review branch. No deployment and no AI credits.
  Safe by default: generates data, validates, and does NOT commit/push.
.EXAMPLE
  .\scripts\nomusa_split_38_181.ps1
.EXAMPLE
  .\scripts\nomusa_split_38_181.ps1 -CheckOnly
.EXAMPLE
  .\scripts\nomusa_split_38_181.ps1 -CommitAndPush
#>
[CmdletBinding()]
param(
    [switch] $CheckOnly,
    [switch] $CommitAndPush
)
$ErrorActionPreference = 'Stop'
$branch = 'review/nomusa-auto-v1-20year-gate-20261115'
$expectedRepo = 'nurioni4188/gongin-nomusa-quiz'
$root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

function Assert-Exit([string] $Label) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Label FAILED with exit code $LASTEXITCODE"
    }
}

Push-Location $root
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'Git CLI is required.'
    }
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        throw 'Node.js CLI is required.'
    }

    $python = (Get-Command python -ErrorAction SilentlyContinue)
    if (-not $python) {
        throw 'Python CLI is required. Check python --version.'
    }

    $activeBranch = (git branch --show-current).Trim()
    Assert-Exit 'Git current branch'
    if ($activeBranch -ne $branch) {
        throw "SAFETY HOLD: on '$activeBranch', expected '$branch'. No changes applied."
    }

    $origin = (git remote get-url origin).Trim()
    Assert-Exit 'Git remote'
    if ($origin -notmatch 'nurioni4188[\/:]gongin-nomusa-quiz(?:\.git)?$') {
        throw "SAFETY HOLD: unexpected remote '$origin'."
    }
    Write-Host ('PASS: Review branch ' + $activeBranch)
    Write-Host ('PASS: Existing project ' + $expectedRepo)

    python -c 'import pymupdf'
    if ($LASTEXITCODE -ne 0) {
        if ($CheckOnly) {
            throw 'PyMuPDF is not installed; use normal mode first.'
        }
        Write-Host 'Installing PyMuPDF only (no AI/Codex required)...'
        python -m pip install --user pymupdf
        Assert-Exit 'PyMuPDF installation'
    }

    $script = Join-Path $root 'scripts\nomusa_split_38_181.py'
    $args = @($script, '--repo', $root)
    if ($CheckOnly) { $args += '--check' }

    & python @args
    Assert-Exit '38-question + 181-parent ledger'
    node --check 'second/historical-2013-2014-38.js'
    Assert-Exit 'Generated JS syntax'

    @'
const fs=require('fs'),vm=require('vm');
const ctx=vm.createContext({window:{}});
for(const path of [
'rc27_essay_catalog.js',
'second/archive_2013_2021.js',
'second/legacy_2007_2012_source_only.js',
'second/historical-2013-2014-38.js'
]) vm.runInContext(fs.readFileSync(path,'utf8'),ctx,{filename:path});
const original=ctx.window.N27_CATALOG.items;
const parts=ctx.window.NOMUSA_2013_2014_SPLIT_V1.items;
const ledger=JSON.parse(fs.readFileSync(
 'review/NOMUSA_SECOND_2013_2014_38_AND_181_LEDGER_20261115.json','utf8'));
const unique=new Set(original.map(x=>x.id));
if(original.length!==309 || unique.size!==309) throw Error('309 source identity FAILED');
if(parts.length!==38 || parts.some(x=>unique.has(x.id))) throw Error('Child ID collision');
if(ledger.legacyLedger181.length!==181) throw Error('181 parent reconciliation FAILED');
if(parts.some(x=>!x.sourceText || x.scoringApproved!==false)) throw Error('Source or scoring gate FAILED');
console.log('PASS: 309 preserved + 38 new child items; 181 original ledger intact.');
console.log('PASS: no approval of generated answer / no RC35 scoring changes.');
'@ | node
    Assert-Exit 'Full local source linking test'

    $generated = @(
      'second/historical-2013-2014-38.js',
      'review/NOMUSA_SECOND_2013_2014_38_AND_181_LEDGER_20261115.json'
    )
    if ($CommitAndPush) {
        if ($CheckOnly) { throw 'Do not combine -CommitAndPush with -CheckOnly.' }
        git add -- $generated
        Assert-Exit 'Stage generated artifacts'
        git diff --cached --check
        Assert-Exit 'Staged diff'
        git diff --cached --quiet
        if ($LASTEXITCODE -eq 1) {
            git commit -m 'data(essay): regenerate checked 38-question and 181-ledger outputs'
            Assert-Exit 'Commit review-only artifacts'
            git push origin "HEAD:refs/heads/$branch"
            Assert-Exit 'Push existing review branch'
            Write-Host 'PASS: Changes saved to existing review branch only.'
        }
        elseif ($LASTEXITCODE -eq 0) {
            Write-Host 'PASS: No new changes; previous version already committed.'
        }
        else { throw 'Git staged diff failed.' }
    }
    else {
        Write-Host 'PASS: Local split/ledger validation finished; no push/deploy.'
    }
    git status --short
}
finally {
    Pop-Location
}
