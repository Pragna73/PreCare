//
//  AppointmentConfirmationView.swift
//  PreCare
//

import SwiftUI
import UIKit
import CoreLocation

struct AppointmentConfirmationView: View {
    let doctor: Doctor
    var appointmentDate: String = "Tomorrow, Aug 9, 2026"
    var appointmentTime: String = "10:00 AM - 10:45 AM"

    @ObservedObject private var locationService = LocationService.shared
    @EnvironmentObject var router: AppRouter
    @Environment(\.dismiss) private var dismiss
    @State private var bookingID = "PRECARE-APT-\(Int.random(in: 1000...9999))"
    @State private var isCopied = false

    private func openDirections() {
        if let mapsUrl = doctor.mapsUrl, let url = URL(string: mapsUrl) {
            UIApplication.shared.open(url)
        } else {
            let userLat = locationService.currentCoordinate?.latitude ?? 13.0286
            let userLon = locationService.currentCoordinate?.longitude ?? 80.0164
            let destLat = doctor.latitude
            let destLon = doctor.longitude
            let urlString = "https://www.google.com/maps/dir/?api=1&origin=\(userLat),\(userLon)&destination=\(destLat),\(destLon)&travelmode=driving"
            if let url = URL(string: urlString) {
                UIApplication.shared.open(url)
            }
        }
    }

    var body: some View {
        ScrollView(showsIndicators: false) {
            VStack(spacing: 24) {

                Spacer().frame(height: 10)

                // Success Icon & Title
                VStack(spacing: 8) {
                    ZStack {
                        Circle()
                            .fill(Color.green.opacity(0.15))
                            .frame(width: 84, height: 84)

                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 56))
                            .foregroundColor(.green)
                    }

                    Text("Appointment Confirmed!")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.primary)

                    Text("Your prenatal consultation has been successfully booked.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 20)
                }

                // Official Appointment Ticket Card
                VStack(spacing: 0) {
                    // Header of ticket
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("PRECARE MEDICAL APPOINTMENT")
                                .font(.system(size: 11, weight: .bold))
                                .foregroundColor(.white.opacity(0.85))
                                .tracking(1)

                            Text(doctor.name)
                                .font(.system(size: 18, weight: .bold))
                                .foregroundColor(.white)

                            Text("\(doctor.doctorName) • \(doctor.specialization)")
                                .font(.system(size: 13, weight: .medium))
                                .foregroundColor(.white.opacity(0.9))
                        }
                        Spacer()

                        Image(systemName: "stethoscope.circle.fill")
                            .font(.system(size: 40))
                            .foregroundColor(.white.opacity(0.9))
                    }
                    .padding(20)
                    .background(
                        LinearGradient(
                            colors: [Color(hex: "#FF2D6F"), Color(hex: "#E01A5A")],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )

                    // Ticket Details
                    VStack(spacing: 16) {

                        // Date & Time Row
                        HStack(spacing: 16) {
                            VStack(alignment: .leading, spacing: 4) {
                                Label("Date", systemImage: "calendar")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text(appointmentDate)
                                    .font(.system(size: 14, weight: .semibold))
                            }
                            Spacer()
                            VStack(alignment: .trailing, spacing: 4) {
                                Label("Time Slot", systemImage: "clock")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text(appointmentTime)
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundColor(Color(hex: "#FF2D6F"))
                            }
                        }

                        Divider()

                        // Hospital / Clinic Location & Proximity
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Label("Hospital Location", systemImage: "mappin.and.ellipse")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Spacer()
                                if let dist = doctor.distanceKm {
                                    Text("📍 \(String(format: "%.1f km away", dist))")
                                        .font(.system(size: 11, weight: .bold))
                                        .foregroundColor(.blue)
                                        .padding(.horizontal, 6)
                                        .padding(.vertical, 2)
                                        .background(Color.blue.opacity(0.1))
                                        .cornerRadius(6)
                                }
                            }

                            Text(doctor.name)
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.primary)

                            Text(doctor.address)
                                .font(.caption)
                                .foregroundColor(.secondary)

                            // Direct Get Directions Button on Ticket
                            Button {
                                openDirections()
                            } label: {
                                HStack(spacing: 6) {
                                    Image(systemName: "arrow.triangle.turn.up.right.diamond.fill")
                                        .font(.system(size: 12))
                                    Text("Get Driving Directions on Google Maps")
                                        .font(.system(size: 12, weight: .bold))
                                }
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity, minHeight: 38)
                                .background(Color.blue)
                                .cornerRadius(10)
                            }
                            .padding(.top, 4)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)

                        Divider()

                        // Patient & Reference
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Label("Patient Contact", systemImage: "phone.fill")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text(SessionStore.shared.cachedPhone.isEmpty ? "+91 9885757159" : SessionStore.shared.cachedPhone)
                                    .font(.system(size: 13, weight: .medium))
                            }
                            Spacer()
                            VStack(alignment: .trailing, spacing: 4) {
                                Label("Booking Reference", systemImage: "ticket.fill")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text(bookingID)
                                    .font(.system(size: 13, weight: .bold))
                                    .foregroundColor(.primary)
                            }
                        }
                    }
                    .padding(20)
                    .background(Color(.secondarySystemGroupedBackground))
                }
                .cornerRadius(20)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(Color.gray.opacity(0.2), lineWidth: 1)
                )
                .shadow(color: Color.black.opacity(0.06), radius: 10, x: 0, y: 4)

                // SMS Notification Banner
                HStack(spacing: 12) {
                    Image(systemName: "message.fill")
                        .foregroundColor(.green)
                        .font(.title3)

                    VStack(alignment: .leading, spacing: 2) {
                        Text("SMS Confirmation Sent")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundColor(.primary)
                        Text("Directions and token \(bookingID) sent to your mobile.")
                            .font(.system(size: 11))
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                }
                .padding(14)
                .background(Color.green.opacity(0.1))
                .cornerRadius(14)

                // Action Buttons
                VStack(spacing: 12) {
                    PrimaryButton(title: "Done • Back to Dashboard") {
                        router.goToDashboard()
                        dismiss()
                    }

                    Button {
                        isCopied = true
                        UIPasteboard.general.string = "Appointment with \(doctor.doctorName) at \(doctor.name) on \(appointmentDate) at \(appointmentTime). Ref: \(bookingID)"
                    } label: {
                        Text(isCopied ? "✓ Details Copied to Clipboard" : "📋 Copy Appointment Details")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(Color(hex: "#FF2D6F"))
                    }
                }

                Spacer().frame(height: 20)
            }
            .padding(.horizontal, 20)
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle("Appointment Confirmed")
        .navigationBarTitleDisplayMode(.inline)
        .navigationBarBackButtonHidden(true)
    }
}
