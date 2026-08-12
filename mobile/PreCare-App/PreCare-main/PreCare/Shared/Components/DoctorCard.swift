//
//  DoctorCard.swift
//  PreCare
//

import SwiftUI
import UIKit

struct DoctorCard: View {
    let doctor: Doctor
    let isSelected: Bool
    var onSelect: (() -> Void)? = nil

    private var initials: String {
        let clean = doctor.doctorName.replacingOccurrences(of: "Dr.", with: "").trimmingCharacters(in: .whitespaces)
        let parts = clean.split(separator: " ")
        if parts.count >= 2 {
            return "\(parts[0].prefix(1))\(parts[1].prefix(1))".uppercased()
        }
        return String(clean.prefix(2)).uppercased()
    }

    private func openDirections() {
        if let mapsUrl = doctor.mapsUrl, let url = URL(string: mapsUrl) {
            UIApplication.shared.open(url)
        } else {
            let encoded = doctor.address.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
            if let url = URL(string: "https://www.google.com/maps/dir/?api=1&destination=\(encoded)&travelmode=driving") {
                UIApplication.shared.open(url)
            }
        }
    }

    private func callHospital() {
        let cleanPhone = doctor.phone.filter { "0123456789+".contains($0) }
        if let url = URL(string: "tel://\(cleanPhone)") {
            UIApplication.shared.open(url)
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            // Top Badge Row
            HStack {
                if isSelected {
                    HStack(spacing: 4) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 11))
                        Text("Selected Hospital")
                            .font(.system(size: 11, weight: .bold))
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(Color.orange)
                    .clipShape(Capsule())
                } else if doctor.aiRecommended {
                    HStack(spacing: 4) {
                        Image(systemName: "sparkles")
                            .font(.system(size: 10))
                        Text(doctor.isClosest ? "Nearest Hospital" : "AI Recommended")
                            .font(.system(size: 11, weight: .bold))
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(Color(hex: "#FF2D6F"))
                    .clipShape(Capsule())
                }

                Spacer()

                if let dist = doctor.distanceKm {
                    HStack(spacing: 4) {
                        Image(systemName: "location.fill")
                            .font(.system(size: 10))
                        Text(dist < 1.0 ? String(format: "%.1f km away", dist) : String(format: "%.1f km", dist))
                            .font(.system(size: 11, weight: .bold))
                    }
                    .foregroundColor(Color.blue)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(8)
                }
            }

            // Hospital & Doctor Title Info
            HStack(alignment: .top, spacing: 12) {
                // Initials Avatar
                Text(initials)
                    .font(.system(size: 15, weight: .bold))
                    .foregroundColor(Color(hex: "#FF2D6F"))
                    .frame(width: 44, height: 44)
                    .background(Color(hex: "#FF2D6F").opacity(0.12))
                    .clipShape(RoundedRectangle(cornerRadius: 12))

                VStack(alignment: .leading, spacing: 3) {
                    Text(doctor.name)
                        .font(.system(size: 15, weight: .bold))
                        .foregroundColor(.primary)
                        .lineLimit(2)

                    Text("\(doctor.doctorName) • \(doctor.specialization)")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.secondary)

                    // Ratings & Reviews
                    HStack(spacing: 4) {
                        HStack(spacing: 2) {
                            ForEach(1...5, id: \.self) { star in
                                Image(systemName: Double(star) <= doctor.rating ? "star.fill" : "star")
                                    .font(.system(size: 10))
                                    .foregroundColor(.yellow)
                            }
                        }
                        Text(String(format: "%.1f", doctor.rating))
                            .font(.system(size: 11, weight: .bold))
                        Text("(\(doctor.userRatingsTotal))")
                            .font(.system(size: 10))
                            .foregroundColor(.gray)

                        Text("• \(doctor.availability)")
                            .font(.system(size: 11, weight: .medium))
                            .foregroundColor(.green)
                    }
                    .padding(.top, 1)
                }
            }

            // AI Recommendation Reason Banner
            if doctor.aiRecommended, let reason = doctor.aiReason {
                HStack(alignment: .top, spacing: 6) {
                    Image(systemName: "bolt.fill")
                        .font(.system(size: 11))
                        .foregroundColor(Color(hex: "#FF2D6F"))
                    Text(reason)
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(Color(hex: "#FF2D6F"))
                }
                .padding(8)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color(hex: "#FF2D6F").opacity(0.08))
                .cornerRadius(10)
            }

            // Address Row
            HStack(alignment: .top, spacing: 6) {
                Image(systemName: "mappin.and.ellipse")
                    .font(.system(size: 12))
                    .foregroundColor(.secondary)
                Text(doctor.address)
                    .font(.system(size: 11))
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }

            Divider()

            // Action Buttons Row: Get Directions + Call + Book
            HStack(spacing: 8) {
                // Get Directions (Opens Google Maps driving navigation)
                Button {
                    openDirections()
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: "arrow.triangle.turn.up.right.diamond.fill")
                            .font(.system(size: 11))
                        Text("Directions")
                            .font(.system(size: 12, weight: .bold))
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity, minHeight: 36)
                    .background(Color.blue)
                    .cornerRadius(10)
                }

                // Call Button
                Button {
                    callHospital()
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: "phone.fill")
                            .font(.system(size: 11))
                        Text("Call")
                            .font(.system(size: 12, weight: .bold))
                    }
                    .foregroundColor(.green)
                    .padding(.horizontal, 12)
                    .frame(minHeight: 36)
                    .background(Color.green.opacity(0.12))
                    .cornerRadius(10)
                }

                // Selection / Book indicator
                Button {
                    onSelect?()
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: isSelected ? "checkmark" : "calendar.badge.plus")
                            .font(.system(size: 11))
                        Text(isSelected ? "Selected" : "Select")
                            .font(.system(size: 12, weight: .bold))
                    }
                    .foregroundColor(isSelected ? .white : Color(hex: "#FF2D6F"))
                    .padding(.horizontal, 14)
                    .frame(minHeight: 36)
                    .background(isSelected ? Color.orange : Color(hex: "#FF2D6F").opacity(0.12))
                    .cornerRadius(10)
                }
            }
        }
        .padding(16)
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(18)
        .overlay(
            RoundedRectangle(cornerRadius: 18)
                .stroke(
                    isSelected ? Color.orange :
                    doctor.aiRecommended ? Color(hex: "#FF2D6F").opacity(0.4) :
                    Color.gray.opacity(0.2),
                    lineWidth: isSelected ? 2 : 1
                )
        )
        .shadow(color: Color.black.opacity(0.04), radius: 6, x: 0, y: 2)
    }
}

