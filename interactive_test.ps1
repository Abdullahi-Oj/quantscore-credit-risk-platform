Write-Host "=== QuantScore Predict API Tester ==="

# Collect inputs
$age = Read-Host "Age"
$gender = Read-Host "Gender (1 = Male, 0 = Female)"
$income = Read-Host "Income"
$savings = Read-Host "Savings"
$loanAmount = Read-Host "Loan Amount"
$loanTermMonths = Read-Host "Loan Term (months)"
$transactions = Read-Host "Transactions per Month"
$previousDefaults = Read-Host "Previous Defaults (0 or 1)"
$repaymentRatio = Read-Host "Repayment Ratio"
$debtToIncome = Read-Host "Debt to Income"
$installment = Read-Host "Installment per Month"
$installmentIncomeRatio = Read-Host "Installment to Income Ratio"

# Create JSON payload with the EXACT FastAPI schema
$body = @{
    age                            = [int]$age
    gender                         = [int]$gender
    income                         = [float]$income
    savings                        = [float]$savings
    loan_amount                    = [float]$loanAmount
    loan_term_months               = [int]$loanTermMonths
    transactions_per_month         = [int]$transactions
    previous_defaults              = [int]$previousDefaults
    repayment_ratio                = [float]$repaymentRatio
    debt_to_income                 = [float]$debtToIncome
    installment_per_month          = [float]$installment
    installment_to_income          = [float]$installmentIncomeRatio
} | ConvertTo-Json

Write-Host "`n=== Sending request to API ==="
Write-Host $body

try {
    $response = Invoke-RestMethod `
        -Uri "http://127.0.0.1:8000/predict" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body

    Write-Host "`n=== Prediction Response ==="
    $response | ConvertTo-Json -Depth 4
}
catch {
    Write-Host "`n❌ ERROR:"
    Write-Host $_.Exception.Message
    Write-Host "`nRaw Error Response:"
    try { $_.ErrorDetails.Message }
    catch { "No error details returned." }
}
