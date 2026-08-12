import SwiftUI
import CoreLocation

struct AnalysisResultView: View {
    let severity: HealthSeverity
    let report: ReportItem?

    init(severity: HealthSeverity = .safe, report: ReportItem? = nil) {
        self.severity = severity
        self.report = report
    }

    @State private var isSubmittingDecision = false
    @State private var decisionError: String?
    @State private var decisionMessage: String?
    @State private var showDecision = false
    @ObservedObject private var locationService = LocationService.shared
    @State private var showLocationEditor = false
    @State private var locationInput = ""
    @State private var confirmationDone = false

    private var effectiveRisk: String {
        if let level = report?.riskLevel, !level.isEmpty {
            let u = level.uppercased()
            if u == "DANGER" || u == "CRITICAL" || u == "HIGH" { return "HIGH" }
            if u == "WARNING" || u == "MODERATE" || u == "MEDIUM" { return "MEDIUM" }
            return "LOW"
        }
        switch severity {
        case .critical: return "HIGH"
        case .warning: return "MEDIUM"
        case .safe: return "LOW"
        }
    }

    private var isHighRisk: Bool { effectiveRisk == "HIGH" }
    private var isMediumRisk: Bool { effectiveRisk == "MEDIUM" }

    var body: some View {
        ScrollView(showsIndicators: false) {
            VStack(spacing: 18) {
                // 1. Top Demographics Header Suite
                patientSuiteCard

                // 2. Risk Alert Banner
                riskAlertBanner

                // 3. High Risk Critical Emergency Cards (if High Risk: Auto-Booked Doctor & Hospital)
                if isHighRisk {
                    emergencyProtocolCard
                    autoBookedTicketCard
                }

                // 4. Moderate Risk Action Confirmation (if Warning)
                if isMediumRisk && !confirmationDone {
                    warningConfirmationCard
                }

                // 5. Prenatal Clinical Indicators Table
                indicatorsTableCard

                // 6. Proximity-Sorted Regional Hospitals (ONLY shown if NOT High Risk / Auto-Booked)
                if !isHighRisk {
                    nearbyHospitalsSection
                }

                // 7. Structured Data & Clinical Summary
                clinicalSummaryCard

                // 8. Navigation to Detailed Agentic Decision
                PrimaryButton(title: "View Agentic AI Decision", icon: "brain.head.profile", color: Color(hex: "#FF2D6F")) {
                    showDecision = true
                }
                .padding(.top, 4)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 16)
        }
        .background(Color(hex: "#F8FAFC"))
        .navigationDestination(isPresented: $showDecision) {
            AIHealthDecisionView(severity: severity, report: report)
        }
        .sheet(isPresented: $showLocationEditor) {
            NavigationStack {
                VStack(spacing: 14) {
                    TextField("City, State", text: $locationInput)
                        .textFieldStyle(.roundedBorder)

                    PrimaryButton(title: "Use This Location") {
                        let trimmed = locationInput.trimmingCharacters(in: .whitespacesAndNewlines)
                        if !trimmed.isEmpty {
                            locationService.locationName = trimmed
                        }
                        showLocationEditor = false
                    }
                }
                .padding()
                .navigationTitle("Change Location")
                .navigationBarTitleDisplayMode(.inline)
            }
        }
        .navigationTitle("Analysis Result")
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - 1. Patient Suite Card (Website Design Parity)
    private var patientSuiteCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("ANALYSIS RESULT SUITE")
                    .font(.system(size: 11, weight: .bold))
                    .foregroundColor(Color(hex: "#FF2D6F"))
                    .tracking(1.0)
                Spacer()
                HStack(spacing: 4) {
                    Image(systemName: "mappin.circle.fill")
                        .foregroundColor(Color(hex: "#FF2D6F"))
                    Text("Near \(locationService.locationName)")
                }
                .font(.system(size: 11, weight: .medium))
                .foregroundColor(.secondary)
            }

            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Patient: \(report?.formattedPatientName ?? "Ananya R")")
                        .font(.system(size: 22, weight: .bold, design: .serif))
                        .foregroundColor(Color(hex: "#1E293B"))

