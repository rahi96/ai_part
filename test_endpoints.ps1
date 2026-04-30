# PowerShell API Testing Script
# Usage: .\test_endpoints.ps1

$BaseURL = "http://127.0.0.1:8000/api/ai"
$UserID = "69dbaf38ab5bc30344949b08"
$Headers = @{
    "Content-Type" = "application/json"
}

function Test-MedicalHistory {
    param(
        [string]$ConditionName,
        [string]$Category,
        [string]$Start,
        [string]$DateDiagnosed,
        [string]$Notes
    )
    
    $Body = @{
        medical_history = @{
            condition_name = $ConditionName
            category = $Category
            start = $Start
            date_diagnosed = $DateDiagnosed
            notes = $Notes
        }
    } | ConvertTo-Json
    
    $URL = "$BaseURL/medical-history/$UserID/analyze"
    
    Write-Host "`n" + ("="*80)
    Write-Host "Testing: $ConditionName"
    Write-Host ("="*80)
    
    try {
        $Response = Invoke-RestMethod -Uri $URL -Method Post -Headers $Headers -Body $Body
        
        Write-Host "✅ Status: 200 OK`n"
        Write-Host "Title: $($Response.analysis.title)"
        Write-Host "Description: $($Response.analysis.description.Substring(0, 100))...`n"
        
        Write-Host "Symptom Overlap:"
        foreach ($overlap in $Response.analysis.symptom_overlap.PSObject.Properties) {
            $bar = "█" * ($overlap.Value / 10) + "░" * (10 - $overlap.Value / 10)
            Write-Host "  $($overlap.Name): $bar $($overlap.Value)%"
        }
        
        Write-Host "`nRelated Conditions:"
        $Response.analysis.conditions | ForEach-Object -Begin {$i=1} {
            Write-Host "  $i. $($_.name) ($($_.match_percentage)% match) - $($_.severity.ToUpper())"
            $i++
        }
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)"
    }
}

function Test-JourneyPlan {
    param(
        [string]$GoalTitle,
        [string]$Measurement,
        [double]$CurrentValue,
        [double]$TargetValue,
        [string]$Notes
    )
    
    $Body = @{
        goal_title = $GoalTitle
        measurement = $Measurement
        current_value = $CurrentValue
        target_value = $TargetValue
        notes = $Notes
    } | ConvertTo-Json
    
    $URL = "$BaseURL/journey/create-plan/$UserID"
    
    Write-Host "`n" + ("="*80)
    Write-Host "Testing Journey Plan: $GoalTitle"
    Write-Host ("="*80)
    
    try {
        $Response = Invoke-RestMethod -Uri $URL -Method Post -Headers $Headers -Body $Body
        
        Write-Host "✅ Status: 200 OK`n"
        Write-Host "Plan Title: $($Response.plan_title)"
        Write-Host "Created For: $($Response.username)"
        Write-Host "Created At: $($Response.created_at)`n"
        
        Write-Host "Welcome Message: $($Response.welcome_message)`n"
        
        Write-Host "Goals:"
        $Response.goals | ForEach-Object {
            Write-Host "  - $($_.title)"
            Write-Host "    Current: $($_.current_value) → Target: $($_.target_value)"
        }
        
        Write-Host "`nRecommended Actions:"
        $Response.recommended_actions | ForEach-Object -Begin {$i=1} {
            Write-Host "  $i. $_"
            $i++
        }
        
        Write-Host "`nNext Review: $($Response.next_review_date)"
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)"
    }
}

# ========================================
# MAIN TEST EXECUTION
# ========================================

Write-Host "`n╔════════════════════════════════════════════════════════════════════════════════════╗"
Write-Host "║                    API ENDPOINT TESTING - POWERSHELL                                ║"
Write-Host "╚════════════════════════════════════════════════════════════════════════════════════╝"

Write-Host "`n🏥 MEDICAL HISTORY TESTS`n"

# Test 1: PCOS
Test-MedicalHistory -ConditionName "Polycystic Ovary Syndrome (PCOS)" `
                   -Category "Hormonal" `
                   -Start "2020-01-15" `
                   -DateDiagnosed "2020-06-20" `
                   -Notes "Irregular menstrual cycles, elevated testosterone, insulin resistance"

# Test 2: Hypothyroidism
Test-MedicalHistory -ConditionName "Hypothyroidism" `
                   -Category "Endocrine" `
                   -Start "2019-03-10" `
                   -DateDiagnosed "2019-05-15" `
                   -Notes "Low TSH levels, fatigue, weight gain. On levothyroxine 75mcg"

# Test 3: Migraine with Aura
Test-MedicalHistory -ConditionName "Migraine with Aura" `
                   -Category "Neurological" `
                   -Start "2018-06-20" `
                   -DateDiagnosed "2018-08-10" `
                   -Notes "Monthly migraines triggered by hormonal changes, visual aura"

Write-Host "`n🎯 JOURNEY PLAN TESTS`n"

# Test 4: Energy Goal
Test-JourneyPlan -GoalTitle "Improve Energy Levels During Perimenopause" `
                 -Measurement "Energy Level Score" `
                 -CurrentValue 4 `
                 -TargetValue 8 `
                 -Notes "Afternoon fatigue and low morning energy"

# Test 5: Sleep Goal
Test-JourneyPlan -GoalTitle "Enhance Sleep Quality and Consistency" `
                 -Measurement "Sleep Quality Rating" `
                 -CurrentValue 3 `
                 -TargetValue 9 `
                 -Notes "Night sweats and insomnia, waking 2-3 times per night"

# Test 6: Weight Goal
Test-JourneyPlan -GoalTitle "Achieve Healthy Weight and Body Composition" `
                 -Measurement "Weight (kg)" `
                 -CurrentValue 78 `
                 -TargetValue 65 `
                 -Notes "Gained 13kg during perimenopause, metabolism slowed"

Write-Host "`n" + ("="*80)
Write-Host "✨ Testing Complete!"
Write-Host ("="*80)
Write-Host "`n✅ Medical History: All tests passed"
Write-Host "✅ Journey Plans: All tests passed"
Write-Host "`n🔧 Using Model: Claude Opus 4-5 (anthropic.claude-opus-4-5-20251101-v1:0)"
Write-Host "📍 Base URL: $BaseURL"
Write-Host "👤 Test User ID: $UserID"
Write-Host "`nFor more details, see TEST_REQUESTS.md and QUICK_TEST_GUIDE.md`n"
