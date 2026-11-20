import os
import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import MedicalReport, LabParameter
from .forms import ReportUploadForm
from .parser import extract_text_from_file, parse_extracted_text, evaluate_parameter
from .pdf_generator import generate_report_pdf

@login_required
def upload_report(request):
    if request.method == 'POST':
        form = ReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.status = 'pending_confirmation'
            report.save()

            # Execute automated text extraction & parsing
            try:
                raw_text = extract_text_from_file(report.report_file.path)
                report.extracted_raw_text = raw_text
                report.save()

                parsed_items = parse_extracted_text(raw_text)

                # Create initial parameters for user verification
                for item in parsed_items:
                    eval_res = evaluate_parameter(
                        item['test_name'],
                        item['measured_value'],
                        item['reference_min'],
                        item['reference_max']
                    )
                    LabParameter.objects.create(
                        report=report,
                        test_name=item['test_name'],
                        measured_value=item['measured_value'],
                        unit=item['unit'],
                        reference_min=item['reference_min'],
                        reference_max=item['reference_max'],
                        status=eval_res['status'],
                        explanation_en=eval_res['explanation_en'],
                        explanation_hi=eval_res['explanation_hi'],
                    )

                messages.info(request, "Report text parsed successfully! Please review and confirm the extracted values below.")
                return redirect('reports:confirm', pk=report.pk)

            except Exception as e:
                report.status = 'failed'
                report.save()
                messages.error(request, f"Error processing report file: {str(e)}")
                return redirect('reports:history')
    else:
        form = ReportUploadForm()

    return render(request, 'reports/upload.html', {'form': form})


@login_required
def confirm_extracted_data(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk, user=request.user)

    if request.method == 'POST':
        # Process confirmed/edited rows submitted by user
        test_names = request.POST.getlist('test_name[]')
        values = request.POST.getlist('measured_value[]')
        units = request.POST.getlist('unit[]')
        ref_mins = request.POST.getlist('ref_min[]')
        ref_maxs = request.POST.getlist('ref_max[]')

        # Wipe previous temporary parameters and replace with confirmed ones
        report.parameters.all().delete()

        abnormal_count = 0
        total_count = len(test_names)

        for i in range(total_count):
            t_name = test_names[i].strip()
            if not t_name:
                continue

            try:
                m_val = float(values[i]) if values[i].strip() else None
            except ValueError:
                m_val = None

            u_val = units[i].strip() if i < len(units) else ''

            try:
                r_min = float(ref_mins[i]) if ref_mins[i].strip() else None
            except (ValueError, IndexError):
                r_min = None

            try:
                r_max = float(ref_maxs[i]) if ref_maxs[i].strip() else None
            except (ValueError, IndexError):
                r_max = None

            eval_res = evaluate_parameter(t_name, m_val, r_min, r_max)
            if eval_res['is_abnormal']:
                abnormal_count += 1

            LabParameter.objects.create(
                report=report,
                test_name=t_name,
                measured_value=m_val,
                raw_value_str=values[i].strip() if i < len(values) else '',
                unit=u_val,
                reference_min=r_min,
                reference_max=r_max,
                status=eval_res['status'],
                explanation_en=eval_res['explanation_en'],
                explanation_hi=eval_res['explanation_hi'],
            )

        report.status = 'confirmed'
        report.clinical_summary = {
            'total_tests': total_count,
            'abnormal_tests': abnormal_count,
            'confirmed_at': datetime.now().isoformat(),
        }
        report.save()

        messages.success(request, f"Laboratory report confirmed and analyzed successfully ({total_count} parameters evaluated).")
        return redirect('reports:detail', pk=report.pk)

    parameters = report.parameters.all()
    return render(request, 'reports/confirm.html', {'report': report, 'parameters': parameters})


@login_required
def report_detail(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk)
    if report.user != request.user and not request.user.is_doctor and not request.user.is_platform_admin:
        messages.error(request, 'Access denied.')
        return redirect('reports:history')

    parameters = report.parameters.all()
    abnormal_params = parameters.filter(status__in=['low', 'high'])
    normal_params = parameters.filter(status='normal')
    other_params = parameters.filter(status__in=['context_needed', 'unable_to_interpret'])

    return render(request, 'reports/detail.html', {
        'report': report,
        'parameters': parameters,
        'abnormal_params': abnormal_params,
        'normal_params': normal_params,
        'other_params': other_params,
    })


@login_required
def report_history(request):
    reports = MedicalReport.objects.filter(user=request.user)
    return render(request, 'reports/history.html', {'reports': reports})


@login_required
def delete_report(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk, user=request.user)
    if request.method == 'POST':
        # Remove media file from disk
        if report.report_file and os.path.isfile(report.report_file.path):
            try:
                os.remove(report.report_file.path)
            except Exception:
                pass
        report.delete()
        messages.success(request, 'Medical report deleted successfully.')
        return redirect('reports:history')
    return render(request, 'reports/delete_confirm.html', {'report': report})


@login_required
def download_report_pdf(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk)
    if report.user != request.user and not request.user.is_doctor and not request.user.is_platform_admin:
        return HttpResponse("Unauthorized", status=403)

    pdf_bytes = generate_report_pdf(report)
    filename = f"MediPredict_Report_MP{report.id:05d}.pdf"

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def compare_reports(request):
    user_reports = MedicalReport.objects.filter(user=request.user, status='confirmed').order_by('-report_date')
    
    r1_id = request.GET.get('report1')
    r2_id = request.GET.get('report2')

    report1 = None
    report2 = None
    comparison_data = []

    if r1_id and r2_id and r1_id != r2_id:
        report1 = get_object_or_404(MedicalReport, pk=r1_id, user=request.user)
        report2 = get_object_or_404(MedicalReport, pk=r2_id, user=request.user)

        # Match parameters between report 1 and report 2
        p1_map = {p.test_name.lower(): p for p in report1.parameters.all()}
        p2_map = {p.test_name.lower(): p for p in report2.parameters.all()}

        all_keys = set(p1_map.keys()).union(set(p2_map.keys()))
        for key in sorted(all_keys):
            p1 = p1_map.get(key)
            p2 = p2_map.get(key)

            v1 = p1.measured_value if (p1 and p1.measured_value is not None) else None
            v2 = p2.measured_value if (p2 and p2.measured_value is not None) else None

            delta = None
            pct_change = None
            if v1 is not None and v2 is not None:
                delta = round(v2 - v1, 2)
                if v1 != 0:
                    pct_change = round(((v2 - v1) / v1) * 100.0, 1)

            comparison_data.append({
                'name': (p2.test_name if p2 else p1.test_name),
                'unit': (p2.unit if p2 else p1.unit),
                'p1_val': v1,
                'p1_status': p1.get_status_display() if p1 else 'N/A',
                'p2_val': v2,
                'p2_status': p2.get_status_display() if p2 else 'N/A',
                'delta': delta,
                'pct_change': pct_change,
            })

    return render(request, 'reports/compare.html', {
        'reports': user_reports,
        'report1': report1,
        'report2': report2,
        'comparison_data': comparison_data,
        'comparison_json': json.dumps([
            {'name': c['name'], 'r1': c['p1_val'], 'r2': c['p2_val']}
            for c in comparison_data if c['p1_val'] is not None and c['p2_val'] is not None
        ])
    })
