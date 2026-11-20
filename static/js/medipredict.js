/**
 * MediPredict AI — Front-End Application Utilities
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5500);
    });

    // 2. BMI Live Calculator on Tracker Form
    const weightInput = document.getElementById('id_weight_kg');
    const heightInput = document.getElementById('id_height_cm');
    const bmiDisplay = document.getElementById('live_bmi_display');

    function updateLiveBMI() {
        if (!weightInput || !heightInput || !bmiDisplay) return;
        const w = parseFloat(weightInput.value);
        const h = parseFloat(heightInput.value);
        if (w > 0 && h > 0) {
            const hm = h / 100.0;
            const bmi = (w / (hm * hm)).toFixed(1);
            let category = 'Normal';
            let badgeClass = 'bg-success';
            if (bmi < 18.5) { category = 'Underweight'; badgeClass = 'bg-info text-dark'; }
            else if (bmi >= 25 && bmi < 30) { category = 'Overweight'; badgeClass = 'bg-warning text-dark'; }
            else if (bmi >= 30) { category = 'Obese'; badgeClass = 'bg-danger'; }

            bmiDisplay.innerHTML = `<span class="badge ${badgeClass} fs-6 py-2 px-3">Calculated BMI: <b>${bmi} kg/m²</b> (${category})</span>`;
        } else {
            bmiDisplay.innerHTML = `<span class="text-muted small">Enter height and weight to calculate BMI automatically</span>`;
        }
    }

    if (weightInput && heightInput) {
        weightInput.addEventListener('input', updateLiveBMI);
        heightInput.addEventListener('input', updateLiveBMI);
        updateLiveBMI();
    }
});

// Dynamic Row Functions for Medical Report Confirmation Table
function addLabRow() {
    const tbody = document.getElementById('labTableBody');
    if (!tbody) return;

    const rowCount = tbody.rows.length;
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" name="test_name[]" class="form-control form-control-sm" placeholder="e.g. Serum Sodium" required></td>
        <td><input type="number" step="any" name="measured_value[]" class="form-control form-control-sm" placeholder="Value" required></td>
        <td><input type="text" name="unit[]" class="form-control form-control-sm" placeholder="Unit e.g. mg/dL"></td>
        <td><input type="number" step="any" name="ref_min[]" class="form-control form-control-sm" placeholder="Min"></td>
        <td><input type="number" step="any" name="ref_max[]" class="form-control form-control-sm" placeholder="Max"></td>
        <td class="text-center">
            <button type="button" class="btn btn-outline-danger btn-sm" onclick="removeLabRow(this)">
                <i class="fa-solid fa-trash"></i>
            </button>
        </td>
    `;
    tbody.appendChild(tr);
}

function removeLabRow(btn) {
    const tr = btn.closest('tr');
    if (tr) tr.remove();
}
