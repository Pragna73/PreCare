import SwiftUI
import UIKit
import CoreLocation

struct AIHealthDecisionView: View {

    let severity: HealthSeverity
    let report: ReportItem?

    init(severity: HealthSeverity, report: ReportItem? = nil) {
        self.severity = severity
        self.report = report
    }

    @State private var isRunningAction = false
    @State private var actionStatus: String?
    @State private var actionError: String?
    @ObservedObject private var locationService = LocationService.shared
    @State private var showLocationEditor = false
    @State private var locationInput = ""

    // MARK: - Navigation State
    @State private var goToDoctor = false
    @State private var goToEmergency = false
    @State private var goToCritical = false

    var body: some View {
        ScrollView(showsIndicators: false) {
            VStack(spacing: 18) {
                decisionCard

                if effectiveSeverity != .critical {
                    nearbyHelpCard
                    meaningCard
                } else {
                    autoBookedEmergencyCard
                }

                actionButtons

                if let actionStatus {
                    CardView {
                        Text(actionStatus)
                            .font(.footnote)
                            .foregroundColor(.green)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                if let actionError {
                    CardView {
                        Text(actionError)
                            .font(.footnote)
                            .foregroundColor(.red)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 16)
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle("AI Health Decision")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showLocationEditor) {
            NavigationStack {
                VStack(spacing: 14) {
                    TextField("City, Country", text: $locationInput)
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

        // MARK: - Navigation Destinations
        .navigationDestination(isPresented: $goToDoctor) {
            BookDoctorView()
        }
        .navigationDestination(isPresented: $goToEmergency) {
            EmergencyTrackingView()
        }
        .navigationDestination(isPresented: $goToCritical) {
            CriticalRiskView()
        }
    }

    // MARK: - Decision Card
    private var decisionCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(titleText)
                .font(.headline)
                .foregroundColor(titleColor)
            HStack(spacing: 4) {
                Image(systemName: "mappin.circle.fill")
                    .foregroundColor(Color(hex: "#FF2D6F"))
                Text("Using real-time GPS location: \(locationService.locationName)")
            }
            .font(.caption)
            .foregroundColor(.secondary)

            Button("Refresh GPS Location") {
                locationService.requestLocationPermission()
            }
            .font(.caption)

            Text(descriptionText)
                .font(.subheadline)
                .foregroundColor(.gray)

            if let report {
                if let reason = report.riskReason {
                    Text("Reason: \(reason)")
                        .font(.footnote)
                        .foregroundColor(.gray)
                }

                if let recommendation = report.recommendation {
                    Text("Recommendation: \(recommendation)")
                        .font(.footnote)
                        .foregroundColor(.gray)
                }

                if let status = report.confirmationStatus {
                    Text("Confirmation: \(status)")
                        .font(.footnote)
                        .foregroundColor(.gray)
                }

                if let plan = report.agentPlans.first {
                    Text("Plan: \(plan.action) (\(plan.status))")
                        .font(.footnote)
                        .foregroundColor(.gray)

                    if let doctor = plan.doctor, let hospital = plan.hospital {
                        Text("\(doctor) • \(hospital)")
                            .font(.footnote)
                            .foregroundColor(.gray)
                    }
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(cardBackground)
        .cornerRadius(16)
    }

    // MARK: - Auto-Booked Emergency Card (Direct parity)
    private var autoBookedEmergencyCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                HStack(spacing: 6) {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                    Text("Emergency Booking Confirmed")
                        .font(.system(size: 15, weight: .bold))
                        .foregroundColor(Color(hex: "#1E293B"))
                }
                Spacer()
                Text("AUTO-BOOKED")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(Color(hex: "#16A34A"))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.green.opacity(0.12))
                    .cornerRadius(6)
            }

            VStack(alignment: .leading, spacing: 8) {
                HStack(spacing: 8) {
                    Image(systemName: "building.2.fill")
                        .foregroundColor(.blue)
                        .frame(width: 20)
                    Text("Hospital: **\(locationService.nearestHospitalName)**")
                        .font(.system(size: 13))
                }
                HStack(spacing: 8) {
                    Image(systemName: "stethoscope")
                        .foregroundColor(.green)
                        .frame(width: 20)
                    Text("Doctor: **\(locationService.doctorOnCall)**")
                        .font(.system(size: 13))
                }
                HStack(spacing: 8) {
                    Image(systemName: "cross.case.fill")
                        .foregroundColor(.red)
                        .frame(width: 20)
                    Text("Ambulance: **Dispatched (ETA: 4 mins)**")
                        .font(.system(size: 13))
                }
            }
            .padding(12)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.red.opacity(0.06))
            .cornerRadius(12)

            if let closest = locationService.nearbyDoctors.first {
                Button {
                    if let mapsUrl = closest.mapsUrl, let url = URL(string: mapsUrl) {
                        UIApplication.shared.open(url)
                    } else if let url = locationService.googleMapsDirectionsUrl(destinationLat: closest.latitude, destinationLon: closest.longitude) {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "arrow.triangle.turn.up.right.diamond.fill")
                        Text("Get Directions to \(closest.name)")
                            .font(.system(size: 13, weight: .bold))
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .background(Color(hex: "#2563EB"))
                    .cornerRadius(12)
                }
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(18)
        .shadow(color: Color.black.opacity(0.04), radius: 6, x: 0, y: 2)
    }

    // MARK: - Action Buttons
    @ViewBuilder
    private var actionButtons: some View {
        switch effectiveSeverity {

        case .safe:
            CardView {
                Text("3 clinics near you are available for routine checkups.")
                    .font(.footnote)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            PrimaryButton(title: isRunningAction ? "Please wait..." : "Book Nearest Clinic", icon: "calendar.badge.plus", color: Color(hex: "#16A34A")) {
                runGoodFlow()
            }
            .disabled(isRunningAction)

            Button("Skip for now") {
                actionStatus = "No problem. You can schedule a routine checkup anytime."
            }
            .font(.footnote)
            .foregroundColor(.secondary)

        case .warning:
            if actionStatus == nil {
                CardView {
                    Text("\(locationService.doctorOnCall) is available today at \(locationService.nearestHospitalName).")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }

                PrimaryButton(title: isRunningAction ? "Please wait..." : "Confirm Appointment", icon: "checkmark.circle.fill", color: .orange) {
                    runWarningFlow()
                }
                .disabled(isRunningAction)

                PrimaryButton(title: "Choose Another Doctor", icon: "person.2.fill", color: Color(hex: "#FF2D6F")) {
                    goToDoctor = true
                }
            }

        case .critical:
            PrimaryButton(title: "Call Emergency Contact", icon: "phone.fill", color: .orange) {
                callEmergencyContact()
            }

            if !isAmbulanceAvailable {
                CardView {
                    Text("No ambulance nearby. Calling nearest hospital emergency line.")
                        .font(.footnote)
                        .foregroundColor(.orange)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            }

            Button("View Emergency Status") {
                goToCritical = true
            }
            .font(.footnote)
            .foregroundColor(.secondary)
        }
    }

    // MARK: - Computed Values
    private var titleText: String {
        switch effectiveSeverity {
        case .safe: return "GOOD: You Are Safe"
        case .warning: return "WARNING: Needs Attention"
        case .critical: return "DANGER: Critical Alert"
        }
    }

    private var descriptionText: String {
        if let recommendation = report?.recommendation, !recommendation.isEmpty {
            return recommendation
        }
        switch effectiveSeverity {
        case .safe:
            return "Everything looks normal. Do you want me to book a doctor for a routine checkup?"
        case .warning:
            return "Your vitals indicate a potential issue. Please consider consulting a doctor."
        case .critical:
            return "Your vitals indicate a serious risk. PreCare AI has automatically initiated doctor booking."
        }
    }

    private var titleColor: Color {
        switch effectiveSeverity {
        case .safe: return .green
        case .warning: return .orange
        case .critical: return .red
        }
    }

    private var cardBackground: Color {
        titleColor.opacity(0.12)
    }

    private var effectiveSeverity: HealthSeverity {
        guard let risk = report?.riskLevel?.uppercased() else { return severity }
        switch risk {
        case "FINE", "GOOD":
            return .safe
        case "MODERATE", "WARNING", "URGENT":
            return .warning
        case "DANGER", "CRITICAL":
            return .critical
        default:
            return severity
        }
    }

    private var nearbyHelpCard: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("Help Near You")
                        .font(.headline)
                    Spacer()
                    Text("📍 Real GPS")
                        .font(.caption2)
                        .foregroundColor(.blue)
                }
                Text("Based on your current location")
                    .font(.caption)
                    .foregroundColor(.secondary)

                helpRow("cross.case.fill", .red, "Ambulance", isAmbulanceAvailable ? locationService.ambulanceETA : "Not available nearby", state: isAmbulanceAvailable ? .available : .unavailable)
                helpRow("building.2.fill", .blue, "Nearest Hospital", locationService.nearestHospitalName, state: .available)
                helpRow("stethoscope", .green, "Doctor On-Call", locationService.doctorOnCall, state: .available)

                if let closest = locationService.nearbyDoctors.first {
                    Button {
                        if let mapsUrl = closest.mapsUrl, let url = URL(string: mapsUrl) {
                            UIApplication.shared.open(url)
                        } else if let url = locationService.googleMapsDirectionsUrl(destinationLat: closest.latitude, destinationLon: closest.longitude) {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        HStack(spacing: 6) {
                            Image(systemName: "arrow.triangle.turn.up.right.diamond.fill")
                                .font(.system(size: 12))
                            Text("Get Directions to \(closest.name)")
                                .font(.system(size: 12, weight: .bold))
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity, minHeight: 38)
                        .background(Color.blue)
                        .cornerRadius(10)
                    }
                    .padding(.top, 4)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var meaningCard: some View {
        CardView {
            VStack(alignment: .leading, spacing: 6) {
                Text("What this means")
                    .font(.headline)
                Text("Based on your location, help is available nearby. We’ve already found the fastest option for you.")
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func helpRow(_ systemImage: String, _ iconColor: Color, _ title: String, _ subtitle: String, state: HelpAvailability) -> some View {
        HStack(spacing: 12) {
            Image(systemName: systemImage)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(iconColor)
                .frame(width: 24, height: 24)
            Circle().fill(state.color).frame(width: 8, height: 8)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.footnote)
                    .fontWeight(.semibold)
                Text(subtitle)
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
            Spacer()
        }
    }

    private func runGoodFlow() {
        runAction {
            let userID = SessionStore.shared.userID.trimmingCharacters(in: .whitespacesAndNewlines)
            let date = Self.tomorrowDateString()
            _ = try await APIClient.shared.bookAppointment(userID: userID, preferredDate: date)
            await MainActor.run {
                actionStatus = "Nearest clinic booked for \(date)."
                goToDoctor = true
            }
        }
    }

    private func runWarningFlow() {
        runAction {
            let userID = SessionStore.shared.userID.trimmingCharacters(in: .whitespacesAndNewlines)
            _ = try await APIClient.shared.autoBookAppointment(userID: userID, location: locationService.locationName)
            if let reportID = report?.id {
                try await APIClient.shared.confirmReport(id: reportID, confirm: true)
            }
            await MainActor.run {
                actionStatus = "Appointment confirmed with \(locationService.nearestHospitalName)."
            }
        }
    }

    private func runDangerFlow() {
        guard let userID = validUserID() else { return }
        let coordString: String
        if let c = locationService.currentCoordinate {
            coordString = "\(c.latitude),\(c.longitude)"
        } else {
            coordString = locationService.locationName
        }
        runAction {
            _ = try await APIClient.shared.triggerEmergency(userID: userID, location: coordString, severity: "high")
            _ = try await APIClient.shared.autoBookAppointment(userID: userID, location: locationService.locationName)
            await MainActor.run {
                actionStatus = "Emergency triggered. Ambulance dispatched to \(locationService.locationName), hospital alerted, and family notified."
                goToCritical = true
            }
        }
    }

    private func runAction(_ action: @escaping () async throws -> Void) {
        isRunningAction = true
        actionError = nil
        actionStatus = nil
        Task {
            do {
                try await action()
                isRunningAction = false
            } catch {
                actionError = error.localizedDescription
                isRunningAction = false
            }
        }
    }

    private func validUserID() -> String? {
        let userID = SessionStore.shared.userID.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !userID.isEmpty else {
            actionError = "Missing user_id. Please login again."
            return nil
        }
        return userID
    }

    private var isAmbulanceAvailable: Bool {
        true
    }

    private func callEmergencyContact() {
        if let url = URL(string: "tel://112") {
            UIApplication.shared.open(url)
        } else {
            actionError = "Unable to place emergency call on this device."
        }
    }

    private static func tomorrowDateString() -> String {
        let date = Calendar.current.date(byAdding: .day, value: 1, to: Date()) ?? Date()
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: date)
    }
}

private enum HelpAvailability {
    case available
    case limited
    case unavailable

    var color: Color {
        switch self {
        case .available:
            return .green
        case .limited:
            return .orange
        case .unavailable:
            return .gray
        }
    }
}