                    HStack(spacing: 6) {
                        Text("Age: \(report?.formattedAge ?? 38) Years Old")
                        Text("•")
                        Text("Maternal Biomarker Report")
                    }
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.secondary)
                }

                Spacer()

                // Risk Level Badge
                VStack(alignment: .trailing, spacing: 4) {
                    Text("Identified Risk Level")
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundColor(.secondary)

                    HStack(spacing: 5) {
                        Circle()
                            .fill(riskBadgeColor)
                            .frame(width: 8, height: 8)
                        Text(riskBadgeTitle)
                            .font(.system(size: 12, weight: .bold))
                            .foregroundColor(riskBadgeColor)
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(riskBadgeColor.opacity(0.12))
                    .cornerRadius(8)
                }
            }
        }
        .padding(18)
        .background(Color.white)
        .cornerRadius(20)
        .shadow(color: Color.black.opacity(0.04), radius: 8, x: 0, y: 2)
    }

    // MARK: - 2. Risk Alert Banner
    private var riskAlertBanner: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: alertBannerIcon)
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(alertBannerColor)
                .padding(.top, 2)

            VStack(alignment: .leading, spacing: 4) {
                Text(alertBannerTitle)
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(Color(hex: "#1E293B"))

                Text(alertBannerDescription)
                    .font(.system(size: 12))
                    .foregroundColor(Color(hex: "#475569"))
                    .lineSpacing(2)
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(alertBannerBg)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(alertBannerBorder, lineWidth: 1)
        )
    }

    // MARK: - 3. High Risk Critical Emergency Protocol Card (Website Parity)
    private var emergencyProtocolCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 10) {
                Image(systemName: "light.beacon.max.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.white)

                VStack(alignment: .leading, spacing: 2) {
                    Text("Critical Emergency Protocol Activated")
                        .font(.system(size: 16, weight: .bold, design: .serif))
                        .foregroundColor(.white)
                    Text("High Risk indicators detected. Emergency dispatch and doctor booking executed automatically.")
                        .font(.system(size: 11))
                        .foregroundColor(Color.white.opacity(0.85))
                }
            }
            .padding(.bottom, 6)
            .overlay(
                Rectangle()
                    .frame(height: 1)
                    .foregroundColor(Color.white.opacity(0.15)),
                alignment: .bottom
            )

            // 3-Grid items
            VStack(spacing: 10) {
                // Ambulance
                HStack {
                    VStack(alignment: .leading, spacing: 3) {
                        HStack(spacing: 5) {
                            Image(systemName: "cross.case.fill")
                                .foregroundColor(.red)
                            Text("AMBULANCE DISPATCH")
                                .font(.system(size: 10, weight: .bold))
                                .foregroundColor(Color(hex: "#FECDD3"))
                        }
                        Text("Dispatched (ETA: 4 mins)")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(.white)
                    }
                    Spacer()
                    Text("✓ CONFIRMED")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(Color(hex: "#4ADE80"))
                }
                .padding(12)
                .background(Color.white.opacity(0.12))
                .cornerRadius(12)

                // Hospital Appointment
                HStack {
                    VStack(alignment: .leading, spacing: 3) {
                        HStack(spacing: 5) {
                            Image(systemName: "building.2.fill")
                                .foregroundColor(.blue)
                            Text("HOSPITAL APPOINTMENT")
                                .font(.system(size: 10, weight: .bold))
                                .foregroundColor(Color(hex: "#FECDD3"))
                        }
                        Text(locationService.nearestHospitalName)
                            .font(.system(size: 13, weight: .bold))
                            .foregroundColor(.white)
                            .lineLimit(1)
                    }
                    Spacer()
                    Text("✓ AUTO-BOOKED")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(Color(hex: "#4ADE80"))
                }
                .padding(12)
                .background(Color.white.opacity(0.12))
                .cornerRadius(12)

                // Family Contact Alerted
                HStack {
                    VStack(alignment: .leading, spacing: 3) {
                        HStack(spacing: 5) {
                            Image(systemName: "phone.fill")
                                .foregroundColor(.green)
                            Text("FAMILY CONTACT ALERTED")
                                .font(.system(size: 10, weight: .bold))
                                .foregroundColor(Color(hex: "#FECDD3"))
                        }
                        Text("Primary Emergency Contact")
                            .font(.system(size: 13, weight: .bold))
                            .foregroundColor(.white)
                    }
                    Spacer()
                    Text("✓ NOTIFIED VIA SMS")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(Color(hex: "#4ADE80"))
                }
                .padding(12)
                .background(Color.white.opacity(0.12))
                .cornerRadius(12)
            }
        }
        .padding(18)
        .background(
            LinearGradient(
                colors: [Color(hex: "#881337"), Color(hex: "#9F1239"), Color(hex: "#BE123C")],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(22)
        .shadow(color: Color(hex: "#BE123C").opacity(0.3), radius: 10, x: 0, y: 4)
    }

    // MARK: - Auto-Booked Confirmation Ticket Card
    private var autoBookedTicketCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            ticketHeader
            ticketDescription
            ticketPatientDetails
            ticketDirectionsButton
        }
        .padding(18)
        .background(Color.white)
        .cornerRadius(20)
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(Color.red.opacity(0.2), lineWidth: 1.5)
        )
        .shadow(color: Color.black.opacity(0.04), radius: 8, x: 0, y: 2)
    }

    private var ticketHeader: some View {
        HStack {
            HStack(spacing: 6) {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.red)
                Text("Automatic Emergency Booking Confirmed")
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(Color(hex: "#991B1B"))
            }
            Spacer()
            Text("AUTO-BOOKED")
                .font(.system(size: 10, weight: .bold))
                .foregroundColor(Color(hex: "#991B1B"))
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.red.opacity(0.12))
                .cornerRadius(6)
        }
    }

    private var ticketDescription: some View {
        Text("Because critical high-risk indicators were detected, an emergency appointment has been automatically booked at top-rated hospital **\(locationService.nearestHospitalName)**.")
            .font(.system(size: 12))
            .foregroundColor(Color(hex: "#475569"))
            .lineSpacing(2)
    }

    private var ticketPatientDetails: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                HStack(spacing: 4) {
                    Image(systemName: "person.fill")
                        .foregroundColor(Color(hex: "#FF2D6F"))
                    Text("Patient: **\(report?.formattedPatientName ?? "Ananya R")**")
                }
                Spacer()
                HStack(spacing: 4) {
                    Image(systemName: "calendar")
                        .foregroundColor(.secondary)
                    Text("Age: **\(report?.formattedAge ?? 38) Yrs**")
                }
            }
            HStack(spacing: 4) {
                Image(systemName: "building.2.fill")
                    .foregroundColor(.blue)
                Text("Hospital: **\(locationService.nearestHospitalName)**")
            }
            HStack(spacing: 4) {
                Image(systemName: "stethoscope")
                    .foregroundColor(.green)
                Text("Specialist On-Call: **\(locationService.doctorOnCall)**")
            }
        }
        .font(.system(size: 12))
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.red.opacity(0.05))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.red.opacity(0.15), lineWidth: 1)
        )
    }

    @ViewBuilder
    private var ticketDirectionsButton: some View {
        if let closest = locationService.nearbyDoctors.first {
            HStack(spacing: 10) {
                Button {
                    if let mapsUrl = closest.mapsUrl, let url = URL(string: mapsUrl) {
                        UIApplication.shared.open(url)
                    } else if let url = locationService.googleMapsDirectionsUrl(destinationLat: closest.latitude, destinationLon: closest.longitude) {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "arrow.triangle.turn.up.right.diamond.fill")
                        Text("Directions")
                            .font(.system(size: 13, weight: .bold))
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity, minHeight: 46)
                    .background(Color(hex: "#2563EB"))
                    .cornerRadius(12)
                }

                Button {
                    let cleanPhone = closest.phone.filter { "0123456789+".contains($0) }
                    if let url = URL(string: "tel://\(cleanPhone)") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "phone.fill")
                        Text("Call Hospital")
                            .font(.system(size: 13, weight: .bold))
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity, minHeight: 46)
                    .background(Color(hex: "#16A34A"))
                    .cornerRadius(12)
                }
            }
        }
    }

    // MARK: - 4. Moderate Risk Confirmation Card
    private var warningConfirmationCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "calendar.badge.clock")
                    .foregroundColor(.orange)
                Text("Nearest Doctor Auto-Scheduled")
                    .font(.system(size: 14, weight: .bold))
                Spacer()
                Text("PENDING")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(.orange)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    .background(Color.orange.opacity(0.12))
                    .cornerRadius(6)
            }

            Text("\(locationService.doctorOnCall) at \(locationService.nearestHospitalName) has been reserved. Please tap Confirm to lock in your appointment.")
                .font(.system(size: 12))
                .foregroundColor(.secondary)

            HStack(spacing: 12) {
                Button {
                    submitConfirmation(true)
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "checkmark.circle.fill")
                        Text(isSubmittingDecision ? "Confirming..." : "Confirm Appointment")
                            .font(.system(size: 14, weight: .bold))
                    }
                    .frame(maxWidth: .infinity, minHeight: 46)
                    .foregroundColor(.white)
                    .background(Color(hex: "#16A34A"))
                    .cornerRadius(12)
                }
                .disabled(isSubmittingDecision)

                Button {
                    submitConfirmation(false)
                } label: {
                    Text("Decline")
                        .font(.system(size: 14, weight: .semibold))
                        .frame(width: 90, height: 46)
                        .foregroundColor(Color(hex: "#EF4444"))
                        .background(Color.red.opacity(0.1))
                        .cornerRadius(12)
                }
                .disabled(isSubmittingDecision)
            }

            if let decisionMessage {
                Text("✓ \(decisionMessage)")
                    .font(.footnote)
                    .foregroundColor(.green)
            }

            if let decisionError {
                Text(decisionError)
                    .font(.footnote)
                    .foregroundColor(.red)
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(18)
        .overlay(
            RoundedRectangle(cornerRadius: 18)
                .stroke(Color.orange.opacity(0.25), lineWidth: 1)
        )
    }

    // MARK: - 5. Prenatal Clinical Indicators Table (IndicatorsTable Parity)
    private var indicatorsTableCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Image(systemName: "waveform.path.ecg")
                    .foregroundColor(Color(hex: "#FF2D6F"))
                Text("Prenatal Clinical Indicators")
                    .font(.system(size: 15, weight: .bold))
                Spacer()
                Text("\(displayIndicators.count) Extracted")
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(.secondary)
            }

            // Table Header
            HStack {
                Text("HEALTH MARKER / PARAMETER")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)

                Text("READING")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(.secondary)
                    .frame(width: 100, alignment: .leading)

                Text("STATUS")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(.secondary)
                    .frame(width: 70, alignment: .trailing)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 8)
            .background(Color(hex: "#F1F5F9"))
            .cornerRadius(8)

            // Table Rows
            VStack(spacing: 0) {
                ForEach(Array(displayIndicators.enumerated()), id: \.offset) { index, item in
                    let isAbnormal = item.status.lowercased() == "abnormal" || item.status.lowercased() == "attention" || item.status.lowercased() == "danger"

                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(item.name)
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundColor(Color(hex: "#1E293B"))

                            if !item.normalRange.isEmpty {
                                Text("Ref: \(item.normalRange)")
                                    .font(.system(size: 10))
                                    .foregroundColor(.secondary)
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)

                        Text(item.value)
                            .font(.system(size: 13, weight: .bold, design: .monospaced))
                            .foregroundColor(isAbnormal ? Color(hex: "#B91C1C") : Color(hex: "#334155"))
                            .frame(width: 100, alignment: .leading)

                        // Badge
                        HStack(spacing: 3) {
                            Image(systemName: isAbnormal ? "exclamationmark.triangle.fill" : "checkmark.circle.fill")
                                .font(.system(size: 10))
                            Text(isAbnormal ? "Attention" : "Normal")
                                .font(.system(size: 10, weight: .bold))
                        }
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(isAbnormal ? Color.amberBadgeBg : Color.greenBadgeBg)
                        .foregroundColor(isAbnormal ? Color.amberBadgeText : Color.greenBadgeText)
                        .cornerRadius(6)
                        .frame(width: 70, alignment: .trailing)
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 10)

                    if index < displayIndicators.count - 1 {
                        Divider()
                            .padding(.horizontal, 6)
                    }
                }
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(20)
        .shadow(color: Color.black.opacity(0.04), radius: 8, x: 0, y: 2)
    }

    // MARK: - 6. Proximity-Sorted Regional Hospitals Roster
    private var nearbyHospitalsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "cross.case.fill")
                    .foregroundColor(Color(hex: "#2563EB"))
                Text("Verified Regional Hospitals")
                    .font(.system(size: 15, weight: .bold))
                Spacer()
                Text("Proximity-Sorted")
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(Color(hex: "#2563EB"))
            }

            ForEach(locationService.nearbyDoctors.prefix(3)) { doc in
                DoctorCard(
                    doctor: doc,
                    isSelected: false,
                    onSelect: {
                        if let mapsUrl = doc.mapsUrl, let url = URL(string: mapsUrl) {
                            UIApplication.shared.open(url)
                        } else if let url = locationService.googleMapsDirectionsUrl(destinationLat: doc.latitude, destinationLon: doc.longitude) {
                            UIApplication.shared.open(url)
                        }
                    }
                )
            }
        }
    }

    // MARK: - 7. Structured Data & Clinical Summary Card
    private var clinicalSummaryCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Clinical Analysis & Signals")
                .font(.system(size: 14, weight: .bold))
                .foregroundColor(Color(hex: "#1E293B"))

            if let reason = report?.riskReason, !reason.isEmpty {
                Text(reason)
                    .font(.system(size: 12))
                    .foregroundColor(Color(hex: "#475569"))
                    .lineSpacing(2)
            }

            if let recommendation = report?.recommendation, !recommendation.isEmpty {
                Text("• **Guidance:** \(recommendation)")
                    .font(.system(size: 12))
                    .foregroundColor(Color(hex: "#475569"))
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white)
        .cornerRadius(18)
        .shadow(color: Color.black.opacity(0.04), radius: 8, x: 0, y: 2)
    }

    // MARK: - Indicator Data Source
    private var displayIndicators: [BiomarkerIndicator] {
        if let indicators = report?.indicators, !indicators.isEmpty {
            return indicators
        }
        // Fallback to sample indicators
        return [
            BiomarkerIndicator(name: "Blood Pressure", value: "165/110 mmHg", normalRange: "90/60 - 120/80", status: "abnormal"),
            BiomarkerIndicator(name: "Maternal Pulse Rate", value: "102 bpm", normalRange: "60 - 99 bpm", status: "abnormal"),
            BiomarkerIndicator(name: "Respiratory Rate", value: "22 /min", normalRange: "12 - 20 /min", status: "abnormal"),
            BiomarkerIndicator(name: "Oxygen Saturation (SpO₂)", value: "96 %", normalRange: "95 - 100 %", status: "normal"),
            BiomarkerIndicator(name: "Gestational Age (POG)", value: "34 Weeks + 2 Days", normalRange: "37 - 42 Wks", status: "normal"),
            BiomarkerIndicator(name: "Body Temperature", value: "37.2 °C", normalRange: "36.5 - 37.5 °C", status: "normal"),
            BiomarkerIndicator(name: "Maternal Weight", value: "82 kg", normalRange: "Trimester gain", status: "normal"),
        ]
    }

    // MARK: - Visual Helpers
    private var riskBadgeColor: Color {
        if isHighRisk { return Color(hex: "#DC2626") }
        if isMediumRisk { return Color(hex: "#D97706") }
        return Color(hex: "#16A34A")
    }

    private var riskBadgeTitle: String {
        if isHighRisk { return "High Risk" }
        if isMediumRisk { return "Moderate Risk" }
        return "Safe / Normal"
    }

    private var alertBannerIcon: String {
        if isHighRisk { return "exclamationmark.octagon.fill" }
        if isMediumRisk { return "exclamationmark.triangle.fill" }
        return "checkmark.seal.fill"
    }

    private var alertBannerColor: Color {
        if isHighRisk { return Color(hex: "#DC2626") }
        if isMediumRisk { return Color(hex: "#D97706") }
        return Color(hex: "#16A34A")
    }

    private var alertBannerBg: Color {
        if isHighRisk { return Color(hex: "#FEF2F2") }
        if isMediumRisk { return Color(hex: "#FFFBEB") }
        return Color(hex: "#F0FDF4")
    }

    private var alertBannerBorder: Color {
        if isHighRisk { return Color(hex: "#FECACA") }
        if isMediumRisk { return Color(hex: "#FDE68A") }
        return Color(hex: "#BBF7D0")
    }

    private var alertBannerTitle: String {
        if isHighRisk { return "Critical High Risk Detected — Emergency Protocol & Doctor Auto-Booked" }
        if isMediumRisk { return "Observational Care Recommended" }
        return "Health Metrics Look Good"
    }

    private var alertBannerDescription: String {
        if isHighRisk {
            return "Attention: Severe bio-markers detected. An emergency protocol has been initiated automatically. Nearby doctor auto-booked and ambulance dispatched."
        }
        if isMediumRisk {
            return "Some metrics deviate slightly from baseline pregnancy medians. We recommend reviewing nearby doctors and booking a checkup."
        }
        return "All analyzed indices align comfortably within standard maternal ranges. Continue your routine prenatal care."
    }

    private func submitConfirmation(_ confirm: Bool) {
        guard let reportID = report?.id else { return }
        isSubmittingDecision = true
        decisionError = nil
        decisionMessage = nil

        Task {
            do {
                try await APIClient.shared.confirmReport(id: reportID, confirm: confirm)
                decisionMessage = confirm ? "Action confirmed successfully." : "Action denied successfully."
                confirmationDone = true
                isSubmittingDecision = false
            } catch {
                decisionError = error.localizedDescription
                isSubmittingDecision = false
            }
        }
    }
}

// MARK: - Badge Color Extensions
private extension Color {
    static let amberBadgeBg = Color(hex: "#FEF3C7")
    static let amberBadgeText = Color(hex: "#92400E")
    static let greenBadgeBg = Color(hex: "#DCFCE7")
    static let greenBadgeText = Color(hex: "#166534")
}
