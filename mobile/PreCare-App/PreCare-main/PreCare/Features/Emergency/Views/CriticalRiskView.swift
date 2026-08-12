//
//  CriticalRiskView.swift
//  PreCare
//

import SwiftUI

struct CriticalRiskView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var router: AppRouter

    private func callEmergency() {
        let emergencyNumber = "911" // change if needed (112 / 108 for India)
        if let url = URL(string: "tel://\(emergencyNumber)") {
            UIApplication.shared.open(url)
        }
    }

    var body: some View {
        VStack(spacing: 24) {

            // MARK: - Back Button Bar
            HStack {
                Button {
                    if !router.path.isEmpty {
                        router.pop()
                    }
                    dismiss()
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 18, weight: .semibold))
                        Text("Back")
                            .font(.system(size: 16, weight: .semibold))
                    }
                    .foregroundColor(.white)
                    .padding(.vertical, 8)
                    .padding(.horizontal, 14)
                    .background(Color.white.opacity(0.18))
                    .clipShape(Capsule())
                }

                Spacer()
            }
            .padding(.top, 4)

            // MARK: - Alert Icon
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 60))
                .foregroundColor(.red)

            VStack(spacing: 8) {
                Text("Critical risk detected.")
                    .font(.title2)
                    .fontWeight(.bold)

                Text("""
AI Analysis complete. Emergency protocols have been initiated automatically.
""")
                .font(.subheadline)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
            }

            // MARK: - Status Cards
            VStack(spacing: 16) {

                EmergencyActionRow(
                    title: "Ambulance dispatched",
                    subtitle: "ETA: 4 mins (Saveetha Rapid Response)",
                    status: "CONFIRMED",
                    icon: "cross.case.fill"
                )

                EmergencyActionRow(
                    title: "\(LocationService.shared.doctorOnCall) alerted",
                    subtitle: "Maternal Emergency Report Sent",
                    status: "NOTIFIED",
                    icon: "stethoscope"
                )

                EmergencyActionRow(
                    title: "Family contacts",
                    subtitle: "Primary contact notified via SMS",
                    status: "CONFIRMED",
                    icon: "person.2.fill"
                )
            }

            Spacer()
        }
        .padding()
        .background(Color.black.opacity(0.95))
        .foregroundColor(.white)
        .navigationBarBackButtonHidden(true)
    }
}
