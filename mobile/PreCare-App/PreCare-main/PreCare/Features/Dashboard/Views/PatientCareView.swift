import SwiftUI

struct PatientCareView: View {
    @State private var isLoading = false
    @State private var message: String?
    @State private var errorMessage: String?
    @State private var latestAppointmentDoctor: String = "Dr. S. Lakshmi, MD"
    @State private var latestAppointmentHospital: String = "Saveetha Medical College & Hospital"
    @State private var latestAppointmentTime: String = "Tomorrow, 10:30 AM"
    @State private var hasBookedAppointment = true

    var body: some View {
        ScrollView(showsIndicators: false) {
            VStack(spacing: 16) {
                // Header Card
                CardView {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Your Care & Appointments")
                            .font(.title3)
                            .fontWeight(.bold)
                        Text("Manage prenatal checkups, specialist consultations, and track your clinical milestones.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                // Active Upcoming Appointment Card
                CardView {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Upcoming Appointment")
                                    .font(.caption)
                                    .fontWeight(.bold)
                                    .foregroundColor(.secondary)
                                    .textCase(.uppercase)
                                Text(latestAppointmentDoctor)
                                    .font(.headline)
                                    .foregroundColor(.primary)
                            }
                            Spacer()
                            HStack(spacing: 4) {
                                Circle()
                                    .fill(Color.green)
                                    .frame(width: 8, height: 8)
                                Text("CONFIRMED")
                                    .font(.caption2)
                                    .fontWeight(.bold)
                                    .foregroundColor(.green)
                            }
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.green.opacity(0.12))
                            .cornerRadius(8)
                        }

                        Divider()

                        HStack(spacing: 16) {
                            HStack(spacing: 8) {
                                Image(systemName: "building.2.fill")
                                    .foregroundColor(Color(hex: "#FF2D6F"))
                                Text(latestAppointmentHospital)
                                    .font(.footnote)
                                    .foregroundColor(.secondary)
                            }
                        }

                        HStack(spacing: 16) {
                            HStack(spacing: 8) {
                                Image(systemName: "calendar.badge.clock")
                                    .foregroundColor(Color(hex: "#FF2D6F"))
                                Text(latestAppointmentTime)
                                    .font(.footnote)
                                    .fontWeight(.semibold)
                                    .foregroundColor(.primary)
                            }
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                // Book Prenatal Checkup Card
                CardView {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Schedule Checkup")
                            .font(.headline)
                        Text("Book your next routine prenatal examination or consultation with your obstetrician.")
                            .font(.footnote)
                            .foregroundColor(.secondary)

                        PrimaryButton(
                            title: isLoading ? "Booking Appointment..." : "Schedule Prenatal Appointment",
                            color: Color(hex: "#FF2D6F")
                        ) {
                            runBookAppointment()
                        }
                        .disabled(isLoading)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                // Prenatal Care Milestones
                CardView {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Prenatal Care Schedule")
                            .font(.headline)

                        VStack(spacing: 10) {
                            careMilestoneRow(
                                title: "Routine Antenatal Vitals & BP Check",
                                subtitle: "Blood pressure, maternal weight & heart rate",
                                status: "Completed",
                                statusColor: .green
                            )
                            Divider()
                            careMilestoneRow(
                                title: "Ultrasound Biometry & FHR Scan",
                                subtitle: "Fetal growth parameters & amniotic fluid assessment",
                                status: "Scheduled",
                                statusColor: Color(hex: "#FF2D6F")
                            )
                            Divider()
                            careMilestoneRow(
                                title: "Maternal Glucose & Hb Profiling",
                                subtitle: "Gestational diabetes & prenatal anemia screening",
                                status: "Scheduled",
                                statusColor: .orange
                            )
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                if let message {
                    CardView {
                        HStack(spacing: 8) {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text(message)
                                .font(.footnote)
                                .foregroundColor(.green)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                if let errorMessage {
                    CardView {
                        HStack(spacing: 8) {
                            Image(systemName: "exclamationmark.circle.fill")
                                .foregroundColor(.red)
                            Text(errorMessage)
                                .font(.footnote)
                                .foregroundColor(.red)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
            .padding()
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle("Care")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await loadAppointmentData()
        }
    }

    private func careMilestoneRow(title: String, subtitle: String, status: String, statusColor: Color) -> some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.footnote)
                    .fontWeight(.medium)
                Text(subtitle)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            Spacer()
            Text(status)
                .font(.caption2)
                .fontWeight(.bold)
                .foregroundColor(statusColor)
                .padding(.horizontal, 6)
                .padding(.vertical, 2)
                .background(statusColor.opacity(0.12))
                .cornerRadius(6)
        }
    }

    private func loadAppointmentData() async {
        guard let userID = validUserID() else { return }
        do {
            let snapshot = try await APIClient.shared.dashboardSnapshot(userID: userID)
            if let label = snapshot.nextAppointmentLabel, !label.isEmpty, label.lowercased() != "no appointment" {
                latestAppointmentDoctor = label
            }
        } catch {
            // Keep default display
        }
    }

    private func runBookAppointment() {
        guard let userID = validUserID() else { return }
        isLoading = true
        errorMessage = nil
        message = nil

        Task {
            do {
                let date = tomorrowDateString()
                let result = try await APIClient.shared.bookAppointment(userID: userID, preferredDate: date)
                message = "Appointment successfully scheduled: \(result)"
                latestAppointmentDoctor = "Dr. S. Lakshmi, MD"
                latestAppointmentHospital = "Saveetha Medical College & Hospital"
                latestAppointmentTime = "Tomorrow, 10:30 AM"
                hasBookedAppointment = true
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }

    private func validUserID() -> String? {
        let userID = SessionStore.shared.userID.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !userID.isEmpty else {
            errorMessage = "Please login again to continue."
            return nil
        }
        return userID
    }

    private func tomorrowDateString() -> String {
        let date = Calendar.current.date(byAdding: .day, value: 1, to: Date()) ?? Date()
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: date)
    }
}
